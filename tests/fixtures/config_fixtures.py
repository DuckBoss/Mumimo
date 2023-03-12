from typing import Any, Dict

import pytest

from src.constants import MumimoCfgFields


@pytest.fixture(autouse=True)
def valid_config_params() -> Dict[str, Any]:
    _connection_params = {
        MumimoCfgFields.SETTINGS.CONNECTION.MUTE: True,
        MumimoCfgFields.SETTINGS.CONNECTION.DEAFEN: True,
        MumimoCfgFields.SETTINGS.CONNECTION.REGISTER: False,
        MumimoCfgFields.SETTINGS.CONNECTION.COMMENT: "test",
        MumimoCfgFields.SETTINGS.CONNECTION.AUTO_RECONNECT: False,
    }
    return _connection_params
