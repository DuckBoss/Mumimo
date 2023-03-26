import logging

_logger = logging.getLogger(__name__)


def register(func):
    def wrapper(name: str = func.__name__):
        _logger.debug(f"Command method called - {name}")
        func()
        _logger.debug(f"Command method executed - {name}")

    return wrapper
