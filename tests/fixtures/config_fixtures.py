from typing import Any, Dict

import pytest

from src.constants import CFG_FIELD_COMMENT, CFG_FIELD_DEAFEN, CFG_FIELD_MUTE, CFG_FIELD_RECONNECT, CFG_FIELD_REGISTER, CFG_FIELD_VERBOSE


@pytest.fixture(autouse=True)
def valid_cfg_path() -> str:
    return "tests/data/config/test_valid_config.toml"


@pytest.fixture(autouse=True)
def invalid_cfg_path() -> str:
    return "invalid/path/to/config/test_invalid_config.toml"


@pytest.fixture(autouse=True)
def valid_config_params() -> Dict[str, Any]:
    _connection_params = {
        CFG_FIELD_MUTE: True,
        CFG_FIELD_DEAFEN: True,
        CFG_FIELD_REGISTER: False,
        CFG_FIELD_COMMENT: "test",
        CFG_FIELD_RECONNECT: False,
        CFG_FIELD_VERBOSE: 0,
    }
    return _connection_params
