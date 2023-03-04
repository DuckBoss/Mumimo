import time
from typing import Dict, Optional


from .logging import get_logger
from .logging import print as _print
from .logging import print_warn as _print_warn
from .logging import print_err as _print_err
from .murmur_connection import MurmurConnection, MurmurConnectionSingleton
from .utils import mumimo_utils
from .services.init_service import MumimoInitService

logger = get_logger(__name__)
print = _print(logger=logger)
print_warn = _print_warn(logger=logger)
print_err = _print_err(logger=logger)


class MumimoService:
    _murmur_connection_instance: Optional[MurmurConnection]

    def __init__(self, sys_args: Dict[str, str]) -> None:
        self._setup(sys_args)

    def _setup(self, sys_args: Dict[str, str]) -> None:
        if not mumimo_utils.is_supported_platform():
            print_warn("Mumimo is only supported for Linux and MacOS systems. You may run into unexpected issues on Windows and other systems.")
        print("Initializing Mumimo client...")
        _init_service = MumimoInitService(sys_args)
        _config = _init_service.initialize_config()
        _connection_params = _init_service.initialize_client_settings(_config)
        print("Mumimo client state configured.")
        self.initialize_connection(_connection_params)

    def initialize_connection(self, connection_params) -> None:
        print("Establishing Murmur connectivity...")
        connection_singleton = MurmurConnectionSingleton(connection_params)
        self._murmur_connection_instance = connection_singleton.instance()
        if self._murmur_connection_instance is not None:
            self._murmur_connection_instance.connect()
            if self._murmur_connection_instance.is_connected:
                if self._murmur_connection_instance._client_state is not None:
                    self._murmur_connection_instance._client_state.audio_properties.mute()
            if self._murmur_connection_instance.start():
                print("Established Murmur connectivity.")
                print("Mumimo client initialized.")
                self._wait_for_interrupt()
            else:
                print_err("Failed to establish Murmur connectivity.")
        else:
            print_err("Failed to initialize Mumimo connection singleton.")

    def _wait_for_interrupt(self) -> None:
        try:
            while True:
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("Gracefully exiting Mumimo client...")
            if self._murmur_connection_instance is not None:
                print("Disconnecting from Murmur server...")
                if self._murmur_connection_instance.stop():
                    print("Disconnected from Murmur server.")
            print("Mumimo client closed.")
