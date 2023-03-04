from typing import Any, Dict

import pytest

from src.config import ConfigSingleton
from src.constants import SYS_ARGS


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
        SYS_ARGS.SYS_HOST: "127.0.0.1",
        SYS_ARGS.SYS_PORT: "64738",
        SYS_ARGS.SYS_USER: "test",
        SYS_ARGS.SYS_PASS: "test",
        SYS_ARGS.SYS_CERT: "path/to/cert",
        SYS_ARGS.SYS_TOKENS: "token1 token2",
        SYS_ARGS.SYS_KEY: "path/to/key",
        SYS_ARGS.SYS_RECONNECT: False,
        SYS_ARGS.SYS_VERBOSE: 0,
    }


@pytest.fixture(autouse=True)
def invalid_connection_params() -> Dict[str, Any]:
    return {
        SYS_ARGS.SYS_HOST: "hello",
        SYS_ARGS.SYS_PORT: "hello",
        SYS_ARGS.SYS_USER: "test",
        SYS_ARGS.SYS_PASS: "test",
        SYS_ARGS.SYS_CERT: "path/to/cert",
        SYS_ARGS.SYS_TOKENS: "token1 token2",
        SYS_ARGS.SYS_KEY: "path/to/key",
        SYS_ARGS.SYS_RECONNECT: False,
        SYS_ARGS.SYS_VERBOSE: 0,
    }
