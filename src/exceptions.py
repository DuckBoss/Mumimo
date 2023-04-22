import logging
from typing import Optional


class LoggedException(Exception):
    def __init__(self, msg: str, logger: Optional[logging.Logger] = None) -> None:
        if isinstance(logger, logging.Logger):
            logging.exception(str(msg))
        super().__init__(msg)


class ValidationError(LoggedException):
    def __init__(self, msg: str, logger: Optional[logging.Logger] = None) -> None:
        super().__init__(msg, logger=logger)


class ConnectivityError(LoggedException):
    def __init__(self, msg: str, logger: Optional[logging.Logger] = None) -> None:
        super().__init__(msg, logger=logger)


class PluginError(LoggedException):
    def __init__(self, msg: str, logger: Optional[logging.Logger] = None) -> None:
        super().__init__(msg, logger)


class ServiceError(LoggedException):
    def __init__(self, msg: str, logger: Optional[logging.Logger] = None) -> None:
        super().__init__(msg, logger=logger)


class DatabaseServiceError(ServiceError):
    def __init__(self, msg: str, logger: Optional[logging.Logger] = None) -> None:
        super().__init__(msg, logger=logger)


class ConfigError(LoggedException):
    def __init__(self, msg: str, logger: Optional[logging.Logger] = None) -> None:
        super().__init__(msg, logger=logger)


class ConfigReadError(ConfigError):
    def __init__(self, msg: str, logger: Optional[logging.Logger] = None) -> None:
        super().__init__(msg, logger=logger)


class ConfigWriteError(ConfigError):
    def __init__(self, msg: str, logger: Optional[logging.Logger] = None) -> None:
        super().__init__(msg, logger=logger)
