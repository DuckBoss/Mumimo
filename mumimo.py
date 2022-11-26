#!/usr/bin/env python3

import sys
import time
from typing import Dict, NoReturn, Optional, Union

from src.constants import (
    ENV_CERT,
    ENV_HOST,
    ENV_KEY,
    ENV_PASS,
    ENV_PORT,
    ENV_TOKENS,
    ENV_USER,
    SYS_CERT,
    SYS_DEBUG,
    SYS_ENV_FILE,
    SYS_HOST,
    SYS_KEY,
    SYS_PASS,
    SYS_PORT,
    SYS_RECONNECT,
    SYS_TOKENS,
    SYS_USER,
)
from src.murmur_connection import MurmurConnection, MurmurConnectionSingleton
from src.system_arguments import args_parser
from src.utils import env_parser, mumimo_utils


class MumimoService:
    _murmur_connection_instance: Optional[MurmurConnection]
    _connection_params: Dict[str, Union[Optional[str], Optional[bool]]]

    def __init__(self, sys_args: Dict[str, str]) -> None:
        print(sys_args)
        self.interpret_sys_args(sys_args)
        self.initialize_connection(self._connection_params)

    def interpret_sys_args(self, sys_args: Dict[str, str]) -> None:
        # Load in options from .env file if present.
        available_env_file: Optional[str] = sys_args.get(SYS_ENV_FILE)
        env_file_dict: Dict[str, Optional[str]] = {}
        if available_env_file is not None:
            env_file_dict = env_parser.read_env_file(available_env_file)
            print(env_file_dict.items())

        # Load in remaining options from system arguments, and prioritize system args
        self._connection_params = {
            SYS_HOST: sys_args.get(SYS_HOST) or env_file_dict.get(ENV_HOST),
            SYS_PORT: sys_args.get(SYS_PORT) or env_file_dict.get(ENV_PORT),
            SYS_USER: sys_args.get(SYS_USER) or env_file_dict.get(ENV_USER),
            SYS_PASS: sys_args.get(SYS_PASS) or env_file_dict.get(ENV_PASS),
            SYS_CERT: sys_args.get(SYS_CERT) or env_file_dict.get(ENV_CERT),
            SYS_KEY: sys_args.get(SYS_KEY) or env_file_dict.get(ENV_KEY),
            SYS_TOKENS: sys_args.get(SYS_TOKENS) or env_file_dict.get(ENV_TOKENS),
            SYS_RECONNECT: bool(sys_args.get(SYS_RECONNECT, False)),
            SYS_DEBUG: bool(sys_args.get(SYS_DEBUG, False)),
        }

    def initialize_connection(self, connection_params) -> None:
        connection_singleton = MurmurConnectionSingleton(connection_params)
        self._murmur_connection_instance = connection_singleton.instance()
        if self._murmur_connection_instance is not None:
            self._murmur_connection_instance.connect()
            if self._murmur_connection_instance.is_connected:
                if self._murmur_connection_instance._client_state is not None:
                    self._murmur_connection_instance._client_state.audio_properties.mute()
            self._murmur_connection_instance.start()
            self._wait_for_interrupt()

    def _wait_for_interrupt(self) -> NoReturn:
        try:
            while True:
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\nExiting Mumimo service.")
            if self._murmur_connection_instance is not None:
                self._murmur_connection_instance.stop()
            sys.exit(0)


if __name__ == "__main__":
    if not mumimo_utils.is_supported_platform():
        print("WARNING: Mumimo is only supported for Linux and MacOS systems.\nYou may run into unexpected issues on Windows and other systems.")
    system_args: Dict[str, str] = vars(args_parser.parse_args())
    mumimo = MumimoService(system_args)
