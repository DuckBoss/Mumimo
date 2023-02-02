import builtins
import logging
import pathlib
import sys
from typing import Optional
from logging.handlers import RotatingFileHandler
from .utils import config_utils
from .constants import VERBOSE_MIN, VERBOSE_PLUS, VERBOSE_STANDARD
from .version import version

_is_initialized = False


def init_logger() -> bool:
    global _is_initialized
    if _is_initialized:
        return False
    _cfg_instance = config_utils.get_config_instance()
    _log_parent_directory = pathlib.Path.cwd() / _cfg_instance["output.logging"]["path"]
    _enable_log = bool(_cfg_instance["output.logging"]["enable"])
    _log_version_directory = _log_parent_directory / f"mumimo_{version()}/"
    if not _log_parent_directory.exists() and _enable_log:
        pathlib.Path.mkdir(_log_parent_directory)
    if not _log_version_directory.exists() and _enable_log:
        pathlib.Path.mkdir(_log_version_directory)
    _is_initialized = True
    return True


def get_logger(logger_name: str):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    if not logger.hasHandlers():
        _cfg_instance = config_utils.get_config_instance()
        if bool(_cfg_instance["output.logging"]["enable"]):
            file_handler = get_file_handler()
            if file_handler is not None:
                logger.addHandler(file_handler)
        console_handler = get_console_handler()
        if console_handler is not None:
            logger.addHandler(console_handler)
    return logger


def _print(msg: str, logger: logging.Logger, level: int = logging.INFO, verbosity: int = VERBOSE_MIN) -> None:
    if isinstance(logger, logging.Logger):
        logger.log(level, msg)
    _cfg_instance = config_utils.get_config_instance()
    _verbosity = int(_cfg_instance["output.logging"]["verbosity"])
    _console_formatter = _cfg_instance.get("output.console", "format")
    if verbosity > VERBOSE_MIN or _verbosity >= VERBOSE_STANDARD:
        if _console_formatter:
            builtins.print(
                _console_formatter % {"levelname": logging.getLevelName(level), "message": msg},
                file=sys.stdout,
            )


def _debug(msg: str, logger: logging.Logger) -> None:
    if not _is_initialized:
        return
    if isinstance(logger, logging.Logger):
        logger.debug(msg)
    _cfg_instance = config_utils.get_config_instance()
    _verbosity = int(_cfg_instance["output.logging"]["verbosity"])
    _console_formatter = _cfg_instance.get("output.console", "format")
    if _verbosity >= VERBOSE_PLUS:
        if _console_formatter:
            builtins.print(
                _console_formatter % {"levelname": "DEBUG", "message": msg},
                file=sys.stderr,
            )


def _error(msg: str, logger: logging.Logger) -> None:
    if not _is_initialized:
        return
    if isinstance(logger, logging.Logger):
        logger.error(msg)
    _cfg_instance = config_utils.get_config_instance()
    _verbosity = int(_cfg_instance["output.logging"]["verbosity"])
    _console_formatter = _cfg_instance.get("output.console", "format")
    if _verbosity >= VERBOSE_MIN:
        if _console_formatter:
            builtins.print(
                _console_formatter % {"levelname": "ERROR", "message": msg},
                file=sys.stderr,
            )


def _warning(msg: str, logger: logging.Logger) -> None:
    if not _is_initialized:
        return
    if isinstance(logger, logging.Logger):
        logger.warning(msg)
    _cfg_instance = config_utils.get_config_instance()
    _verbosity = int(_cfg_instance["output.logging"]["verbosity"])
    _console_formatter = _cfg_instance.get("output.console", "format")
    if _verbosity >= VERBOSE_MIN:
        if _console_formatter:
            builtins.print(
                _console_formatter % {"levelname": "WARNING", "message": msg},
                file=sys.stdout,
            )


def get_console_handler():
    if not _is_initialized:
        return
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.CRITICAL)
    _cfg_instance = config_utils.get_config_instance()
    _logging_formatter = _cfg_instance.get("output.logging", "format")
    console_handler.setFormatter(_logging_formatter)
    return console_handler


def get_file_handler() -> Optional[RotatingFileHandler]:
    if not _is_initialized:
        return

    _cfg_instance = config_utils.get_config_instance()
    _logging_formatter = _cfg_instance.get("output.logging", "format")
    _log_location = pathlib.Path.cwd() / _cfg_instance["output.logging"]["path"] / f"mumimo_{version()}"
    _log_name = _cfg_instance["output.logging"]["name"]
    _max_bytes = int(_cfg_instance["output.logging"]["max_bytes"])
    _max_logs = int(_cfg_instance["output.logging"]["max_logs"])
    _log_level = _cfg_instance["output.logging"]["level"]

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
