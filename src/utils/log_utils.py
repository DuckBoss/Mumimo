from typing import Any, Dict, Optional

from ..constants import DEFAULT_PATH_LOGGING_CONFIG_FILE, LogCfgSections
from ..log_config import LogConfig
from ..settings import settings


def initialize_log_config(cfg_path: Optional[str] = None) -> "LogConfig":
    # Load in configurations from custom config file path if present.
    # Otherwise load configurations from default config file path.
    _cfg_instance: Optional["LogConfig"] = settings.configs.get_log_config()
    if _cfg_instance is None:
        if not cfg_path:
            cfg_path = DEFAULT_PATH_LOGGING_CONFIG_FILE
        _cfg_instance = LogConfig(cfg_path)
        _cfg_instance.read(cfg_path)
        settings.configs.set_log_config(_cfg_instance)
    return _cfg_instance


def privacy_file_redact_all_check():
    _log_config = settings.configs.get_log_config()
    if _log_config is None:
        return False
    file_privacy_dict: Dict[str, Any] = _log_config.get(LogCfgSections.OUTPUT_FILE_PRIVACY, {})
    return all(file_privacy_dict.values())


def privacy_console_redact_all_check():
    _log_config = settings.configs.get_log_config()
    if _log_config is None:
        return False
    console_privacy_dict: Dict[str, Any] = _log_config.get(LogCfgSections.OUTPUT_CONSOLE_PRIVACY, {})
    return all(console_privacy_dict.values())
