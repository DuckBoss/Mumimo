import builtins
import logging
import pathlib
import sys
from logging.handlers import RotatingFileHandler
from typing import Any, Dict, Optional

import toml

from .constants import DEFAULT_PATH_LOGGING_CONFIG_FILE, VERBOSE_MIN, VERBOSE_NONE, VERBOSE_STANDARD, LogCfgFields, LogCfgSections, SysArgs
from .version import version

_IS_INITIALIZED: bool = False
_log_config: Dict[str, Any] = {}


def _read_log_config(cfg_path: Optional[str] = None):
    if not cfg_path:
        cfg_path = DEFAULT_PATH_LOGGING_CONFIG_FILE
    _cfg_path = pathlib.Path.cwd() / cfg_path
    with open(str(_cfg_path.resolve()), "r", encoding="utf-8") as file_handler:
        contents = toml.load(file_handler, _dict=dict)
        _log_config.update(contents)


def init_logger(sys_args: Optional[Dict[str, str]] = None) -> bool:
    global _IS_INITIALIZED
    if _IS_INITIALIZED:
        return False
    if sys_args is None:
        sys_args = {}
    _read_log_config(sys_args.get(SysArgs.SYS_LOG_CONFIG_FILE, None))
    _log_config[SysArgs.SYS_VERBOSE] = int(sys_args.get(SysArgs.SYS_VERBOSE, VERBOSE_MIN))
    _log_parent_directory = pathlib.Path.cwd() / _log_config[LogCfgSections.OUTPUT][LogCfgSections.FILE][LogCfgFields.OUTPUT.FILE.PATH]
    _enable_log = bool(_log_config[LogCfgSections.OUTPUT][LogCfgSections.FILE][LogCfgFields.OUTPUT.FILE.ENABLE])
    _log_version_directory = _log_parent_directory / f"mumimo_{version()}/"
    if not _log_parent_directory.exists() and _enable_log:
        pathlib.Path.mkdir(_log_parent_directory)
    if not _log_version_directory.exists() and _enable_log:
        pathlib.Path.mkdir(_log_version_directory)
    _IS_INITIALIZED = True
    return True


def get_logger(logger_name: str):
    if not _log_config:
        _read_log_config()
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    if not logger.hasHandlers():
        if bool(_log_config[LogCfgSections.OUTPUT][LogCfgSections.FILE][LogCfgFields.OUTPUT.FILE.ENABLE]):
            file_handler = get_file_handler()
            if file_handler is not None:
                logger.addHandler(file_handler)
        console_handler = get_console_handler()
        if console_handler is not None:
            logger.addHandler(console_handler)
    return logger


def _print(msg: str, logger: logging.Logger, level: int = logging.INFO, verbosity: int = VERBOSE_NONE) -> None:
    if not _IS_INITIALIZED:
        return
    if isinstance(logger, logging.Logger):
        logger.log(level, msg)
    _verbosity = int(_log_config[SysArgs.SYS_VERBOSE])
    _console_formatter = _log_config[LogCfgSections.OUTPUT][LogCfgSections.CONSOLE][LogCfgFields.OUTPUT.CONSOLE.FORMAT]
    if verbosity >= VERBOSE_MIN or _verbosity >= VERBOSE_MIN:
        if _console_formatter:
            builtins.print(
                _console_formatter % {"levelname": logging.getLevelName(level), "message": msg},
                file=sys.stdout,
            )


def _debug(msg: str, logger: logging.Logger) -> None:
    if not _IS_INITIALIZED:
        return
    if isinstance(logger, logging.Logger):
        logger.debug(msg)
    _verbosity = int(_log_config[SysArgs.SYS_VERBOSE])
    _console_formatter = _log_config[LogCfgSections.OUTPUT][LogCfgSections.CONSOLE][LogCfgFields.OUTPUT.CONSOLE.FORMAT]
    if _verbosity >= VERBOSE_STANDARD:
        if _console_formatter:
            builtins.print(
                _console_formatter % {"levelname": "DEBUG", "message": msg},
                file=sys.stderr,
            )


def _error(msg: str, logger: logging.Logger) -> None:
    if not _IS_INITIALIZED:
        return
    if isinstance(logger, logging.Logger):
        logger.error(msg)
    _verbosity = int(_log_config[SysArgs.SYS_VERBOSE])
    _console_formatter = _log_config[LogCfgSections.OUTPUT][LogCfgSections.CONSOLE][LogCfgFields.OUTPUT.CONSOLE.FORMAT]
    if _verbosity >= VERBOSE_MIN:
        if _console_formatter:
            builtins.print(
                _console_formatter % {"levelname": "ERROR", "message": msg},
                file=sys.stderr,
            )


def _warning(msg: str, logger: logging.Logger) -> None:
    if not _IS_INITIALIZED:
        return
    if isinstance(logger, logging.Logger):
        logger.warning(msg)
    _verbosity = int(_log_config[SysArgs.SYS_VERBOSE])
    _console_formatter = _log_config[LogCfgSections.OUTPUT][LogCfgSections.CONSOLE][LogCfgFields.OUTPUT.CONSOLE.FORMAT]
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
    _logging_formatter = logging.Formatter(_log_config[LogCfgSections.OUTPUT][LogCfgSections.FILE][LogCfgFields.OUTPUT.FILE.FORMAT])
    console_handler.setFormatter(_logging_formatter)
    return console_handler


def get_file_handler() -> Optional[RotatingFileHandler]:
    if not _IS_INITIALIZED:
        return None

    _logging_formatter = logging.Formatter(_log_config[LogCfgSections.OUTPUT][LogCfgSections.FILE][LogCfgFields.OUTPUT.FILE.FORMAT])
    _log_location = (
        pathlib.Path.cwd() / _log_config[LogCfgSections.OUTPUT][LogCfgSections.FILE][LogCfgFields.OUTPUT.FILE.PATH] / f"mumimo_{version()}"
    )
    _log_name = _log_config[LogCfgSections.OUTPUT][LogCfgSections.FILE][LogCfgFields.OUTPUT.FILE.NAME] % version()
    _max_bytes = int(_log_config[LogCfgSections.OUTPUT][LogCfgSections.FILE][LogCfgFields.OUTPUT.FILE.MAX_BYTES])
    _max_logs = int(_log_config[LogCfgSections.OUTPUT][LogCfgSections.FILE][LogCfgFields.OUTPUT.FILE.MAX_LOGS])
    _log_level = _log_config[LogCfgSections.OUTPUT][LogCfgSections.FILE][LogCfgFields.OUTPUT.FILE.LEVEL]

    file_handler = RotatingFileHandler(_log_location / _log_name, maxBytes=_max_bytes, backupCount=_max_logs, delay=True)
    file_handler.setLevel(_log_level)
    file_handler.setFormatter(_logging_formatter)
    return file_handler


def print(logger: logging.Logger):
    def wrap(msg: str, level: int = logging.INFO):
        _print(msg=msg, level=level, logger=logger)

    return wrap


def debug(logger: logging.Logger):
    def wrap(msg: str):
        _debug(msg=msg, logger=logger)

    return wrap


def print_warning(logger: logging.Logger):
    def wrap(msg: str):
        _warning(msg=msg, logger=logger)

    return wrap


def print_error(logger: logging.Logger):
    def wrap(msg: str):
        _error(msg=msg, logger=logger)

    return wrap


def print_warn(logger: logging.Logger):
    return print_warning(logger)


def print_err(logger: logging.Logger):
    return print_error(logger)
