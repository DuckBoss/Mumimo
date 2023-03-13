from typing import Optional

from ..config import Config
from ..constants import DEFAULT_PATH_CONFIG_FILE
from ..logging import get_logger
from ..logging import print_warn as _print_warn
from ..settings import settings

_logger = get_logger(__name__)
print_warn = _print_warn(logger=_logger)


def initialize_mumimo_config(cfg_path: Optional[str] = None) -> "Config":
    # Load in configurations from custom config file path if present.
    # Otherwise load configurations from default config file path.
    _cfg_instance: Optional["Config"] = settings.get_mumimo_config()
    if _cfg_instance is None:
        if not cfg_path:
            cfg_path = DEFAULT_PATH_CONFIG_FILE
            print_warn("Mumimo config file path not provided. Reading config from default path.")
        _cfg_instance = Config(cfg_path)
        _cfg_instance.read()
        settings.set_mumimo_config(_cfg_instance)
    return _cfg_instance
