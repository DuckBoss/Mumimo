import pathlib
from typing import Optional

from ..config import Config, ConfigSingleton
from ..constants import DEFAULT_PATH_CONFIG_FILE
from ..exceptions import ConfigReadError

from ..logging import get_logger

_logger = get_logger(__name__)


def initialize_mumimo_config(cfg_path: Optional[str] = None) -> "Config":
    # Load in configurations from custom config file path if present.
    # Otherwise load configurations from default config file.
    _cfg_instance = get_config_instance()
    try:
        if not cfg_path:
            cfg_path = DEFAULT_PATH_CONFIG_FILE
        _cfg_instance.read(cfg_path)
    except ConfigReadError:
        raise
    finally:
        return _cfg_instance


def get_config_instance() -> "Config":
    _cfg_instance = ConfigSingleton().instance()
    if _cfg_instance is None:
        raise ConfigReadError("Unexpected error: unable to read config file.")
    return _cfg_instance
