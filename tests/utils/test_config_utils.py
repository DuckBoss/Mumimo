import pathlib
from unittest.mock import patch

import pytest

from src.config import ConfigSingleton
from src.constants import DEFAULT_PATH_CONFIG_FILE
from src.exceptions import ConfigReadError
from src.utils import config_utils


class TestConfigUtils:
    def test_initialize_mumimo_config_valid_cfg_path(self, valid_cfg_path: str) -> None:
        ConfigSingleton.clear()
        _cfg_instance = config_utils.initialize_mumimo_config(valid_cfg_path)
        assert _cfg_instance is not None

    def test_initialize_mumimo_config_invalid_cfg_path(self, invalid_cfg_path: str) -> None:
        ConfigSingleton.clear()
        with pytest.raises(ConfigReadError, match=r"^Unable to read config file at:"):
            config_utils.initialize_mumimo_config(invalid_cfg_path)

    def test_initialization_mumimo_config_no_cfg_path_uses_default_path(self) -> None:
        ConfigSingleton.clear()
        _cfg_instance = config_utils.initialize_mumimo_config(None)
        assert _cfg_instance is not None
        assert _cfg_instance._config_file_path == pathlib.Path.cwd() / DEFAULT_PATH_CONFIG_FILE

    @patch.object(ConfigSingleton, "instance")
    def test_initialization_mumimo_config_instance_failed_to_initialize(self, config_instance) -> None:
        config_instance.return_value = None
        with pytest.raises(ConfigReadError, match="^Unexpected error:"):
            config_utils.initialize_mumimo_config(None)
