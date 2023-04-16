import logging
import pathlib
import sys
from typing import Dict, Optional

from .constants import VERBOSE_HIGH, VERBOSE_MIN, VERBOSE_STANDARD, LogCfgFields, SysArgs
from .settings import settings
from .utils import log_utils
from .version import version

_IS_INITIALIZED: bool = False
_log_file_handler: Optional[logging.Handler] = None
_log_console_handler: Optional[logging.Handler] = None
_logger = logging.getLogger(__name__)


def init_logger(sys_args: Optional[Dict[str, str]] = None) -> bool:
    global _IS_INITIALIZED, _log_file_handler, _log_console_handler
    if _IS_INITIALIZED:
        return False
    if sys_args is None:
        return False
    _log_config = log_utils.initialize_log_config(sys_args.get(SysArgs.SYS_LOG_CONFIG_FILE, None))
    _log_config.set(SysArgs.SYS_VERBOSE, int(sys_args.get(SysArgs.SYS_VERBOSE, VERBOSE_MIN)), create_keys_if_not_exists=True)
    _log_parent_directory: pathlib.Path = pathlib.Path.cwd() / _log_config.get(LogCfgFields.OUTPUT.FILE.PATH)
    _log_version_directory: pathlib.Path = _log_parent_directory / f"mumimo_{version()}/"
    _enable_file_log = bool(_log_config.get(LogCfgFields.OUTPUT.FILE.ENABLE))
    if _enable_file_log:
        pathlib.Path.mkdir(_log_parent_directory, exist_ok=True)
        pathlib.Path.mkdir(_log_version_directory, exist_ok=True)
    _enable_console_log = _log_config.get(SysArgs.SYS_VERBOSE) >= VERBOSE_MIN
    _logger.root.setLevel(logging.DEBUG)
    if not _logger.root.hasHandlers():
        if _enable_file_log:
            file_handler = get_file_handler()
            if file_handler is not None:
                _logger.root.addHandler(file_handler)
                _log_file_handler = file_handler
            else:
                print("File handler unable to initialize.")
        if _enable_console_log:
            console_handler = get_console_handler()
            if console_handler is not None:
                _logger.root.addHandler(console_handler)
                _log_console_handler = console_handler
    # Disable logging for asyncio/aiosqlite libraries unless the verbose level is max:
    if _log_config.get(SysArgs.SYS_VERBOSE) >= VERBOSE_HIGH:
        logging.getLogger("asyncio").setLevel(logging.DEBUG)
        logging.getLogger("aiosqlite").setLevel(logging.DEBUG)
    else:
        logging.getLogger("asyncio").setLevel(logging.ERROR)
        logging.getLogger("aiosqlite").setLevel(logging.ERROR)
    _IS_INITIALIZED = True
    return _IS_INITIALIZED


def get_console_handler() -> Optional[logging.StreamHandler]:
    _log_config = settings.configs.get_log_config()
    if _log_config is None:
        return None
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.CRITICAL)
    _verbosity = int(_log_config.get(SysArgs.SYS_VERBOSE))
    if _verbosity == VERBOSE_MIN:
        console_handler.setLevel(logging.INFO)
    elif _verbosity >= VERBOSE_STANDARD:
        console_handler.setLevel(logging.DEBUG)
    _logging_formatter = logging.Formatter(_log_config.get(LogCfgFields.OUTPUT.CONSOLE.FORMAT))
    console_handler.setFormatter(_logging_formatter)
    return console_handler


def get_file_handler() -> Optional[logging.FileHandler]:
    _log_config = settings.configs.get_log_config()
    if _log_config is None:
        return None
    _logging_formatter = logging.Formatter(_log_config.get(LogCfgFields.OUTPUT.FILE.FORMAT))
    _log_location: pathlib.Path = pathlib.Path.cwd() / _log_config.get(LogCfgFields.OUTPUT.FILE.PATH) / f"mumimo_{version()}"
    _log_name: str = _log_config.get(LogCfgFields.OUTPUT.FILE.NAME) % version()
    _log_level: int = _log_config.get(LogCfgFields.OUTPUT.FILE.LEVEL)
    _log_location_path: pathlib.Path = (_log_location / _log_name).resolve()

    file_handler = logging.FileHandler(filename=_log_location_path)
    file_handler.setLevel(_log_level)
    file_handler.setFormatter(_logging_formatter)
    return file_handler


def log_privacy(msg: str, logger: logging.Logger, level: int = logging.INFO) -> None:
    if not _IS_INITIALIZED:
        return
    if not logger.hasHandlers():
        return

    _file_redact_all: bool = log_utils.privacy_file_redact_all_check()
    _console_redact_all: bool = log_utils.privacy_console_redact_all_check()

    if _log_file_handler:
        _cached_file_level: int = _log_file_handler.level
        if _file_redact_all:
            _log_file_handler.setLevel(logging.CRITICAL)
    if _log_console_handler:
        _cached_console_level: int = _log_console_handler.level
        if _console_redact_all:
            _log_console_handler.setLevel(logging.CRITICAL)

    if not _file_redact_all and not _console_redact_all:
        logger.log(level, msg)

    if _log_file_handler:
        _log_file_handler.setLevel(_cached_file_level)  # type: ignore
    if _log_console_handler:
        _log_console_handler.setLevel(_cached_console_level)  # type: ignore
