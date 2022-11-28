from typing import Optional

from ..config import Config, ConfigSingleton
from ..constants import DEFAULT_PATH_CONFIG_FILE
from ..exceptions import ConfigReadError


def initialize_mumimo_config(cfg_path: Optional[str] = None) -> "Config":
    # Load in configurations from custom config file path if present.
    # Otherwise load configurations from default config file.
    _cfg_instance = ConfigSingleton().instance()
    if _cfg_instance is None:
        raise ConfigReadError("Unexpected error: unable to read config file.")
    try:
        if not cfg_path:
            cfg_path = DEFAULT_PATH_CONFIG_FILE
        _cfg_instance.read(cfg_path)
    except ConfigReadError:
        print(f"Mumimo config initialization error: unable to read config file at '{cfg_path}'")
        raise
    return _cfg_instance
