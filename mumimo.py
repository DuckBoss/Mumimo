#!/usr/bin/env python3

import sys
import time
from typing import Dict, NoReturn, Optional

from src.murmur_connection import MurmurConnection, MurmurConnectionSingleton
from src.system_arguments import args_parser
from src.utils import mumimo_utils


class MumimoService:
    _murmur_connection_instance: Optional[MurmurConnection]

    def __init__(self, sys_args: Dict[str, str]) -> None:
        self._setup(sys_args)

    def _setup(self, sys_args: Dict[str, str]) -> None:
        _connection_params = mumimo_utils.initialize_client_settings(sys_args)
        self.initialize_connection(_connection_params)

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
    system_args: Dict[str, str] = vars(args_parser.parse_args())
    if not mumimo_utils.is_supported_platform():
        print("WARNING: Mumimo is only supported for Linux and MacOS systems.\nYou may run into unexpected issues on Windows and other systems.")
    mumimo = MumimoService(system_args)
