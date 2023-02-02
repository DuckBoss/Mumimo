from argparse import ArgumentTypeError
from typing import Dict
from unittest.mock import patch

import pytest

from src.constants import (
    CFG_SECTION,
    CFG_FIELD,
    SYS_ARGS,
    VERBOSITY_MAX,
    VERBOSITY_MIN,
)
from src.exceptions import ConfigError
from src.utils import mumimo_utils
from src.services.init_service import MumimoInitService


class TestClientSettingsInitialization:
    @pytest.fixture(autouse=True)
    def get_init_service(self):
        return MumimoInitService({})

    class TestSysArgsAndConfigPriorityConsolidation:
        def test_get_prioritized_client_config_options_sys_args_reconnect_priority(self, cfg_instance):
            sys_args = {SYS_ARGS.SYS_RECONNECT: True}
            cfg_instance[CFG_SECTION.SETTINGS.CONNECTION] = {CFG_FIELD.SETTINGS.CONNECTION.AUTO_RECONNECT: False}

            _prioritized_options = mumimo_utils.get_prioritized_client_config_options(sys_args, cfg_instance)
            assert _prioritized_options[CFG_SECTION_MAIN][CFG_FIELD_RECONNECT] is True

        def test_get_prioritized_client_config_options_cfg_verbose_priority(self, cfg_instance):
            sys_args = {}
            cfg_instance[CFG_SECTION_MAIN] = {CFG_FIELD_VERBOSE: 1}

            _prioritized_options = mumimo_utils.get_prioritized_client_config_options(sys_args, cfg_instance)
            assert _prioritized_options[CFG_SECTION_MAIN][CFG_FIELD_VERBOSE] == 1

        def test_get_prioritized_client_config_options_cfg_reconnect_priority(self, cfg_instance):
            sys_args = {}
            cfg_instance[CFG_SECTION_MAIN] = {CFG_FIELD_RECONNECT: True}

            _prioritized_options = mumimo_utils.get_prioritized_client_config_options(sys_args, cfg_instance)
            assert _prioritized_options[CFG_SECTION_MAIN][CFG_FIELD_RECONNECT] is True

    class TestSysArgsAndEnvPriorityConsolidation:
        @pytest.fixture(autouse=True)
        def env_data(self) -> Dict[str, str]:
            return {
                ENV_HOST: "127.0.0.1",
                ENV_PORT: "64738",
                ENV_USER: "test",
                ENV_PASS: "test",
                ENV_CERT: "path/to/cert",
                ENV_KEY: "path/to/key",
                ENV_TOKENS: "token3 token4",
            }

        def test_get_prioritized_client_env_options_not_used(self, valid_connection_params):
            valid_connection_params[SYS_ENV_FILE] = None

            _prioritized_env_data = mumimo_utils.get_prioritized_client_env_options(valid_connection_params)
            assert _prioritized_env_data[SYS_HOST] == "127.0.0.1"

        @patch("src.utils.env_parser.read_env_file")
        def test_get_prioritized_client_env_options_sys_args_tokens_priority(self, mock_env_data, valid_connection_params, env_data):
            valid_connection_params[SYS_TOKENS] = "token1 token2"
            mock_env_data.return_value = env_data

            _prioritized_env_data = mumimo_utils.get_prioritized_client_env_options(valid_connection_params)
            assert _prioritized_env_data[SYS_TOKENS] == ["token1", "token2"]

        @patch("src.utils.env_parser.read_env_file")
        def test_get_prioritized_client_env_options_sys_args_connection_options_priority(self, mock_env_data, valid_connection_params, env_data):
            del valid_connection_params[SYS_RECONNECT]
            del valid_connection_params[SYS_VERBOSE]
            mock_env_data.return_value = env_data

            _prioritized_env_data = mumimo_utils.get_prioritized_client_env_options(valid_connection_params)
            valid_connection_params[SYS_TOKENS] = valid_connection_params[SYS_TOKENS].split(" ")
            assert _prioritized_env_data == valid_connection_params

        @patch("src.utils.env_parser.read_env_file")
        def test_get_prioritized_client_env_options_env_tokens_priority(self, mock_env_data, valid_connection_params, env_data):
            del valid_connection_params[SYS_TOKENS]
            valid_connection_params[SYS_ENV_FILE] = "mocked_data"
            mock_env_data.return_value = env_data

            _prioritized_env_data = mumimo_utils.get_prioritized_client_env_options(valid_connection_params)
            assert _prioritized_env_data[SYS_TOKENS] == ["token3", "token4"]

        @patch("src.utils.env_parser.read_env_file")
        def test_get_prioritized_client_env_options_env_connection_options_priority(self, mock_env_data, valid_connection_params, env_data):
            valid_connection_params[SYS_ENV_FILE] = "mocked_data"
            mock_env_data.return_value = env_data

            _prioritized_env_data = mumimo_utils.get_prioritized_client_env_options(valid_connection_params)
            del valid_connection_params[SYS_ENV_FILE]
            del valid_connection_params[SYS_RECONNECT]
            del valid_connection_params[SYS_VERBOSE]
            valid_connection_params[SYS_TOKENS] = valid_connection_params[SYS_TOKENS].split(" ")

            assert _prioritized_env_data == valid_connection_params

    @patch("src.utils.config_utils.initialize_mumimo_config")
    def test_initialize_config_instance_failed(self, init_cfg_mock) -> None:
        init_cfg_mock.return_value = None
        with pytest.raises(ConfigError, match=r"^An unexpected error occurred"):
            mumimo_utils.initialize_config({})

    def test_get_prioritized_client_verbosity_level_verbose_below_min(self) -> None:
        sys_args = {SYS_VERBOSE: str(VERBOSITY_MIN - 1)}
        with patch("src.utils.mumimo_utils.initialize_config") as x:
            assert mumimo_utils.get_prioritized_client_verbosity_level(sys_args, x) is not None

    def test_get_prioritized_client_verbosity_level_verbose_above_max(self) -> None:
        sys_args = {SYS_VERBOSE: str(VERBOSITY_MAX + 1)}
        with patch("src.utils.mumimo_utils.initialize_config") as x:
            assert mumimo_utils.get_prioritized_client_verbosity_level(sys_args, x) is not None

    def test_get_prioritized_client_verbosity_level_invalid_verbose(self) -> None:
        sys_args = {SYS_VERBOSE: "invalid_verbose_level"}
        with patch("src.utils.mumimo_utils.initialize_config") as x:
            with pytest.raises(ArgumentTypeError, match=r"^The verbose level must be"):
                mumimo_utils.get_prioritized_client_verbosity_level(sys_args, x)
