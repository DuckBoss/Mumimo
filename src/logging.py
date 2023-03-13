import builtins
import logging
import pathlib
import sys
from typing import Dict, Optional

from .utils import log_utils
from .settings import settings
from .constants import VERBOSE_MIN, VERBOSE_NONE, VERBOSE_STANDARD, LogCfgFields, SysArgs
from .version import version

_IS_INITIALIZED: bool = False


def init_logger(sys_args: Optional[Dict[str, str]] = None) -> bool:
    global _IS_INITIALIZED
    if _IS_INITIALIZED:
        return False
    if sys_args is None:
        sys_args = {}
    _log_config = log_utils.initialize_log_config(sys_args.get(SysArgs.SYS_LOG_CONFIG_FILE, None))
    _log_config.set(SysArgs.SYS_VERBOSE, int(sys_args.get(SysArgs.SYS_VERBOSE, VERBOSE_MIN)), create_keys_if_not_exists=True)
    _log_parent_directory: pathlib.Path = pathlib.Path.cwd() / _log_config.get(LogCfgFields.OUTPUT.FILE.PATH)
    _enable_log = bool(_log_config.get(LogCfgFields.OUTPUT.FILE.ENABLE))
    _log_version_directory: pathlib.Path = _log_parent_directory / f"mumimo_{version()}/"
    if _enable_log:
        pathlib.Path.mkdir(_log_parent_directory, exist_ok=True)
        pathlib.Path.mkdir(_log_version_directory, exist_ok=True)
    _IS_INITIALIZED = True
    return _IS_INITIALIZED


def get_logger(logger_name: str) -> logging.Logger:
    _log_config = settings.get_log_config()
    if _log_config is None:
        _log_config = log_utils.initialize_log_config()
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    if not logger.hasHandlers():
        if bool(_log_config.get(LogCfgFields.OUTPUT.FILE.ENABLE)):
            file_handler = get_file_handler()
            if file_handler is not None:
                logger.addHandler(file_handler)
        console_handler = get_console_handler()
        if console_handler is not None:
            logger.addHandler(console_handler)
    return logger


def _print(
    msg: str, logger: logging.Logger, level: int = logging.INFO, verbosity: int = VERBOSE_NONE, skip_file: bool = False, skip_console: bool = False
) -> None:
    if not _IS_INITIALIZED:
        return
    _log_config = settings.get_log_config()
    if _log_config is None:
        return
    if not skip_file:
        if isinstance(logger, logging.Logger):
            logger.log(level, msg)
    if skip_console:
        return
    _verbosity = int(_log_config.get(SysArgs.SYS_VERBOSE))
    _console_formatter = _log_config.get(LogCfgFields.OUTPUT.CONSOLE.FORMAT)
    if verbosity >= VERBOSE_MIN or _verbosity >= VERBOSE_MIN:
        if _console_formatter:
            builtins.print(
                _console_formatter % {"levelname": logging.getLevelName(level), "message": msg},
                file=sys.stdout,
            )


def _debug(msg: str, logger: logging.Logger, skip_file: bool = False, skip_console: bool = False) -> None:
    if not _IS_INITIALIZED:
        return
    _log_config = settings.get_log_config()
    if _log_config is None:
        return
    if not skip_file:
        if isinstance(logger, logging.Logger):
            logger.debug(msg)
    if skip_console:
        return
    _verbosity = int(_log_config.get(SysArgs.SYS_VERBOSE))
    _console_formatter = _log_config.get(LogCfgFields.OUTPUT.CONSOLE.FORMAT)
    if _verbosity >= VERBOSE_STANDARD:
        if _console_formatter:
            builtins.print(
                _console_formatter % {"levelname": "DEBUG", "message": msg},
                file=sys.stderr,
            )


def _error(msg: str, logger: logging.Logger, exc: Optional[str] = None) -> None:
    if not _IS_INITIALIZED:
        return
    if isinstance(logger, logging.Logger):
        logger.error(f"{msg}")
    _verbosity = int(_log_config[SysArgs.SYS_VERBOSE])
    _console_formatter = _log_config.get(LogCfgFields.OUTPUT.CONSOLE.FORMAT)
    if _verbosity >= VERBOSE_MIN:
        if _console_formatter:
            builtins.print(
                _console_formatter % {"levelname": "ERROR", "message": msg},
                file=sys.stderr,
            )


def _warning(msg: str, logger: logging.Logger, skip_file: bool = False, skip_console: bool = False) -> None:
    if not _IS_INITIALIZED:
        return
    _log_config = settings.get_log_config()
    if _log_config is None:
        return
    if not skip_file:
        if isinstance(logger, logging.Logger):
            logger.warning(msg)
    if skip_console:
        return
    _verbosity = int(_log_config.get(SysArgs.SYS_VERBOSE))
    _console_formatter = _log_config.get(LogCfgFields.OUTPUT.CONSOLE.FORMAT)
    if _verbosity >= VERBOSE_MIN:
        if _console_formatter:
            builtins.print(
                _console_formatter % {"levelname": "WARNING", "message": msg},
                file=sys.stdout,
            )


def get_console_handler():
    if not _IS_INITIALIZED:
        return None
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.CRITICAL)
    _log_config = settings.get_log_config()
    if _log_config is None:
        return
    _logging_formatter = logging.Formatter(_log_config.get(LogCfgFields.OUTPUT.FILE.FORMAT))
    console_handler.setFormatter(_logging_formatter)
    return console_handler


def get_file_handler() -> Optional[logging.FileHandler]:
    if not _IS_INITIALIZED:
        return None
    _log_config = settings.get_log_config()
    if _log_config is None:
        return
    _logging_formatter = logging.Formatter(_log_config.get(LogCfgFields.OUTPUT.FILE.FORMAT))
    _log_location = pathlib.Path.cwd() / _log_config.get(LogCfgFields.OUTPUT.FILE.PATH) / f"mumimo_{version()}"
    _log_name = _log_config.get(LogCfgFields.OUTPUT.FILE.NAME) % version()
    _log_level = _log_config.get(LogCfgFields.OUTPUT.FILE.LEVEL)

    file_handler = logging.FileHandler(_log_location / _log_name, delay=True)
    file_handler.setLevel(_log_level)
    file_handler.setFormatter(_logging_formatter)
    return file_handler


def print(logger: logging.Logger):
    def wrap(msg: str, level: int = logging.INFO, skip_file: bool = False, skip_console: bool = False):
        _print(msg=msg, level=level, logger=logger, skip_file=skip_file, skip_console=skip_console)

    return wrap


def debug(logger: logging.Logger):
    def wrap(msg: str, skip_file: bool = False, skip_console: bool = False):
        _debug(msg=msg, logger=logger, skip_file=skip_file, skip_console=skip_console)

    return wrap


def print_warning(logger: logging.Logger):
    def wrap(msg: str, skip_file: bool = False, skip_console: bool = False):
        _warning(msg=msg, logger=logger, skip_file=skip_file, skip_console=skip_console)

    return wrap


def print_error(logger: logging.Logger):
    def wrap(msg: str, exc: Optional[str] = None):
        _error(msg=msg, exc=exc, logger=logger)

    return wrap


def print_warn(logger: logging.Logger):
    return print_warning(logger)


def print_err(logger: logging.Logger):
    return print_error(logger)
