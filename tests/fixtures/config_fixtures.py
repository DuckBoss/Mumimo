from typing import Any, Dict

import pytest

from src.constants import MUMIMO_CFG_FIELDS


@pytest.fixture(autouse=True)
def valid_cfg_path() -> str:
    return "tests/data/config/test_valid_config.toml"


@pytest.fixture(autouse=True)
def invalid_cfg_path() -> str:
    return "invalid/path/to/config/test_invalid_config.toml"


@pytest.fixture(autouse=True)
def valid_config_params() -> Dict[str, Any]:
    _connection_params = {
        MUMIMO_CFG_FIELDS.SETTINGS.CONNECTION.MUTE: True,
        MUMIMO_CFG_FIELDS.SETTINGS.CONNECTION.DEAFEN: True,
        MUMIMO_CFG_FIELDS.SETTINGS.CONNECTION.REGISTER: False,
        MUMIMO_CFG_FIELDS.SETTINGS.CONNECTION.COMMENT: "test",
        MUMIMO_CFG_FIELDS.SETTINGS.CONNECTION.AUTO_RECONNECT: False,
    }
    return _connection_params
