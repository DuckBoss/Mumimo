import logging
import time
from typing import TYPE_CHECKING, Dict, Optional

from .murmur_connection import MurmurConnection
from .services.init_service import MumimoInitService
from .settings import settings
from .utils import connection_utils

if TYPE_CHECKING:
    from .client_state import ClientState

logger = logging.getLogger(__name__)


class MumimoService:
    _murmur_connection_instance: Optional[MurmurConnection]

    def __init__(self, sys_args: Dict[str, str]) -> None:
        self._setup(sys_args)

    def _setup(self, sys_args: Dict[str, str]) -> None:
        if not connection_utils.is_supported_platform():
            logger.warning("Mumimo is only supported for Linux and MacOS systems. You may run into unexpected issues on Windows and other systems.")
        logger.info("Initializing Mumimo client...")
        _init_service = MumimoInitService(sys_args)
        logger.info("Initializing client settings...")
        _config = _init_service.initialize_config()
        _connection_params = _init_service.initialize_client_settings(_config)
        logger.info("Mumimo client settings initialized.")
        self.initialize_connection(_connection_params)

    def initialize_connection(self, connection_params) -> None:
        logger.info("Establishing Murmur connectivity...")
        self._murmur_connection_instance = MurmurConnection()
        if self._murmur_connection_instance is not None:
            self._murmur_connection_instance.setup(connection_params)
            self._murmur_connection_instance.ready().connect()
            if self._murmur_connection_instance.is_connected:
                _client_state: Optional["ClientState"] = settings.get_client_state()
                if _client_state is not None:
                    _client_state.audio_properties.mute()
            if self._murmur_connection_instance.start():
                logger.info("Established Murmur connectivity.")
                logger.info("Mumimo client initialized.")
                self._wait_for_interrupt()
            else:
                logger.error("Failed to establish Murmur connectivity.")
        else:
            logger.error("Failed to initialize Mumimo connection instance singleton.")

    def _wait_for_interrupt(self) -> None:
        try:
            while True:
                time.sleep(0.1)
        except KeyboardInterrupt:
            logger.info("Gracefully exiting Mumimo client...")
            if self._murmur_connection_instance is not None:
                logger.info("Disconnecting from Murmur server...")
                if self._murmur_connection_instance.stop():
                    logger.info("Disconnected from Murmur server.")
            logger.info("Mumimo client closed.")
