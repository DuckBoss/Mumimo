from typing import Any, Dict

import pytest

from src.constants import CFG_FIELD


@pytest.fixture(autouse=True)
def valid_cfg_path() -> str:
    return "tests/data/config/test_valid_config.toml"


@pytest.fixture(autouse=True)
def invalid_cfg_path() -> str:
    return "invalid/path/to/config/test_invalid_config.toml"


@pytest.fixture(autouse=True)
def valid_config_params() -> Dict[str, Any]:
    _connection_params = {
        CFG_FIELD.SETTINGS.CONNECTION.MUTE: True,
        CFG_FIELD.SETTINGS.CONNECTION.DEAFEN: True,
        CFG_FIELD.SETTINGS.CONNECTION.REGISTER: False,
        CFG_FIELD.SETTINGS.CONNECTION.COMMENT: "test",
        CFG_FIELD.SETTINGS.CONNECTION.AUTO_RECONNECT: False,
    }
    return _connection_params
