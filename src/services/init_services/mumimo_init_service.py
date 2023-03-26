import logging
from typing import TYPE_CHECKING, Any, Dict

from ...constants import SysArgs
from ...services.database_service import DatabaseService
from ...services.init_services.cfg_init_service import ConfigInitService
from ...services.init_services.client_settings_init_service import ClientSettingsInitService

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from ...config import Config


class MumimoInitService:
    def __init__(self, sys_args: Dict[str, str]) -> None:
        self._sys_args: Dict[str, str] = sys_args
        self._cfg_init_service: ConfigInitService = ConfigInitService(sys_args)
        self._client_settings_init_service: ClientSettingsInitService = ClientSettingsInitService(sys_args)
        self._db_init_service: DatabaseService = DatabaseService()

    async def initialize(self) -> None:
        # Initialize the mumimo configuration file.
        logger.info("Initializing configuration file...")
        cfg: "Config" = self._cfg_init_service.initialize_config(self._sys_args.get(SysArgs.SYS_CONFIG_FILE))
        logger.info("Mumimo client configuration initialized.")
        # Initialize mumimo client settings.
        logger.info("Initializing client settings...")
        self._client_settings_init_service.initialize_client_settings(cfg)
        logger.info("Mumimo client settings initialized.")
        # Initialize the internal database.
        logger.info("Initializing internal database...")
        _prioritized_env_opts = self._client_settings_init_service.get_prioritized_env_options()
        await self._db_init_service.initialize_database(
            dialect=_prioritized_env_opts.get(SysArgs.SYS_DB_DIALECT, ""),
            username=_prioritized_env_opts.get(SysArgs.SYS_DB_USER, ""),
            host=_prioritized_env_opts.get(SysArgs.SYS_DB_HOST, ""),
            password=_prioritized_env_opts.get(SysArgs.SYS_DB_PASS, None),
            database=_prioritized_env_opts.get(SysArgs.SYS_DB_NAME, None),
            drivername=_prioritized_env_opts.get(SysArgs.SYS_DB_DRIVER, None),
            query=_prioritized_env_opts.get(SysArgs.SYS_DB_QUERY, None),
        )
        logger.info("Mumimo internal database initialized.")

    async def get_connection_parameters(self) -> Dict[str, Any]:
        return self._client_settings_init_service.get_connection_parameters()
