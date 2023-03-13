from typing import Optional

from ..settings import settings
from ..constants import DEFAULT_PATH_LOGGING_CONFIG_FILE
from ..log_config import LogConfig


def initialize_log_config(cfg_path: Optional[str] = None) -> "LogConfig":
    # Load in configurations from custom config file path if present.
    # Otherwise load configurations from default config file path.
    _cfg_instance: Optional["LogConfig"] = settings.get_log_config()
    if _cfg_instance is None:
        if not cfg_path:
            cfg_path = DEFAULT_PATH_LOGGING_CONFIG_FILE
        _cfg_instance = LogConfig(cfg_path)
        _cfg_instance.read(cfg_path)
        settings.set_log_config(_cfg_instance)
    return _cfg_instance
