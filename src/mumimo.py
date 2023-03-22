import asyncio
import logging
from typing import TYPE_CHECKING, Dict, Optional

from .constants import SysArgs
from .exceptions import ServiceError
from .murmur_connection import MurmurConnection
from .services.database_service import DatabaseService
from .services.mumimo_init_service import MumimoInitService
from .settings import settings
from .utils import connection_utils

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
        logger.info("Initializing client settings...")
        _config = _mumimo_init_service.initialize_config()
        _mumimo_init_service.initialize_client_settings(_config)
        _connection_params = _mumimo_init_service.get_connection_parameters()
        if not _connection_params:
            raise ServiceError(
                "Unable to retrieve client connection parameters: attempted to retrieve connection parameters before initializing client settings.",
                logger=logger,
            )
        logger.info("Mumimo client settings initialized.")
        logger.info("Initializing internal database...")
        _prioritized_env_opts = _mumimo_init_service.get_prioritized_env_options()
        if not _prioritized_env_opts:
            raise ServiceError(
                "Unable to retrieve prioritized environment parameters: attempted to retrieve prioritized environment parameters \
                    before initializing client settings.",
                logger=logger,
            )
        _db_init_service: DatabaseService = DatabaseService()
        await _db_init_service.initialize_database(
            dialect=_prioritized_env_opts.get(SysArgs.SYS_DB_DIALECT, ""),
            username=_prioritized_env_opts.get(SysArgs.SYS_DB_USER, ""),
            host=_prioritized_env_opts.get(SysArgs.SYS_DB_HOST, ""),
            password=_prioritized_env_opts.get(SysArgs.SYS_DB_PASS, None),
            database=_prioritized_env_opts.get(SysArgs.SYS_DB_NAME, None),
            drivername=_prioritized_env_opts.get(SysArgs.SYS_DB_DRIVER, None),
            query=_prioritized_env_opts.get(SysArgs.SYS_DB_QUERY, None),
        )
        logger.info("Mumimo internal database initialized.")
        await self.initialize_connection(_connection_params)

    async def initialize_connection(self, connection_params) -> None:
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
            logger.info("Gracefully exiting Mumimo client...")
            if self._murmur_connection_instance is not None:
                logger.info("Disconnecting from Murmur server...")
                if self._murmur_connection_instance.stop():
                    logger.info("Disconnected from Murmur server.")
                await DatabaseService().close(clean=True)
            _async_runner = asyncio.get_running_loop()
            if _async_runner.is_running():
                _async_runner.stop()
            logger.info("Mumimo client closed.")
