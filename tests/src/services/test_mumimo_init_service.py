from unittest.mock import patch

import pytest

from src.constants import VERBOSITY_MAX, EnvArgs, MumimoCfgFields, SysArgs
from src.exceptions import ConfigError
from src.services.mumimo_init_service import MumimoInitService
from src.utils import config_utils
from src.utils.config_utils import initialize_mumimo_config


class TestMumimoInitService:
    @pytest.fixture(autouse=True)
    def get_init_service(self):
        yield MumimoInitService({})

    def test__get_sys_args(self, get_init_service) -> None:
        init_service: MumimoInitService = get_init_service
        init_service._sys_args = {"test": "test"}
        assert init_service._get_sys_args() == {"test": "test"}

    class TestInitializeConfig:
        @patch.object(config_utils, "initialize_mumimo_config")
        def test_initialize_config(self, mumimo_cfg_mock, get_init_service) -> None:
            init_service: MumimoInitService = get_init_service
            mumimo_cfg_mock.return_value = {}
            assert init_service.initialize_config() == {}

        @patch.object(config_utils, "initialize_mumimo_config")
        def test_initialize_config_failed(self, mumimo_cfg_mock, get_init_service) -> None:
            init_service: MumimoInitService = get_init_service
            mumimo_cfg_mock.return_value = None
            with pytest.raises(ConfigError, match="^An unexpected error"):
                init_service.initialize_config()

    class TestInitializeClientSettings:
        @pytest.fixture(autouse=True)
        def get_expected_prioritized_client_opts(self):
            return {
                SysArgs.SYS_RECONNECT: True,
            }

        @pytest.fixture(autouse=True)
        def get_expected_prioritized_env_opts(self):
            return {
                SysArgs.SYS_HOST: "host",
                SysArgs.SYS_PORT: 12345,
                SysArgs.SYS_USER: "user",
                SysArgs.SYS_PASS: "pass",
                SysArgs.SYS_CERT: "cert",
                SysArgs.SYS_KEY: "key",
                SysArgs.SYS_TOKENS: "tokens",
                SysArgs.SYS_SUPER_USER: "super",
            }

        @patch("src.services.mumimo_init_service.MumimoInitService._get_prioritized_client_config_options")
        @patch("src.services.mumimo_init_service.MumimoInitService._get_prioritized_client_env_options")
        @patch("src.services.mumimo_init_service.MumimoInitService._get_sys_args")
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
        ) -> None:
            init_service: MumimoInitService = get_init_service
            mock_init_mumimo_cfg.return_value = initialize_mumimo_config()
            if mock_init_mumimo_cfg.return_value is None:
                pytest.fail("mock config failed to be created.")

            # mock_init_mumimo_cfg.return_value.set(f"{CFG_SECTION.SETTINGS.CONNECTION}.{CFG_FIELD.SETTINGS.CONNECTION.AUTO_RECONNECT}", True)
            mock_sys_args.return_value = {SysArgs.SYS_VERBOSE: VERBOSITY_MAX}
            mock_env_opts.return_value = get_expected_prioritized_env_opts
            mock_config_opts.return_value = get_expected_prioritized_client_opts
            _ = init_service.initialize_client_settings(mock_init_mumimo_cfg.return_value)
            # client_settings["auto_reconnect"] = True

            expected_connection_opts = {
                **mock_config_opts.return_value,
                **mock_env_opts.return_value,
                **mock_sys_args.return_value,
            }
            assert expected_connection_opts is not None

    class TestGetPrioritizedOptions:
        def test_get_prioritized_cfg_options_empty(self, get_init_service) -> None:
            init_service: MumimoInitService = get_init_service
            init_service._prioritized_cfg_opts = {}
            assert init_service.get_prioritized_cfg_options() == {}

        def test_get_prioritized_cfg_options(self, get_init_service) -> None:
            init_service: MumimoInitService = get_init_service
            init_service._prioritized_cfg_opts = {"test": "test"}
            assert init_service.get_prioritized_cfg_options() == {"test": "test"}

        def test_get_prioritized_env_options_empty(self, get_init_service) -> None:
            init_service: MumimoInitService = get_init_service
            init_service._prioritized_env_opts = {}
            assert init_service.get_prioritized_env_options() == {}

        def test_get_prioritized_env_options(self, get_init_service) -> None:
            init_service: MumimoInitService = get_init_service
            init_service._prioritized_env_opts = {"test": "test"}
            assert init_service.get_prioritized_env_options() == {"test": "test"}

    class TestGetConnectionParameters:
        @patch("src.services.mumimo_init_service.MumimoInitService.get_prioritized_cfg_options")
        @patch("src.services.mumimo_init_service.MumimoInitService.get_prioritized_env_options")
        def test_get_connection_parameters_prioritized_options_are_none(self, mock_env_opts, mock_cfg_opts, get_init_service) -> None:
            mock_env_opts.return_value = {}
            mock_cfg_opts.return_value = {}
            init_service: MumimoInitService = get_init_service
            assert init_service.get_connection_parameters() == {}

        @patch("src.services.mumimo_init_service.MumimoInitService._get_sys_args")
        @patch("src.services.mumimo_init_service.MumimoInitService.get_prioritized_cfg_options")
        @patch("src.services.mumimo_init_service.MumimoInitService.get_prioritized_env_options")
        def test_get_connection_parameters_prioritized_options(self, mock_env_opts, mock_cfg_opts, mock_sys_args, get_init_service) -> None:
            mock_env_opts.return_value = {
                SysArgs.SYS_HOST: "host",
                SysArgs.SYS_PORT: 12345,
                SysArgs.SYS_USER: "mumimo",
                SysArgs.SYS_PASS: "pass",
                SysArgs.SYS_SUPER_USER: "superuser",
                SysArgs.SYS_CERT: "cert",
                SysArgs.SYS_TOKENS: "token1 token2",
                SysArgs.SYS_KEY: "key",
            }
            mock_sys_args.return_value = {
                SysArgs.SYS_VERBOSE: 0,
            }
            mock_cfg_opts.return_value = {
                SysArgs.SYS_RECONNECT: True,
            }
            init_service: MumimoInitService = get_init_service
            assert init_service.get_connection_parameters() == {
                SysArgs.SYS_HOST: "host",
                SysArgs.SYS_PORT: 12345,
                SysArgs.SYS_USER: "mumimo",
                SysArgs.SYS_PASS: "pass",
                SysArgs.SYS_SUPER_USER: "superuser",
                SysArgs.SYS_CERT: "cert",
                SysArgs.SYS_TOKENS: "token1 token2",
                SysArgs.SYS_KEY: "key",
                SysArgs.SYS_RECONNECT: True,
                SysArgs.SYS_VERBOSE: 0,
            }

    class TestPrioritizedOptions:
        @pytest.fixture(autouse=True)
        def get_expected_env_mock_sys_args(self):
            return {
                SysArgs.SYS_HOST: "host",
                SysArgs.SYS_PORT: 12345,
                SysArgs.SYS_USER: "mumimo",
                SysArgs.SYS_PASS: "pass",
                SysArgs.SYS_SUPER_USER: "superuser",
                SysArgs.SYS_CERT: "cert",
                SysArgs.SYS_TOKENS: "token1 token2",
                SysArgs.SYS_KEY: "key",
                SysArgs.SYS_DB_DIALECT: "sqlite",
                SysArgs.SYS_DB_DRIVER: "aiosqlite",
                SysArgs.SYS_DB_USER: "mumimo",
                SysArgs.SYS_DB_PASS: "pass",
                SysArgs.SYS_DB_HOST: "mumimo_db",
                SysArgs.SYS_DB_NAME: "mumimo",
                SysArgs.SYS_DB_QUERY: "mumimo_query",
            }

        @pytest.fixture(autouse=True)
        def get_expected_env_mock_no_sys_args(self):
            return {
                EnvArgs.ENV_HOST: "test_host",
                EnvArgs.ENV_PORT: 12345,
                EnvArgs.ENV_USER: "test_user",
                EnvArgs.ENV_PASS: "test_pass",
                EnvArgs.ENV_SUPER_USER: "test_super_user",
                EnvArgs.ENV_CERT: "test_cert",
                EnvArgs.ENV_TOKENS: ["test_token_1", "test_token_2"],
                EnvArgs.ENV_KEY: "test_key",
                EnvArgs.ENV_DB_DIALECT: "sqlite",
                EnvArgs.ENV_DB_DRIVER: "aiosqlite",
                EnvArgs.ENV_DB_USER: "test_mumimo",
                EnvArgs.ENV_DB_PASS: "test_mumimo",
                EnvArgs.ENV_DB_HOST: "test_mumimo_db",
                EnvArgs.ENV_DB_NAME: "test_mumimo",
                EnvArgs.ENV_DB_QUERY: "test_mumimo_query",
            }

        @patch.object(config_utils, "initialize_mumimo_config")
        @patch.object(MumimoInitService, "_get_sys_args")
        def test__get_prioritized_client_config_options_with_sys_args(self, mock_sys_args, mock_init_mumimo_cfg, get_init_service) -> None:
            init_service: MumimoInitService = get_init_service
            mock_init_mumimo_cfg.return_value = initialize_mumimo_config()
            mock_sys_args.return_value = {SysArgs.SYS_RECONNECT: True}
            client_settings = init_service._get_prioritized_client_config_options(mock_init_mumimo_cfg)
            assert client_settings == {SysArgs.SYS_RECONNECT: True}

        @patch.object(MumimoInitService, "_get_sys_args")
        def test__get_prioritized_client_config_options_without_sys_args(self, mock_sys_args, get_init_service) -> None:
            init_service: MumimoInitService = get_init_service
            mock_cfg = initialize_mumimo_config()
            mock_sys_args.return_value = {}
            if mock_cfg is not None:
                mock_cfg.set(MumimoCfgFields.SETTINGS.CONNECTION.AUTO_RECONNECT, True)
                client_settings = init_service._get_prioritized_client_config_options(mock_cfg)
                assert client_settings[SysArgs.SYS_RECONNECT] is False

        @patch.object(MumimoInitService, "_get_sys_args")
        @patch("src.utils.parsers.env_parser.read_env_file")
        def test__get_prioritized_client_env_options_with_sys_args(
            self, mock_env_args, mock_sys_args, get_init_service, get_expected_env_mock_sys_args
        ) -> None:
            init_service: MumimoInitService = get_init_service
            mock_env_args.return_value = {}
            mock_sys_args.return_value = get_expected_env_mock_sys_args
            client_settings = init_service._get_prioritized_client_env_options()
            assert client_settings == {
                SysArgs.SYS_HOST: mock_sys_args.return_value[SysArgs.SYS_HOST],
                SysArgs.SYS_PORT: mock_sys_args.return_value[SysArgs.SYS_PORT],
                SysArgs.SYS_USER: mock_sys_args.return_value[SysArgs.SYS_USER],
                SysArgs.SYS_PASS: mock_sys_args.return_value[SysArgs.SYS_PASS],
                SysArgs.SYS_SUPER_USER: mock_sys_args.return_value[SysArgs.SYS_SUPER_USER],
                SysArgs.SYS_CERT: mock_sys_args.return_value[SysArgs.SYS_CERT],
                SysArgs.SYS_TOKENS: ["token1", "token2"],
                SysArgs.SYS_KEY: mock_sys_args.return_value[SysArgs.SYS_KEY],
                SysArgs.SYS_DB_DIALECT: mock_sys_args.return_value[SysArgs.SYS_DB_DIALECT],
                SysArgs.SYS_DB_DRIVER: mock_sys_args.return_value[SysArgs.SYS_DB_DRIVER],
                SysArgs.SYS_DB_USER: mock_sys_args.return_value[SysArgs.SYS_DB_USER],
                SysArgs.SYS_DB_PASS: mock_sys_args.return_value[SysArgs.SYS_DB_PASS],
                SysArgs.SYS_DB_HOST: mock_sys_args.return_value[SysArgs.SYS_DB_HOST],
                SysArgs.SYS_DB_NAME: mock_sys_args.return_value[SysArgs.SYS_DB_NAME],
                SysArgs.SYS_DB_QUERY: mock_sys_args.return_value[SysArgs.SYS_DB_QUERY],
            }

        @patch.object(MumimoInitService, "_get_sys_args")
        @patch("src.utils.parsers.env_parser.read_env_file")
        def test__get_prioritized_client_env_options_without_sys_args(
            self, mock_env_args, mock_sys_args, get_init_service, get_expected_env_mock_no_sys_args
        ) -> None:
            init_service: MumimoInitService = get_init_service
            mock_env_args.return_value = get_expected_env_mock_no_sys_args
            mock_sys_args.return_value = {SysArgs.SYS_ENV_FILE: "data/test.env"}
            client_settings = init_service._get_prioritized_client_env_options()
            assert client_settings == {
                SysArgs.SYS_HOST: mock_env_args.return_value[EnvArgs.ENV_HOST],
                SysArgs.SYS_PORT: mock_env_args.return_value[EnvArgs.ENV_PORT],
                SysArgs.SYS_USER: mock_env_args.return_value[EnvArgs.ENV_USER],
                SysArgs.SYS_PASS: mock_env_args.return_value[EnvArgs.ENV_PASS],
                SysArgs.SYS_SUPER_USER: mock_env_args.return_value[EnvArgs.ENV_SUPER_USER],
                SysArgs.SYS_CERT: mock_env_args.return_value[EnvArgs.ENV_CERT],
                SysArgs.SYS_TOKENS: mock_env_args.return_value[EnvArgs.ENV_TOKENS],
                SysArgs.SYS_KEY: mock_env_args.return_value[EnvArgs.ENV_KEY],
                SysArgs.SYS_DB_DIALECT: mock_env_args.return_value[EnvArgs.ENV_DB_DIALECT],
                SysArgs.SYS_DB_DRIVER: mock_env_args.return_value[EnvArgs.ENV_DB_DRIVER],
                SysArgs.SYS_DB_USER: mock_env_args.return_value[EnvArgs.ENV_DB_USER],
                SysArgs.SYS_DB_PASS: mock_env_args.return_value[EnvArgs.ENV_DB_PASS],
                SysArgs.SYS_DB_HOST: mock_env_args.return_value[EnvArgs.ENV_DB_HOST],
                SysArgs.SYS_DB_NAME: mock_env_args.return_value[EnvArgs.ENV_DB_NAME],
                SysArgs.SYS_DB_QUERY: mock_env_args.return_value[EnvArgs.ENV_DB_QUERY],
            }
