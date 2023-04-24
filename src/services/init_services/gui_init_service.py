import logging
from typing import Dict, Optional

from ...config import Config
from ...constants import DEFAULT_PATH_CONFIG_FILE
from ...exceptions import ConfigError
from ...settings import settings

logger = logging.getLogger(__name__)


class GUIInitService:
    def __init__(self, sys_args: Dict[str, str]) -> None:
        self._sys_args = sys_args

    def initialize_gui(self, cfg_path: Optional[str] = None) -> "Config":
        # Load in themes from custom themes file path if present.
        # Otherwise load themes from default themes file path.
        _cfg_instance: Optional["Config"] = settings.configs.get_gui_themes()
        if _cfg_instance is None:
            if not cfg_path:
                cfg_path = DEFAULT_PATH_CONFIG_FILE
                logger.warning("Mumimo gui config file path not provided. Reading gui config from default path.")
            _cfg_instance = Config(cfg_path)
            _cfg_instance.read()
            settings.configs.set_gui_themes(_cfg_instance)

        _cfg_instance = settings.configs.get_gui_themes()
        if _cfg_instance is None:
            raise ConfigError("An unexpected error occurred where the gui config file was not read during initialization.", logger=logger)
        return _cfg_instance
