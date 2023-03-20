import logging
from typing import Optional


class LoggedException(Exception):
    def __init__(self, msg: str, logger: Optional[logging.Logger] = None, *args) -> None:
        if isinstance(logger, logging.Logger):
            logging.exception(str(msg))
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


class DatabaseServiceError(ServiceError):
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
