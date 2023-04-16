import logging
from typing import Dict, Optional

from ...config import Config
from ...constants import DEFAULT_PATH_CONFIG_FILE
from ...exceptions import ConfigError
from ...settings import settings

logger = logging.getLogger(__name__)


class ConfigInitService:
    def __init__(self, sys_args: Dict[str, str]) -> None:
        self._sys_args = sys_args

    def initialize_config(self, cfg_path: Optional[str] = None) -> "Config":
        # Load in configurations from custom config file path if present.
        # Otherwise load configurations from default config file path.
        _cfg_instance: Optional["Config"] = settings.configs.get_mumimo_config()
        if _cfg_instance is None:
            if not cfg_path:
                cfg_path = DEFAULT_PATH_CONFIG_FILE
                logger.warning("Mumimo config file path not provided. Reading config from default path.")
            _cfg_instance = Config(cfg_path)
            _cfg_instance.read()
            settings.configs.set_mumimo_config(_cfg_instance)

        _cfg_instance = settings.configs.get_mumimo_config()
        if _cfg_instance is None:
            raise ConfigError("An unexpected error occurred where the config file was not read during initialization.", logger=logger)
        return _cfg_instance
