import logging
import threading
import time
from typing import Dict, Optional, Union, List


import pymumble_py3 as pymumble
from pymumble_py3.users import User
from pymumble_py3.constants import (
    PYMUMBLE_CLBK_TEXTMESSAGERECEIVED,
    PYMUMBLE_CLBK_CONNECTED,
    PYMUMBLE_CLBK_USERCREATED,
    PYMUMBLE_CLBK_USERREMOVED,
    PYMUMBLE_CLBK_DISCONNECTED,
    PYMUMBLE_CLBK_CHANNELCREATED,
    PYMUMBLE_CLBK_CHANNELREMOVED,
)
from pymumble_py3.errors import ConnectionRejectedError

from .client_state import ClientState
from .services.cmd_processing_service import CommandProcessingService
from .constants import VERBOSE_MAX, SysArgs, MumimoCfgFields
from .exceptions import ConnectivityError, ServiceError
from .lib.singleton import singleton
from .settings import settings
from .utils.args_validators import SystemArgumentsValidator
from .utils import mumble_utils
from .version import version

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
            client_type=1,
        )
        self._connection_instance.set_codec_profile("audio")
        self._connection_instance.set_receive_sound(True)
        self._connection_instance.set_loop_rate(0.05)

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
        except ConnectionRejectedError as err:
            raise ConnectivityError(str(err), logger) from err

    def _post_connection_actions(self) -> None:
        if self._connection_instance is None:
            raise ServiceError("Unable to conduct post connection actions: there is no active murmur connection.", logger=logger)

        # Save the client state to the settings and set callbacks.
        _client_state: Optional[ClientState] = settings.state.get_client_state()
        if _client_state is None:
            _client_state = ClientState(self._connection_instance)
            settings.state.set_client_state(_client_state)
        # Set on_server_connect callback in client state.
        self._connection_instance.callbacks.set_callback(PYMUMBLE_CLBK_CONNECTED, _client_state.server_properties.on_server_connect)
        logger.debug(f"Added murmur callback: {PYMUMBLE_CLBK_CONNECTED}-{_client_state.server_properties.on_server_connect.__name__}")
        # Set on_server_disconnect callback in client state.
        self._connection_instance.callbacks.set_callback(PYMUMBLE_CLBK_DISCONNECTED, _client_state.server_properties.on_server_disconnect)
        logger.debug(f"Added murmur callback: {PYMUMBLE_CLBK_DISCONNECTED}-{_client_state.server_properties.on_server_disconnect.__name__}")
        # Set on_user_created callback in client state.
        self._connection_instance.callbacks.set_callback(PYMUMBLE_CLBK_USERCREATED, _client_state.server_properties.on_user_created)
        logger.debug(f"Added murmur callback: {PYMUMBLE_CLBK_USERCREATED}-{_client_state.server_properties.on_user_created.__name__}")
        # Set on_user_removed callback in client state.
        self._connection_instance.callbacks.set_callback(PYMUMBLE_CLBK_USERREMOVED, _client_state.server_properties.on_user_removed)
        logger.debug(f"Added murmur callback: {PYMUMBLE_CLBK_USERREMOVED}-{_client_state.server_properties.on_user_removed.__name__}")
        # Set on_channel_created callback in client state.
        self._connection_instance.callbacks.set_callback(PYMUMBLE_CLBK_CHANNELCREATED, _client_state.server_properties.on_channel_created)
        logger.debug(f"Added murmur callback: {PYMUMBLE_CLBK_CHANNELCREATED}-{_client_state.server_properties.on_channel_created.__name__}")
        # Set on_channel_removed callback in client state.
        self._connection_instance.callbacks.set_callback(PYMUMBLE_CLBK_CHANNELREMOVED, _client_state.server_properties.on_channel_removed)
        logger.debug(f"Added murmur callback: {PYMUMBLE_CLBK_CHANNELREMOVED}-{_client_state.server_properties.on_channel_removed.__name__}")

        # Save the command processing service to the settings and set command processing mumble callbacks.
        _cmd_service: Optional[CommandProcessingService] = settings.commands.services.get_cmd_processing_service()
        if _cmd_service is None:
            _cmd_service = CommandProcessingService(self._connection_instance)
            settings.commands.services.set_cmd_processing_service(_cmd_service)
        self._connection_instance.callbacks.set_callback(PYMUMBLE_CLBK_TEXTMESSAGERECEIVED, _cmd_service.process_cmd)
        logger.debug(f"Added murmur callback: {PYMUMBLE_CLBK_TEXTMESSAGERECEIVED}-{_cmd_service.process_cmd.__name__}")

        # Listen to all channels when connecting to the server.
        _user: Optional["User"] = self._connection_instance.users.myself
        if _user:
            # Set bot client comment
            _user.comment(f"Mumimo - v{version()}")
            # Mute the bot on server join
            _client_state.audio_properties.mute()
            # _user.myself.register() - don't implement yet
            _channels = []
            for _, channel in enumerate(self._connection_instance.channels.items()):
                _channels.append(channel[1]["channel_id"])
                logger.debug(f"Added listening channel: '{channel[1]['name']}-{channel[1]['channel_id']}'")
            _user.add_listening_channels(_channels)

    async def _async_post_connection_actions(self) -> None:
        logger.debug("Running asynchronous post connection actions.")

        # Detect all active users and add the users to the database with permissions if they don't exist:
        _database_service = settings.database.get_database_instance()
        if not _database_service:
            raise ServiceError("Failed async post connection actions: database instance not found.", logger=logger)
        _inst = self._connection_instance
        if not _inst:
            raise ServiceError("Failed async post connection actions: mumble instance not found.", logger=logger)
        _cfg = settings.configs.get_mumimo_config()
        if not _cfg:
            raise ServiceError("Failed async post connection actions: mumimo config not found.", logger=logger)
        _bot_name = _cfg.get(MumimoCfgFields.SETTINGS.CONNECTION.NAME, None)
        if not _bot_name:
            raise ServiceError("Failed async post connection actions: mumimo bot name not found in config.", logger=logger)

        _all_users: List["User"] = [user for id, user in _inst.users.items() if user["name"] != _bot_name]
        for _user in _all_users:
            await mumble_utils.Management.User.add_user(_user)

        logger.debug("Asynchronous post connection actions complete.")

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
