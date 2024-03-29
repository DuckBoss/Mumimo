import asyncio
import logging
from typing import TYPE_CHECKING, Any, Dict, Optional

from .exceptions import ServiceError
from .murmur_connection import MurmurConnection
from .services.init_services.mumimo_init_service import MumimoInitService
from .settings import settings
from .utils import connection_utils, mumble_utils

if TYPE_CHECKING:
    from .client_state import ClientState

logger = logging.getLogger(__name__)


class MumimoService:
    _murmur_connection_instance: Optional[MurmurConnection]

    def __init__(self, sys_args: Dict[str, str]) -> None:
        asyncio.run(self._setup(sys_args))

    async def _setup(self, sys_args: Dict[str, str]) -> None:
        if not connection_utils.is_supported_platform():
            logger.warning("Mumimo is only supported for Linux and MacOS systems. You may run into unexpected issues on Windows and other systems.")
        logger.info("Initializing Mumimo client...")
        _mumimo_init_service: MumimoInitService = MumimoInitService(sys_args)
        await _mumimo_init_service.initialize()
        _connection_params = await _mumimo_init_service.get_connection_parameters()
        if not _connection_params:
            raise ServiceError(
                "Unable to retrieve client connection parameters: attempted to retrieve connection parameters before initializing client settings.",
                logger=logger,
            )
        await self.initialize_connection(_connection_params)

    async def initialize_connection(self, connection_params: Dict[str, Any]) -> None:
        logger.info("Establishing Murmur connectivity...")
        self._murmur_connection_instance = MurmurConnection()
        if self._murmur_connection_instance is not None:
            self._murmur_connection_instance.setup(connection_params)
            self._murmur_connection_instance.ready().connect()
            if self._murmur_connection_instance.is_connected:
                settings.connection.set_murmur_connection(self._murmur_connection_instance)
                _client_state: Optional["ClientState"] = settings.state.get_client_state()
                if _client_state is not None:
                    _client_state.audio_properties.mute()
            if self._murmur_connection_instance.start():
                logger.info("Established Murmur connectivity.")
                logger.info("Mumimo client initialized.")
                await self._murmur_connection_instance._async_post_connection_actions()
                await self._wait_for_interrupt()
            else:
                logger.error("Failed to establish Murmur connectivity.")
        else:
            logger.error("Failed to initialize Mumimo connection instance singleton.")

    async def _wait_for_interrupt(self) -> None:
        try:
            while True:
                await asyncio.sleep(0.1)
        except asyncio.exceptions.CancelledError:
            await mumble_utils.Management.exit_server()
