from argparse import ArgumentTypeError
from typing import Dict
from unittest.mock import patch

import pytest

from src.constants import (
    CFG_FIELD_RECONNECT,
    CFG_FIELD_VERBOSE,
    CFG_SECTION_MAIN,
    ENV_CERT,
    ENV_HOST,
    ENV_KEY,
    ENV_PASS,
    ENV_PORT,
    ENV_TOKENS,
    ENV_USER,
    SYS_ENV_FILE,
    SYS_HOST,
    SYS_RECONNECT,
    SYS_TOKENS,
    SYS_VERBOSE,
    VERBOSITY_MAX,
    VERBOSITY_MIN,
)
from src.exceptions import ConfigError
from src.utils import mumimo_utils


class TestSupportedPlatforms:
    @patch("platform.system")
    def test_is_supported_platform_linux(self, mock_platform):
        mock_platform.return_value = "Linux"
        is_supported = mumimo_utils.is_supported_platform()
        assert is_supported is True

    @patch("platform.system")
    def test_is_supported_platform_macos(self, mock_platform):
        mock_platform.return_value = "Darwin"
        is_supported = mumimo_utils.is_supported_platform()
        assert is_supported is True

    @patch("platform.system")
    def test_is_not_supported_platform_windows(self, mock_platform):
        mock_platform.return_value = "Windows"
        is_supported = mumimo_utils.is_supported_platform()
        assert is_supported is False

    @patch("platform.system")
    def test_is_not_supported_platform_java(self, mock_platform):
        mock_platform.return_value = "Java"
        is_supported = mumimo_utils.is_supported_platform()
        assert is_supported is False


class TestVerbosityValidation:
    def test_verbosity_is_valid(self) -> None:
        assert mumimo_utils.validate_verbose_level(str(VERBOSITY_MIN)) == VERBOSITY_MIN

    def test_verbosity_is_none(self) -> None:
        assert mumimo_utils.validate_verbose_level(None) == 0  # type: ignore

    def test_verbosity_is_invalid_string(self) -> None:
        with pytest.raises(ArgumentTypeError, match=r"^The verbose level must be"):
            mumimo_utils.validate_verbose_level("invalid")

    def test_verbosity_is_lower_than_min(self) -> None:
        assert mumimo_utils.validate_verbose_level(str(VERBOSITY_MIN - 999)) == VERBOSITY_MIN

    def test_verbosity_is_higher_than_max(self) -> None:
        assert mumimo_utils.validate_verbose_level(str(VERBOSITY_MAX + 999)) == VERBOSITY_MAX


class TestParseChannelTokens:
    def test_parse_channel_tokens_is_valid(self) -> None:
        assert mumimo_utils.parse_channel_tokens("token1 token2") == ["token1", "token2"]

    def test_parse_channel_tokens_is_none(self) -> None:
        assert mumimo_utils.parse_channel_tokens(None) is None  # type: ignore

    def test_parse_channel_tokens_invalid_values(self) -> None:
        assert mumimo_utils.parse_channel_tokens(5) is None  # type: ignore

    def test_parse_channel_tokens_extra_spaces(self) -> None:
        assert mumimo_utils.parse_channel_tokens(" token1   token2  ") == ["token1", "token2"]

    def test_parse_channel_tokens_empty(self) -> None:
        assert mumimo_utils.parse_channel_tokens("") is None

    def test_parse_channel_tokens_spaces(self) -> None:
        assert mumimo_utils.parse_channel_tokens("  ") is None


class TestClientSettingsInitialization:
    class TestSysArgsAndConfigPriorityConsolidation:
        def test_get_prioritized_client_config_options_sys_args_verbose_priority(self, cfg_instance):
            sys_args = {SYS_VERBOSE: 2}
            cfg_instance[CFG_SECTION_MAIN] = {CFG_FIELD_VERBOSE: 0}

            _prioritized_options = mumimo_utils.get_prioritized_client_config_options(sys_args, cfg_instance)
            assert _prioritized_options[CFG_SECTION_MAIN][CFG_FIELD_VERBOSE] == 2

        def test_get_prioritized_client_config_options_sys_args_reconnect_priority(self, cfg_instance):
            sys_args = {SYS_RECONNECT: True}
            cfg_instance[CFG_SECTION_MAIN] = {CFG_FIELD_RECONNECT: False}

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
    def test_initialize_client_settings_config_instance_failed(self, init_cfg_mock) -> None:
        init_cfg_mock.return_value = None
        with pytest.raises(ConfigError, match=r"^An unexpected error occurred"):
            mumimo_utils.initialize_client_settings({})

    def test_initialize_client_settings_sys_args_verbose_below_min(self) -> None:
        sys_args = {SYS_VERBOSE: str(VERBOSITY_MIN - 1)}
        with patch("src.utils.config_utils.initialize_mumimo_config"):
            assert mumimo_utils.initialize_client_settings(sys_args) is not None

    def test_initialize_client_settings_sys_args_verbose_above_max(self) -> None:
        sys_args = {SYS_VERBOSE: str(VERBOSITY_MAX + 1)}
        with patch("src.utils.config_utils.initialize_mumimo_config"):
            assert mumimo_utils.initialize_client_settings(sys_args) is not None

    def test_initialize_client_settings_sys_args_invalid_verbose(self) -> None:
        sys_args = {SYS_VERBOSE: "invalid_verbose_level"}
        with patch("src.utils.config_utils.initialize_mumimo_config"):
            with pytest.raises(ArgumentTypeError, match=r"^The verbose level must be"):
                mumimo_utils.initialize_client_settings(sys_args)
