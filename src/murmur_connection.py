import threading
import time
from typing import Dict, Optional, Union

import pymumble_py3 as pymumble
from pymumble_py3.errors import ConnectionRejectedError

from .client_state import ClientState
from .constants import SYS_CERT, SYS_DEBUG, SYS_HOST, SYS_KEY, SYS_PASS, SYS_PORT, SYS_RECONNECT, SYS_TOKENS, SYS_USER
from .utils.args_validators import SystemArgumentsValidator


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
        if cls._murmur_connection_instance is not None:
            del cls._murmur_connection_instance


class MurmurConnection:
    _thread: Optional[threading.Thread] = None
    _thread_stop_event: threading.Event = threading.Event()

    _connection_instance: Optional[pymumble.Mumble] = None
    _connection_params: Optional[Dict[str, Union[str, bool]]] = None
    _is_connected: bool = False

    _client_state: Optional[ClientState] = None

    def __init__(self, connection_params: Optional[Dict[str, Union[str, bool]]] = None) -> None:
        if self._connection_instance is None:
            self._setup(connection_params)
            print("Setup murmur connection.")

    @property
    def connection_instance(self) -> Optional[pymumble.Mumble]:
        return self._connection_instance

    @property
    def is_connected(self) -> bool:
        return self._is_connected

    def _setup(self, connection_params: Optional[Dict[str, Union[str, bool]]] = None) -> None:
        if connection_params is None:
            # TODO: Add non-blocking warning here if connection params is not provided in initialization
            return
        self._validate_connection_params(connection_params)
        self._connection_params = connection_params

    def connect(self, connection_params: Optional[Dict[str, Union[str, bool]]] = None) -> None:
        if self._connection_instance is not None:
            raise Exception("Unable to connect: a murmur connection instance is already connected.")
        if connection_params is not None:
            self._connection_params = connection_params
        self._connect_instance()

    def start(self) -> bool:
        if self._is_connected:
            if self._thread is None:
                self._thread = threading.Thread(target=self._loop, args=(self._thread_stop_event,))
            else:
                self._thread_stop_event.set()
                self._thread.join()
                self._thread = threading.Thread(target=self._loop, args=(self._thread_stop_event,))
            self._thread.start()
            return True
        return False

    def stop(self) -> bool:
        if self._connection_instance is not None:
            if self._thread is not None:
                self._thread_stop_event.set()
                self._thread.join()
            self._connection_instance.stop()
            self._is_connected = False
            self._connection_instance = None
            self._thread = None
            return True
        return False

    def _connect_instance(self) -> None:
        if self._connection_params is None:
            raise Exception("Unable to connect: connection parameters are undefined.")

        self._connection_instance = pymumble.Mumble(
            host=self._connection_params.get(SYS_HOST),
            port=int(self._connection_params.get(SYS_PORT, 64738)),
            user=self._connection_params.get(SYS_USER),
            password=str(self._connection_params.get(SYS_PASS)),
            certfile=self._connection_params.get(SYS_CERT),
            keyfile=self._connection_params.get(SYS_KEY),
            tokens=self._connection_params.get(SYS_TOKENS),
            reconnect=bool(self._connection_params.get(SYS_RECONNECT, False)),
            debug=bool(self._connection_params.get(SYS_DEBUG, False)),
            stereo=True,
        )
        self._connection_instance.set_codec_profile("audio")
        self._connection_instance.set_receive_sound(True)

        try:
            self._connection_instance.start()
            self._connection_instance.is_ready()
            self._is_connected = True
            if self._client_state is None:
                self._client_state = ClientState(self._connection_instance)
            # self._connection_instance.users.myself.register() - don't implement yet
            # self._connection_instance.users.myself.comment(f"Mumimo - v0.0.1") - don't implement yet
        except ConnectionRejectedError as err:
            raise err

    def _loop(self, stop_event: threading.Event) -> None:
        while True:
            if stop_event.is_set():
                break
            time.sleep(0.1)

    def _validate_connection_params(self, params: Dict[str, Union[str, bool]]) -> None:
        SystemArgumentsValidator.validate_host_param(params.get(SYS_HOST))
        SystemArgumentsValidator.validate_port_param(params.get(SYS_PORT))
        SystemArgumentsValidator.validate_user_param(params.get(SYS_USER))
        SystemArgumentsValidator.validate_password_param(params.get(SYS_PASS))
        SystemArgumentsValidator.validate_cert_param(params.get(SYS_CERT))
        SystemArgumentsValidator.validate_key_param(params.get(SYS_KEY))
        SystemArgumentsValidator.validate_tokens_param(params.get(SYS_TOKENS))
        SystemArgumentsValidator.validate_reconnect_param(params.get(SYS_RECONNECT))
        SystemArgumentsValidator.validate_debug_param(params.get(SYS_DEBUG))
