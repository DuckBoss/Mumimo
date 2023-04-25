import logging
from typing import Dict, Optional

from ...config import Config
from ...constants import DEFAULT_PATH_GUI_THEMES_FILE
from ...exceptions import ConfigError
from ...settings import settings

logger = logging.getLogger(__name__)


class GUIInitService:
    def __init__(self, sys_args: Dict[str, str]) -> None:
        self._sys_args = sys_args

    def initialize_gui(self, themes_path: Optional[str] = None) -> "Config":
        # Load in themes from custom themes file path if present.
        # Otherwise load themes from default themes file path.
        _themes_instance: Optional["Config"] = settings.configs.get_gui_themes()
        if _themes_instance is None:
            if not themes_path:
                themes_path = DEFAULT_PATH_GUI_THEMES_FILE
                logger.warning("Mumimo gui themes file path not provided. Reading gui themes from default path.")
            _themes_instance = Config(themes_path)
            _themes_instance.read()
            settings.configs.set_gui_themes(_themes_instance)

        _themes_instance = settings.configs.get_gui_themes()
        if _themes_instance is None:
            raise ConfigError("An unexpected error occurred where the gui themes file was not read during initialization.", logger=logger)
        return _themes_instance
