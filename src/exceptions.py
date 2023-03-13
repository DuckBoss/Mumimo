import logging
from typing import Optional

from .logging import print


class LoggedException(Exception):
    def __init__(self, msg: str, logger: Optional[logging.Logger] = None, *args) -> None:
        if isinstance(logger, logging.Logger):
            print(logger)(str(msg), logging.ERROR)
        super().__init__(msg, *args)


class ValidationError(LoggedException):
    def __init__(self, msg: str, logger: Optional[logging.Logger] = None, *args) -> None:
        super().__init__(msg, logger=logger, *args)


class ConnectivityError(LoggedException):
    def __init__(self, msg: str, logger: Optional[logging.Logger] = None, *args) -> None:
        super().__init__(msg, logger=logger, *args)


class ServiceError(LoggedException):
    def __init__(self, msg: str, logger: Optional[logging.Logger] = None, *args) -> None:
        super().__init__(msg, logger=logger, *args)


class ConfigError(LoggedException):
    def __init__(self, msg: str, logger: Optional[logging.Logger] = None, *args) -> None:
        super().__init__(msg, logger=logger, *args)


class ConfigReadError(ConfigError):
    def __init__(self, msg: str, logger: Optional[logging.Logger] = None, *args) -> None:
        super().__init__(msg, logger=logger, *args)


class ConfigWriteError(ConfigError):
    def __init__(self, msg: str, logger: Optional[logging.Logger] = None, *args) -> None:
        super().__init__(msg, logger=logger, *args)
