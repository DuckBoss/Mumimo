from typing import Any, Dict

import pytest

from src.config import ConfigSingleton
from src.constants import SYS_CERT, SYS_HOST, SYS_KEY, SYS_PASS, SYS_PORT, SYS_RECONNECT, SYS_TOKENS, SYS_USER, SYS_VERBOSE


@pytest.fixture(autouse=True)
def cfg_instance():
    _cfg_instance = ConfigSingleton().instance()
    yield _cfg_instance
    if _cfg_instance is not None:
        _cfg_instance.clear()
        del _cfg_instance


@pytest.fixture(autouse=True)
def cfg_instance_teardown():
    _cfg_instance = ConfigSingleton().instance()
    yield
    if _cfg_instance is not None:
        _cfg_instance.clear()
        del _cfg_instance


@pytest.fixture(autouse=True)
def valid_connection_params() -> Dict[str, Any]:
    return {
        SYS_HOST: "127.0.0.1",
        SYS_PORT: "64738",
        SYS_USER: "test",
        SYS_PASS: "test",
        SYS_CERT: "path/to/cert",
        SYS_TOKENS: "token1 token2",
        SYS_KEY: "path/to/key",
        SYS_RECONNECT: False,
        SYS_VERBOSE: 0,
    }


@pytest.fixture(autouse=True)
def invalid_connection_params() -> Dict[str, Any]:
    return {
        SYS_HOST: "hello",
        SYS_PORT: "hello",
        SYS_USER: "test",
        SYS_PASS: "test",
        SYS_CERT: "path/to/cert",
        SYS_TOKENS: "token1 token2",
        SYS_KEY: "path/to/key",
        SYS_RECONNECT: False,
        SYS_VERBOSE: 0,
    }
