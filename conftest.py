from typing import Dict, Union

import pytest

from src.constants import SYS_CERT, SYS_DEBUG, SYS_HOST, SYS_KEY, SYS_PASS, SYS_PORT, SYS_RECONNECT, SYS_TOKENS, SYS_USER


@pytest.fixture(autouse=True)
def valid_connection_params() -> Dict[str, Union[str, bool]]:
    return {
        SYS_HOST: "127.0.0.1",
        SYS_PORT: "64738",
        SYS_USER: "test",
        SYS_PASS: "test",
        SYS_CERT: "path/to/cert",
        SYS_TOKENS: "token1 token2",
        SYS_KEY: "path/to/key",
        SYS_RECONNECT: False,
        SYS_DEBUG: False,
    }


@pytest.fixture(autouse=True)
def invalid_connection_params() -> Dict[str, Union[str, bool]]:
    return {
        SYS_HOST: "hello",
        SYS_PORT: "hello",
        SYS_USER: "test",
        SYS_PASS: "test",
        SYS_CERT: "path/to/cert",
        SYS_TOKENS: "token1 token2",
        SYS_KEY: "path/to/key",
        SYS_RECONNECT: False,
        SYS_DEBUG: False,
    }
