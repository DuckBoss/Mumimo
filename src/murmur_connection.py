import logging
import threading
import time
from typing import Dict, Optional, Union

import pymumble_py3 as pymumble
from pymumble_py3.constants import PYMUMBLE_CLBK_TEXTMESSAGERECEIVED
from pymumble_py3.errors import ConnectionRejectedError

from .client_state import ClientState
from .constants import VERBOSE_MAX, SysArgs
from .exceptions import ConnectivityError, ServiceError
from .lib.singleton import singleton
from .settings import settings
from .utils.args_validators import SystemArgumentsValidator

logger = logging.getLogger(__name__)


@singleton
class MurmurConnection:
    _thread: Optional[threading.Thread] = None
    _thread_stop_event: threading.Event = threading.Event()

    _connection_instance: Optional[pymumble.Mumble] = None
    _connection_params: Optional[Dict[str, Union[str, bool]]] = None
    _is_connected: bool = False

    @property
    def connection_instance(self) -> Optional[pymumble.Mumble]:
        return self._connection_instance

    @property
    def is_connected(self) -> bool:
        return self._is_connected

    def setup(self, connection_params: Dict[str, Union[str, bool]]):
        if not connection_params:
            logger.warning("Connection parameters have not been provided during Murmur initialization.")
            return
        self._validate_sys_args(connection_params)
        self._connection_params = connection_params
        logger.debug("Validated murmur connection parameters.")

    def ready(self) -> "MurmurConnection":
        if self.is_connected:
            raise ConnectivityError(
                "Unable to connect: a murmur connection instance is already connected. Please stop the active connection before creating a new one.",
                logger=logger,
            )
        if self._connection_params is None:
            raise ConnectivityError("Unable to connect: connection parameters have not been specified.", logger=logger)
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
        self._connection_instance.set_receive_sound(True)
        logger.debug("Murmur connection instance defined.")
        return self

    def connect(self) -> "MurmurConnection":
        if self.is_connected:
            raise ConnectivityError(
                "Unable to connect: a murmur connection instance is already connected. Please stop the active connection before creating a new one.",
                logger=logger,
            )
        if self._connection_instance is None:
            raise ConnectivityError("Unable to connect: the murmur connection instance is not initialized.", logger=logger)
        self._connect_instance()
        logger.debug("Murmur connection instance established.")
        self._post_connection_actions()
        logger.debug("Murmur post-connection actions completed.")
        return self

    def start(self) -> bool:
        if self._is_connected and self._connection_instance:
            if self._thread is None:
                self._thread = threading.Thread(name="murmur-conn", target=self._loop, args=(self._thread_stop_event,))
            else:
                self._thread_stop_event.set()
                self._thread.join()
                self._thread = threading.Thread(name="murmur-conn", target=self._loop, args=(self._thread_stop_event,))
            logger.debug(f"Connectivity thread: [{self._thread.name}] initialized.")
            self._thread.start()
            logger.debug(f"Connectivity thread: [{self._thread.name} | {self._thread.ident}] started.")
            return True
        return False

    def stop(self) -> bool:
        if self._connection_instance is not None:
            if self._thread is not None:
                logger.debug(f"Connectivity thread: [{self._thread.name} | {self._thread.ident}] closing...")
                self._thread_stop_event.set()
                self._thread.join()
                logger.debug(f"Connectivity thread: [{self._thread.name}] closed.")
            try:
                self._connection_instance.stop()
            except AttributeError:
                logger.debug("Connection instance closed prematurely.")
            self._is_connected = False
            self._connection_instance = None
            self._thread = None
            return True
        return False

    def _connect_instance(self) -> None:
        if self._connection_instance is None:
            raise ConnectivityError("Unable to connect: the murmur connection instance is not initialized.", logger=logger)
        try:
            self._connection_instance.start()
            self._connection_instance.is_ready()
            self._is_connected = True

            # self._connection_instance.users.myself.register() - don't implement yet
            # self._connection_instance.users.myself.comment(f"Mumimo - v0.0.1") - don't implement yet
        except ConnectionRejectedError as err:
            raise ConnectivityError(str(err), logger) from err

    def _post_connection_actions(self) -> None:
        if self._connection_instance is None:
            raise ServiceError("Unable to conduct post connection actions: there is no active murmur connection.", logger=logger)

        _client_state: Optional[ClientState] = settings.get_client_state()
        if _client_state is None:
            settings.set_client_state(ClientState(self._connection_instance))
            _client_state = settings.get_client_state()
        if _client_state is not None:
            self._connection_instance.callbacks.set_callback(PYMUMBLE_CLBK_TEXTMESSAGERECEIVED, _client_state.cmd_service.process_cmd)
            logger.debug(f"Added murmur callback: {PYMUMBLE_CLBK_TEXTMESSAGERECEIVED}-{_client_state.cmd_service.process_cmd.__name__}")

    def _loop(self, stop_event: threading.Event) -> None:
        while True:
            if stop_event.is_set():
                break
            time.sleep(0.1)

    def _validate_sys_args(self, params: Dict[str, Union[str, bool]]) -> None:
        SystemArgumentsValidator.validate_host_param(params.get(SysArgs.SYS_HOST))  # type: ignore
        SystemArgumentsValidator.validate_port_param(params.get(SysArgs.SYS_PORT))  # type: ignore
        SystemArgumentsValidator.validate_user_param(params.get(SysArgs.SYS_USER))  # type: ignore
        SystemArgumentsValidator.validate_password_param(params.get(SysArgs.SYS_PASS))  # type: ignore
        SystemArgumentsValidator.validate_cert_param(params.get(SysArgs.SYS_CERT))  # type: ignore
        SystemArgumentsValidator.validate_key_param(params.get(SysArgs.SYS_KEY))  # type: ignore
        SystemArgumentsValidator.validate_tokens_param(params.get(SysArgs.SYS_TOKENS))  # type: ignore
        SystemArgumentsValidator.validate_auto_reconnect_param(params.get(SysArgs.SYS_RECONNECT))  # type: ignore
        SystemArgumentsValidator.validate_verbose_param(params.get(SysArgs.SYS_VERBOSE))  # type: ignore
