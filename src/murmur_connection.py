import threading
import time
from typing import Dict, Optional, Union

import pymumble_py3 as pymumble
from pymumble_py3.constants import PYMUMBLE_CLBK_TEXTMESSAGERECEIVED
from pymumble_py3.errors import ConnectionRejectedError

from .client_state import ClientState
from .constants import VERBOSE_MAX, SysArgs
from .settings import settings
from .exceptions import ConnectivityError, ValidationError, ServiceError
from .logging import debug as _debug
from .logging import get_logger
from .logging import print as _print
from .logging import print_warn as _print_warn
from .utils.args_validators import SystemArgumentsValidator

logger = get_logger(__name__)
print = _print(logger=logger)
print_warn = _print_warn(logger=logger)
debug = _debug(logger=logger)


class MurmurConnectionSingleton:
    _murmur_connection_instance: Optional["MurmurConnection"] = None

    def __new__(cls, *args, **kwargs) -> "MurmurConnectionSingleton":
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
            cls._instance._murmur_connection_instance = MurmurConnection(*args, **kwargs)
        return cls._instance

    @classmethod
    def instance(cls) -> Optional["MurmurConnection"]:
        if cls._instance is not None:
            return cls._instance._murmur_connection_instance
        return None

    @classmethod
    def clear(cls) -> None:
        if cls._instance is not None:
            del cls._instance


class MurmurConnection:
    _thread: Optional[threading.Thread] = None
    _thread_stop_event: threading.Event = threading.Event()

    _connection_instance: Optional[pymumble.Mumble] = None
    _connection_params: Optional[Dict[str, Union[str, bool]]] = None
    _is_connected: bool = False

    def __init__(self, connection_params: Optional[Dict[str, Union[str, bool]]] = None) -> None:
        if self._connection_instance is None:
            self._setup(connection_params)

    @property
    def connection_instance(self) -> Optional[pymumble.Mumble]:
        return self._connection_instance

    @property
    def is_connected(self) -> bool:
        return self._is_connected

    def _setup(self, connection_params: Optional[Dict[str, Union[str, bool]]] = None) -> None:
        if connection_params is None:
            print_warn("Connection parameters have not been provided during Murmur initialization.")
            return
        self._validate_connection_params(connection_params)
        self._connection_params = connection_params
        print("Validated murmur connection parameters.")

    def connect(self, connection_params: Optional[Dict[str, Union[str, bool]]] = None) -> None:
        if self._connection_instance is not None:
            raise ConnectivityError("Unable to connect: a murmur connection instance is already connected.", logger=logger)
        if connection_params is not None:
            self._connection_params = connection_params
        self._connect_instance()

    def start(self) -> bool:
        if self._is_connected:
            if self._thread is None:
                self._thread = threading.Thread(name="murmur-conn", target=self._loop, args=(self._thread_stop_event,))
            else:
                self._thread_stop_event.set()
                self._thread.join()
                self._thread = threading.Thread(name="murmur-conn", target=self._loop, args=(self._thread_stop_event,))
            debug(f"Connectivity thread: [{self._thread.name}] initialized.")
            self._thread.start()
            debug(f"Connectivity thread: [{self._thread.name} | {self._thread.ident}] started.")
            return True
        return False

    def stop(self) -> bool:
        if self._connection_instance is not None:
            if self._thread is not None:
                debug(f"Connectivity thread: [{self._thread.name} | {self._thread.ident}] closing...")
                self._thread_stop_event.set()
                self._thread.join()
                debug(f"Connectivity thread: [{self._thread.name}] closed.")
            self._connection_instance.stop()
            self._is_connected = False
            self._connection_instance = None
            self._thread = None
            return True
        return False

    def _connect_instance(self) -> None:
        if self._connection_params is None:
            raise ValidationError("Unable to connect: connection parameters are undefined.", logger=logger)

        self._connection_instance = pymumble.Mumble(
            host=self._connection_params.get(SysArgs.SYS_HOST),
            port=int(self._connection_params.get(SysArgs.SYS_PORT, 64738)),
            user=self._connection_params.get(SysArgs.SYS_USER),
            password=str(self._connection_params.get(SysArgs.SYS_PASS)),
            certfile=self._connection_params.get(SysArgs.SYS_CERT),
            keyfile=self._connection_params.get(SysArgs.SYS_KEY),
            tokens=self._connection_params.get(SysArgs.SYS_TOKENS),
            reconnect=bool(self._connection_params.get(SysArgs.SYS_RECONNECT, False)),
            debug=bool(int(self._connection_params.get(SysArgs.SYS_VERBOSE, False)) >= VERBOSE_MAX),
            stereo=True,
        )
        self._connection_instance.set_codec_profile("audio")
        self._connection_instance.set_receive_sound(False)  # Only set to False if testing on Windows

        # Set up callbacks
        self._set_up_callbacks()

        try:
            self._connection_instance.start()
            self._connection_instance.is_ready()
            self._is_connected = True

            # self._connection_instance.users.myself.register() - don't implement yet
            # self._connection_instance.users.myself.comment(f"Mumimo - v0.0.1") - don't implement yet
        except ConnectionRejectedError as err:
            raise ConnectivityError(str(err), logger) from err

    def _set_up_callbacks(self) -> None:
        if self._connection_instance is None:
            raise ServiceError("Unable to set up mumble callbacks: the connection instance is not initialized.", logger=logger)

        _client_state: Optional[ClientState] = settings.get_client_state()
        if _client_state is None:
            settings.set_client_state(ClientState(self._connection_instance))
        if _client_state is not None:
            self._connection_instance.callbacks.set_callback(PYMUMBLE_CLBK_TEXTMESSAGERECEIVED, _client_state.cmd_service.process_cmd)

    def _loop(self, stop_event: threading.Event) -> None:
        while True:
            if stop_event.is_set():
                break
            time.sleep(0.1)

    def _validate_connection_params(self, params: Dict[str, Union[str, bool]]) -> None:
        SystemArgumentsValidator.validate_host_param(params.get(SysArgs.SYS_HOST))
        SystemArgumentsValidator.validate_port_param(params.get(SysArgs.SYS_PORT))
        SystemArgumentsValidator.validate_user_param(params.get(SysArgs.SYS_USER))
        SystemArgumentsValidator.validate_password_param(params.get(SysArgs.SYS_PASS))
        SystemArgumentsValidator.validate_cert_param(params.get(SysArgs.SYS_CERT))
        SystemArgumentsValidator.validate_key_param(params.get(SysArgs.SYS_KEY))
        SystemArgumentsValidator.validate_tokens_param(params.get(SysArgs.SYS_TOKENS))
        SystemArgumentsValidator.validate_auto_reconnect_param(params.get(SysArgs.SYS_RECONNECT))
        SystemArgumentsValidator.validate_verbose_param(params.get(SysArgs.SYS_VERBOSE))
