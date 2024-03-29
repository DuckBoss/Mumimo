import logging
import pathlib
import sys
from typing import Dict, Optional, TYPE_CHECKING, Mapping, Any

from .constants import VERBOSE_HIGH, VERBOSE_MIN, VERBOSE_STANDARD, LogCfgFields, SysArgs
from .settings import settings
from .utils import log_utils
from .version import version

_IS_INITIALIZED: bool = False
_log_file_handler: Optional[logging.Handler] = None
_log_console_handler: Optional[logging.Handler] = None
_logger = logging.getLogger(__name__)


if TYPE_CHECKING:
    from logging import _FormatStyle


class LogFormatter(logging.Formatter):
    _grey = "\x1b[38;20m"
    _cyan = "\x1b[36:36m"
    _yellow = "\x1b[33;20m"
    _red = "\x1b[31;20m"
    _bold_red = "\x1b[31;1m"
    _reset = "\x1b[0m"
    _fmt = ""

    FORMATS = {
        logging.DEBUG: _fmt,
        logging.INFO: _fmt,
        logging.WARNING: _fmt,
        logging.ERROR: _fmt,
        logging.CRITICAL: _fmt,
    }

    def __init__(
        self,
        fmt: str | None = None,
        datefmt: str | None = None,
        style: "_FormatStyle" = "%",
        validate: bool = True,
        *,
        defaults: Mapping[str, Any] | None = None,
    ) -> None:
        super().__init__(fmt, datefmt, style, validate, defaults=defaults)
        if fmt is not None:
            self.FORMATS = {
                logging.DEBUG: self._cyan + fmt + self._reset,
                logging.INFO: self._grey + fmt + self._reset,
                logging.WARNING: self._yellow + fmt + self._reset,
                logging.ERROR: self._red + fmt + self._reset,
                logging.CRITICAL: self._bold_red + fmt + self._reset,
            }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


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
    _logging_formatter = LogFormatter(_log_config.get(LogCfgFields.OUTPUT.CONSOLE.FORMAT))
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
