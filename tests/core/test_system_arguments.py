import pytest

from src.constants import VERBOSITY_MIN
from src.system_arguments import args_parser


class TestSystemArguments:
    @pytest.fixture()
    def sys_args_parser(self):
        return args_parser

    class TestOptionHeadless:
        def test_option_headless(self, sys_args_parser):
            options = ["-hl"]
            parser = sys_args_parser.parse_args(options)
            assert parser.headless is True

        def test_option_no_headless(self, sys_args_parser):
            options = []
            parser = sys_args_parser.parse_args(options)
            assert parser.headless is False

    class TestOptionConfigFile:
        def test_option_valid_config_file(self, sys_args_parser):
            options = ["-cf", "path/to/config"]
            parser = sys_args_parser.parse_args(options)
            assert parser.config_file == "path/to/config"

        def test_option_invalid_config_file_value(self, sys_args_parser):
            options = ["-cf", 99]
            with pytest.raises(TypeError):
                sys_args_parser.parse_args(options)

        def test_option_invalid_config_file_empty(self, sys_args_parser):
            options = ["-cf"]
            with pytest.raises(SystemExit):
                sys_args_parser.parse_args(options)

    class TestOptionHost:
        def test_option_valid_host(self, sys_args_parser):
            options = ["-sh", "127.0.0.1"]
            parser = sys_args_parser.parse_args(options)
            assert parser.host == "127.0.0.1"

        def test_option_invalid_host_value(self, sys_args_parser):
            options = ["-sh", 99]
            with pytest.raises(TypeError):
                sys_args_parser.parse_args(options)

        def test_option_invalid_host_empty(self, sys_args_parser):
            options = ["-sh"]
            with pytest.raises(SystemExit):
                sys_args_parser.parse_args(options)

    class TestOptionPort:
        def test_option_valid_port(self, sys_args_parser):
            # The type is an integer, but the input value is a string.
            # argsparse internally converts it to an integer.
            options = ["-sp", "64738"]
            parser = sys_args_parser.parse_args(options)
            assert parser.port == 64738

        def test_option_invalid_port_value(self, sys_args_parser):
            # The type is an integer, but the input value must be a string.
            options = ["-sp", 64738]
            with pytest.raises(TypeError):
                sys_args_parser.parse_args(options)

        def test_option_invalid_port_empty(self, sys_args_parser):
            options = ["-sp"]
            with pytest.raises(SystemExit):
                sys_args_parser.parse_args(options)

    class TestOptionUser:
        def test_option_valid_user(self, sys_args_parser):
            options = ["-u", "testuser"]
            parser = sys_args_parser.parse_args(options)
            assert parser.user == "testuser"

        def test_option_invalid_user_value(self, sys_args_parser):
            options = ["-u", 99]
            with pytest.raises(TypeError):
                sys_args_parser.parse_args(options)

        def test_option_invalid_user_empty(self, sys_args_parser):
            options = ["-u"]
            with pytest.raises(SystemExit):
                sys_args_parser.parse_args(options)

    class TestOptionPassword:
        def test_option_valid_password(self, sys_args_parser):
            options = ["-p", "testpassword"]
            parser = sys_args_parser.parse_args(options)
            assert parser.password == "testpassword"

        def test_option_invalid_password_value(self, sys_args_parser):
            options = ["-p", 99]
            with pytest.raises(TypeError):
                sys_args_parser.parse_args(options)

        def test_option_invalid_password_empty(self, sys_args_parser):
            options = ["-p"]
            with pytest.raises(SystemExit):
                sys_args_parser.parse_args(options)

    class TestOptionCertFile:
        def test_option_valid_cert_file(self, sys_args_parser):
            options = ["-c", "path/to/cert"]
            parser = sys_args_parser.parse_args(options)
            assert parser.cert_file == "path/to/cert"

        def test_option_invalid_cert_file_value(self, sys_args_parser):
            options = ["-c", 99]
            with pytest.raises(TypeError):
                sys_args_parser.parse_args(options)

        def test_option_invalid_cert_file_empty(self, sys_args_parser):
            options = ["-c"]
            with pytest.raises(SystemExit):
                sys_args_parser.parse_args(options)

    class TestOptionKeyFile:
        def test_option_valid_key_file(self, sys_args_parser):
            options = ["-k", "path/to/key"]
            parser = sys_args_parser.parse_args(options)
            assert parser.key_file == "path/to/key"

        def test_option_invalid_key_file_value(self, sys_args_parser):
            options = ["-k", 99]
            with pytest.raises(TypeError):
                sys_args_parser.parse_args(options)

        def test_option_invalid_key_file_empty(self, sys_args_parser):
            options = ["-k"]
            with pytest.raises(SystemExit):
                sys_args_parser.parse_args(options)

    class TestOptionTokens:
        def test_option_valid_tokens(self, sys_args_parser):
            options = ["-t", "token1 token2"]
            parser = sys_args_parser.parse_args(options)
            assert parser.tokens == "token1 token2"

        def test_option_invalid_tokens_value(self, sys_args_parser):
            options = ["-t", 99]
            with pytest.raises(TypeError):
                sys_args_parser.parse_args(options)

        def test_option_invalid_tokens_empty(self, sys_args_parser):
            options = ["-t"]
            with pytest.raises(SystemExit):
                sys_args_parser.parse_args(options)

    class TestOptionReconnect:
        def test_option_auto_reconnect(self, sys_args_parser):
            options = ["-ar"]
            parser = sys_args_parser.parse_args(options)
            assert parser.auto_reconnect is True

        def test_option_no_auto_reconnect(self, sys_args_parser):
            options = []
            parser = sys_args_parser.parse_args(options)
            assert parser.auto_reconnect is False

    class TestOptionVerbose:
        def test_option_verbose(self, sys_args_parser):
            options = ["-v"]
            parser = sys_args_parser.parse_args(options)
            assert parser.verbose == 1

        def test_option_no_verbose(self, sys_args_parser):
            options = []
            parser = sys_args_parser.parse_args(options)
            assert parser.verbose == VERBOSITY_MIN

    class TestOptionGenerateCert:
        def test_option_generate_cert(self, sys_args_parser):
            options = ["-gc"]
            parser = sys_args_parser.parse_args(options)
            assert parser.generate_cert is True

        def test_option_no_generatecert(self, sys_args_parser):
            options = []
            parser = sys_args_parser.parse_args(options)
            assert parser.generate_cert is False

    class TestOptionSuperUser:
        def test_option_valid_superuser(self, sys_args_parser):
            options = ["-su", "superuser"]
            parser = sys_args_parser.parse_args(options)
            assert parser.superuser == "superuser"

        def test_option_invalid_superuser_value(self, sys_args_parser):
            options = ["-su", 99]
            with pytest.raises(TypeError):
                sys_args_parser.parse_args(options)

        def test_option_invalid_superuser_empty(self, sys_args_parser):
            options = ["-su"]
            with pytest.raises(SystemExit):
                sys_args_parser.parse_args(options)

    class TestOptionEnvFile:
        def test_option_valid_env_file(self, sys_args_parser):
            options = ["-e", "path/to/env"]
            parser = sys_args_parser.parse_args(options)
            assert parser.env_file == "path/to/env"

        def test_option_invalid_superuser_value(self, sys_args_parser):
            options = ["-e", 99]
            with pytest.raises(TypeError):
                sys_args_parser.parse_args(options)

        def test_option_invalid_superuser_empty(self, sys_args_parser):
            options = ["-e"]
            with pytest.raises(SystemExit):
                sys_args_parser.parse_args(options)
