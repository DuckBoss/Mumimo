import logging
from typing import TYPE_CHECKING, Any, Dict

from ...constants import SysArgs
from ...services.database_service import DatabaseService
from ...services.init_services.cfg_init_service import ConfigInitService
from ...services.init_services.client_settings_init_service import ClientSettingsInitService
from ...services.init_services.plugins_init_service import PluginsInitService
from ...services.init_services.gui_init_service import GUIInitService

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from ...config import Config


class MumimoInitService:
    def __init__(self, sys_args: Dict[str, str]) -> None:
        self._sys_args: Dict[str, str] = sys_args
        self._cfg_init_service: ConfigInitService = ConfigInitService(sys_args)
        self._client_settings_init_service: ClientSettingsInitService = ClientSettingsInitService(sys_args)
        self._db_init_service: DatabaseService = DatabaseService()
        self._plugins_init_service: PluginsInitService = PluginsInitService(sys_args)
        self._gui_init_service: GUIInitService = GUIInitService(sys_args)

    async def initialize(self) -> None:
        # Initialize the mumimo configuration file.
        logger.info("Initializing configuration file...")
        cfg: "Config" = self._cfg_init_service.initialize_config(self._sys_args.get(SysArgs.SYS_CONFIG_FILE))
        logger.info("Mumimo client configuration initialized.")
        # Initialize mumimo client settings.
        logger.info("Initializing client settings...")
        self._client_settings_init_service.initialize_client_settings(cfg)
        logger.info("Mumimo client settings initialized.")
        # Initialize mumimo gui settings.
        logger.info("Initializing client gui settings...")
        self._gui_init_service.initialize_gui(self._sys_args.get(SysArgs.SYS_GUI_THEMES_FILE))
        logger.info("Client gui settings initialized.")
        # Initialize the internal database.
        logger.info("Initializing internal database...")
        # print(cfg)
        _prioritized_cfg_opts = self._client_settings_init_service.get_prioritized_cfg_options()
        # print(_prioritized_cfg_opts)
        _prioritized_env_opts = self._client_settings_init_service.get_prioritized_env_options()
        await self._db_init_service.initialize_database(
            dialect=_prioritized_env_opts.get(SysArgs.SYS_DB_DIALECT, None),
            username=_prioritized_env_opts.get(SysArgs.SYS_DB_USER, None),
            host=_prioritized_env_opts.get(SysArgs.SYS_DB_HOST, None),
            port=_prioritized_env_opts.get(SysArgs.SYS_DB_PORT, None),
            password=_prioritized_env_opts.get(SysArgs.SYS_DB_PASS, None),
            database_name=_prioritized_env_opts.get(SysArgs.SYS_DB_NAME, None),
            drivername=_prioritized_env_opts.get(SysArgs.SYS_DB_DRIVER, None),
            use_remote=_prioritized_cfg_opts.get(SysArgs.SYS_DB_USEREMOTEDB, None),
            local_database_dialect=_prioritized_cfg_opts.get(SysArgs.SYS_DB_LOCALDBDIALECT, None),
            local_database_path=_prioritized_cfg_opts.get(SysArgs.SYS_DB_LOCALDBPATH, None),
            local_database_driver=_prioritized_cfg_opts.get(SysArgs.SYS_DB_LOCALDBDRIVER, None),
        )
        logger.info("Mumimo internal database initialized.")
        # Initialize the plugins.
        logger.info("Mumimo plugins initializing...")
        await self._plugins_init_service.initialize_plugins(self._db_init_service)
        logger.info("Mumimo plugins initialized.")

    async def get_connection_parameters(self) -> Dict[str, Any]:
        return self._client_settings_init_service.get_connection_parameters()
