import sys
import time
from typing import Dict, NoReturn, Optional, Union

import pymumble_py3 as pymumble
from pymumble_py3.errors import ConnectionRejectedError

from .constants import SYS_CERT, SYS_DEBUG, SYS_HOST, SYS_KEY, SYS_PASS, SYS_PORT, SYS_RECONNECT, SYS_TOKENS, SYS_USER
from .utils.args_validators import SystemArgumentsValidator


class MurmurConnection:
    _instance: Optional[pymumble.Mumble] = None
    _connection_params: Optional[Dict[str, Union[str, bool]]] = None
    _is_connected: bool = False

    def __init__(self, connection_params: Optional[Dict[str, Union[str, bool]]] = None) -> None:
        self._setup(connection_params)

    @property
    def instance(self):
        return self._instance

    def _setup(self, connection_params: Optional[Dict[str, Union[str, bool]]]) -> None:
        if connection_params is None:
            # TODO: Add non-blocking warning here if connection params is not provided in initialization
            return
        self._validate_connection_params(connection_params)
        self._connection_params = connection_params

    def connect(self, connection_params: Optional[Dict[str, Union[str, bool]]] = None) -> NoReturn:
        if self._instance is not None:
            raise Exception("Unable to connect: a murmur connection instance is already connected.")
        if connection_params is not None:
            self._connection_params = connection_params
        self._connect_instance()
        self._loop()

    def _connect_instance(self) -> None:
        if self._connection_params is None:
            raise Exception("Unable to connect: connection parameters are undefined.")

        self._instance = pymumble.Mumble(
            host=self._connection_params.get(SYS_HOST),
            port=int(self._connection_params.get(SYS_PORT, 64738)),
            user=self._connection_params.get(SYS_USER),
            password=self._connection_params.get(SYS_PASS),
            certfile=self._connection_params.get(SYS_CERT),
            keyfile=self._connection_params.get(SYS_KEY),
            tokens=self._connection_params.get(SYS_TOKENS),
            reconnect=self._connection_params.get(SYS_RECONNECT, False),
            debug=self._connection_params.get(SYS_DEBUG, False),
            stereo=True,
        )
        self._instance.set_codec_profile("audio")
        self._instance.set_receive_sound(True)

        try:
            self._instance.start()
            self._instance.is_ready()
            self._is_connected = True
            # self.mumble_inst.users.myself.register() - don't implement yet
            # self._instance.users.myself.comment(f"Mumimo - v0.0.1") - don't implement yet
            # self._instance.users.myself.mute() - don't implement yet
        except ConnectionRejectedError as err:
            raise err

    def _loop(self):
        try:
            while True:
                time.sleep(0.3)
        except KeyboardInterrupt:
            print("\nExiting Mumimo service.")
            if self._instance is not None:
                self._instance.stop()
                self._instance = None
                self._is_connected = False
            sys.exit(0)

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
