from unittest.mock import patch

import pytest
from src.config import ConfigSingleton

from src.constants import (
    MUMIMO_CFG_FIELDS,
    ENV_ARGS,
    SYS_ARGS,
    VERBOSITY_MAX,
)
from src.exceptions import ConfigError
from src.utils import config_utils
from src.services.init_service import MumimoInitService


class TestMumimoInitService:
    @pytest.fixture(autouse=True)
    def get_init_service(self):
        yield MumimoInitService({})

    def test__get_sys_args(self, get_init_service):
        init_service: MumimoInitService = get_init_service
        init_service._sys_args = {"test": "test"}
        assert init_service._get_sys_args() == {"test": "test"}

    class TestInitializeConfig:
        @patch.object(config_utils, "initialize_mumimo_config")
        def test_initialize_config(self, mumimo_cfg_mock, get_init_service):
            init_service: MumimoInitService = get_init_service
            mumimo_cfg_mock.return_value = {}
            assert init_service.initialize_config() == {}

        @patch.object(config_utils, "initialize_mumimo_config")
        def test_initialize_config_failed(self, mumimo_cfg_mock, get_init_service):
            init_service: MumimoInitService = get_init_service
            mumimo_cfg_mock.return_value = None
            with pytest.raises(ConfigError, match="^An unexpected error"):
                init_service.initialize_config()

    class TestInitializeClientSettings:
        @pytest.fixture(autouse=True)
        def get_expected_prioritized_client_opts(self):
            return {
                SYS_ARGS.SYS_RECONNECT: True,
            }

        @pytest.fixture(autouse=True)
        def get_expected_prioritized_env_opts(self):
            return {
                SYS_ARGS.SYS_HOST: "host",
                SYS_ARGS.SYS_PORT: 12345,
                SYS_ARGS.SYS_USER: "user",
                SYS_ARGS.SYS_PASS: "pass",
                SYS_ARGS.SYS_CERT: "cert",
                SYS_ARGS.SYS_KEY: "key",
                SYS_ARGS.SYS_TOKENS: "tokens",
                SYS_ARGS.SYS_SUPER_USER: "super",
            }

        @patch("src.services.init_service.MumimoInitService._get_prioritized_client_config_options")
        @patch("src.services.init_service.MumimoInitService._get_prioritized_client_env_options")
        @patch("src.services.init_service.MumimoInitService._get_sys_args")
        @patch.object(config_utils, "initialize_mumimo_config")
        def test_initialize_client_settings(
            self,
            mock_init_mumimo_cfg,
            mock_sys_args,
            mock_env_opts,
            mock_config_opts,
            get_init_service,
            get_expected_prioritized_env_opts,
            get_expected_prioritized_client_opts,
        ):
            ConfigSingleton.clear()
            init_service: MumimoInitService = get_init_service
            mock_init_mumimo_cfg.return_value = ConfigSingleton().instance()
            if mock_init_mumimo_cfg.return_value is None:
                pytest.fail("mock config failed to be created.")

            # mock_init_mumimo_cfg.return_value.set(f"{CFG_SECTION.SETTINGS.CONNECTION}.{CFG_FIELD.SETTINGS.CONNECTION.AUTO_RECONNECT}", True)
            mock_sys_args.return_value = {SYS_ARGS.SYS_VERBOSE: VERBOSITY_MAX}
            mock_env_opts.return_value = get_expected_prioritized_env_opts
            mock_config_opts.return_value = get_expected_prioritized_client_opts
            client_settings = init_service.initialize_client_settings(mock_init_mumimo_cfg.return_value)
            # client_settings["auto_reconnect"] = True

            expected_connection_opts = {
                **mock_config_opts.return_value,
                **mock_env_opts.return_value,
                **mock_sys_args.return_value,
            }
            assert client_settings == expected_connection_opts

    class TestPrioritizedOptions:
        @pytest.fixture(autouse=True)
        def get_expected_env_mock_sys_args(self):
            return {
                SYS_ARGS.SYS_HOST: "host",
                SYS_ARGS.SYS_PORT: 12345,
                SYS_ARGS.SYS_USER: "mumimo",
                SYS_ARGS.SYS_PASS: "pass",
                SYS_ARGS.SYS_SUPER_USER: "superuser",
                SYS_ARGS.SYS_CERT: "cert",
                SYS_ARGS.SYS_TOKENS: "token1 token2",
                SYS_ARGS.SYS_KEY: "key",
            }

        @pytest.fixture(autouse=True)
        def get_expected_env_mock_no_sys_args(self):
            return {
                ENV_ARGS.ENV_HOST: "test_host",
                ENV_ARGS.ENV_PORT: 12345,
                ENV_ARGS.ENV_USER: "test_user",
                ENV_ARGS.ENV_PASS: "test_pass",
                ENV_ARGS.ENV_SUPER_USER: "test_super_user",
                ENV_ARGS.ENV_CERT: "test_cert",
                ENV_ARGS.ENV_TOKENS: ["test_token_1", "test_token_2"],
                ENV_ARGS.ENV_KEY: "test_key",
            }

        @patch.object(config_utils, "initialize_mumimo_config")
        @patch.object(MumimoInitService, "_get_sys_args")
        def test__get_prioritized_client_config_options_with_sys_args(self, mock_sys_args, mock_init_mumimo_cfg, get_init_service):
            ConfigSingleton.clear()
            init_service: MumimoInitService = get_init_service
            mock_init_mumimo_cfg.return_value = ConfigSingleton().instance()
            mock_sys_args.return_value = {SYS_ARGS.SYS_RECONNECT: True}
            client_settings = init_service._get_prioritized_client_config_options(mock_init_mumimo_cfg)
            assert client_settings == {SYS_ARGS.SYS_RECONNECT: True}

        @patch.object(MumimoInitService, "_get_sys_args")
        def test__get_prioritized_client_config_options_without_sys_args(self, mock_sys_args, get_init_service):
            ConfigSingleton.clear()
            init_service: MumimoInitService = get_init_service
            mock_cfg = ConfigSingleton().instance()
            mock_sys_args.return_value = {}
            if mock_cfg is not None:
                mock_cfg.set(MUMIMO_CFG_FIELDS.SETTINGS.CONNECTION.AUTO_RECONNECT, True)
                client_settings = init_service._get_prioritized_client_config_options(mock_cfg)
                assert client_settings[SYS_ARGS.SYS_RECONNECT] is False

        @patch.object(MumimoInitService, "_get_sys_args")
        @patch("src.utils.env_parser.read_env_file")
        def test__get_prioritized_client_env_options_with_sys_args(
            self, mock_env_args, mock_sys_args, get_init_service, get_expected_env_mock_sys_args
        ):
            ConfigSingleton.clear()
            init_service: MumimoInitService = get_init_service
            mock_env_args.return_value = {}
            mock_sys_args.return_value = get_expected_env_mock_sys_args
            client_settings = init_service._get_prioritized_client_env_options()
            assert client_settings == {
                SYS_ARGS.SYS_HOST: mock_sys_args.return_value[SYS_ARGS.SYS_HOST],
                SYS_ARGS.SYS_PORT: mock_sys_args.return_value[SYS_ARGS.SYS_PORT],
                SYS_ARGS.SYS_USER: mock_sys_args.return_value[SYS_ARGS.SYS_USER],
                SYS_ARGS.SYS_PASS: mock_sys_args.return_value[SYS_ARGS.SYS_PASS],
                SYS_ARGS.SYS_SUPER_USER: mock_sys_args.return_value[SYS_ARGS.SYS_SUPER_USER],
                SYS_ARGS.SYS_CERT: mock_sys_args.return_value[SYS_ARGS.SYS_CERT],
                SYS_ARGS.SYS_TOKENS: ["token1", "token2"],
                SYS_ARGS.SYS_KEY: mock_sys_args.return_value[SYS_ARGS.SYS_KEY],
            }

        @patch.object(MumimoInitService, "_get_sys_args")
        @patch("src.utils.env_parser.read_env_file")
        def test__get_prioritized_client_env_options_without_sys_args(
            self, mock_env_args, mock_sys_args, get_init_service, get_expected_env_mock_no_sys_args
        ):
            ConfigSingleton.clear()
            init_service: MumimoInitService = get_init_service
            mock_env_args.return_value = get_expected_env_mock_no_sys_args
            mock_sys_args.return_value = {SYS_ARGS.SYS_ENV_FILE: "data/test.env"}
            client_settings = init_service._get_prioritized_client_env_options()
            assert client_settings == {
                SYS_ARGS.SYS_HOST: mock_env_args.return_value[ENV_ARGS.ENV_HOST],
                SYS_ARGS.SYS_PORT: mock_env_args.return_value[ENV_ARGS.ENV_PORT],
                SYS_ARGS.SYS_USER: mock_env_args.return_value[ENV_ARGS.ENV_USER],
                SYS_ARGS.SYS_PASS: mock_env_args.return_value[ENV_ARGS.ENV_PASS],
                SYS_ARGS.SYS_SUPER_USER: mock_env_args.return_value[ENV_ARGS.ENV_SUPER_USER],
                SYS_ARGS.SYS_CERT: mock_env_args.return_value[ENV_ARGS.ENV_CERT],
                SYS_ARGS.SYS_TOKENS: mock_env_args.return_value[ENV_ARGS.ENV_TOKENS],
                SYS_ARGS.SYS_KEY: mock_env_args.return_value[ENV_ARGS.ENV_KEY],
            }
