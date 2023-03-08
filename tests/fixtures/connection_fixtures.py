from typing import Any, Dict

import pytest

from src.config import ConfigSingleton
from src.constants import SysArgs


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
        SysArgs.SYS_HOST: "127.0.0.1",
        SysArgs.SYS_PORT: "64738",
        SysArgs.SYS_USER: "test",
        SysArgs.SYS_PASS: "test",
        SysArgs.SYS_CERT: "path/to/cert",
        SysArgs.SYS_TOKENS: "token1 token2",
        SysArgs.SYS_KEY: "path/to/key",
        SysArgs.SYS_RECONNECT: False,
        SysArgs.SYS_VERBOSE: 0,
    }


@pytest.fixture(autouse=True)
def invalid_connection_params() -> Dict[str, Any]:
    return {
        SysArgs.SYS_HOST: "hello",
        SysArgs.SYS_PORT: "hello",
        SysArgs.SYS_USER: "test",
        SysArgs.SYS_PASS: "test",
        SysArgs.SYS_CERT: "path/to/cert",
        SysArgs.SYS_TOKENS: "token1 token2",
        SysArgs.SYS_KEY: "path/to/key",
        SysArgs.SYS_RECONNECT: False,
        SysArgs.SYS_VERBOSE: 0,
    }
