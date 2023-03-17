from typing import Dict, Union

import pytest

from src.constants import SysArgs
from src.exceptions import ValidationError
from src.utils.args_validators import SystemArgumentsValidator as validator


class TestSystemArgumentsValidators:
    @pytest.fixture(autouse=True)
    def sys_args(self) -> Dict[str, Union[str, bool, None]]:
        return {
            "host": "",
            "port": "",
            "user": "",
            "password": "",
            "cert_file": "",
            "key_file": "",
            "tokens": "",
            "auto_reconnect": "",
            "verbose": "",
        }

    @pytest.fixture(autouse=True)
    def host(self, sys_args):
        yield sys_args[SysArgs.SYS_HOST]
        sys_args[SysArgs.SYS_HOST] = ""

    @pytest.fixture(autouse=True)
    def port(self, sys_args):
        yield sys_args[SysArgs.SYS_PORT]
        sys_args[SysArgs.SYS_PORT] = ""

    @pytest.fixture(autouse=True)
    def user(self, sys_args):
        yield sys_args[SysArgs.SYS_USER]
        sys_args[SysArgs.SYS_USER] = ""

    @pytest.fixture(autouse=True)
    def password(self, sys_args):
        yield sys_args[SysArgs.SYS_PASS]
        sys_args[SysArgs.SYS_PASS] = ""

    @pytest.fixture(autouse=True)
    def cert(self, sys_args):
        yield sys_args[SysArgs.SYS_CERT]
        sys_args[SysArgs.SYS_CERT] = ""

    @pytest.fixture(autouse=True)
    def key(self, sys_args):
        yield sys_args[SysArgs.SYS_KEY]
        sys_args[SysArgs.SYS_KEY] = ""

    @pytest.fixture(autouse=True)
    def tokens(self, sys_args):
        yield sys_args[SysArgs.SYS_TOKENS]
        sys_args[SysArgs.SYS_TOKENS] = ""

    @pytest.fixture(autouse=True)
    def reconnect(self, sys_args):
        yield sys_args[SysArgs.SYS_RECONNECT]
        sys_args[SysArgs.SYS_RECONNECT] = ""

    @pytest.fixture(autouse=True)
    def verbose(self, sys_args):
        yield sys_args[SysArgs.SYS_VERBOSE]
        sys_args[SysArgs.SYS_VERBOSE] = ""

    class TestHostParam:
        def test_host_is_none(self, host) -> None:
            host = None
            with pytest.raises(ValidationError, match=r".*\ must be provided.$"):
                validator.validate_host_param(host)  # type: ignore

        def test_host_is_empty(self, host) -> None:
            host = ""
            with pytest.raises(ValidationError, match=r".*\ cannot be empty.$"):
                validator.validate_host_param(host)

        def test_host_is_invalid(self, host) -> None:
            host = "invalid_host"
            with pytest.raises(ValidationError, match=r".*\ is not a valid host ip or url.$"):
                validator.validate_host_param(host)

        def test_host_is_valid_ipv4(self, host) -> None:
            host = "127.0.0.1"
            assert validator.validate_host_param(host) is None

        def test_host_is_invalid_ipv4(self, host) -> None:
            host = "127.0.0133.12"
            with pytest.raises(ValidationError, match=r".*\ is not a valid host ip or url.$"):
                validator.validate_host_param(host)

        def test_host_is_valid_ipv6(self, host) -> None:
            host = "0:0:0:0:0:0:0:1"
            assert validator.validate_host_param(host) is None

        def test_host_is_invalid_ipv6(self, host) -> None:
            host = "1545:23:0:0:155"
            with pytest.raises(ValidationError, match=r".*\ is not a valid host ip or url.$"):
                validator.validate_host_param(host)

        def test_host_is_valid_url(self, host) -> None:
            host = "https://myhost.ddns.net"
            assert validator.validate_host_param(host) is None

        def test_host_is_invalid_url(self, host) -> None:
            host = "localhost"
            with pytest.raises(ValidationError, match=r".*\ is not a valid host ip or url.$"):
                validator.validate_host_param(host)

    class TestPortParam:
        def test_port_valid_number(self, port) -> None:
            port = 64738
            assert validator.validate_port_param(port) is None

        def test_port_valid_string(self, port) -> None:
            port = "64738"
            assert validator.validate_port_param(port) is None

        def test_port_is_none(self, port) -> None:
            port = None
            with pytest.raises(ValidationError, match=r".*\ must be provided.$"):
                validator.validate_port_param(port)  # type: ignore

        def test_port_is_empty(self, port) -> None:
            port = ""
            with pytest.raises(ValidationError, match=r".*\ cannot be empty.$"):
                validator.validate_port_param(port)

        def test_port_is_invalid_string(self, port) -> None:
            port = "invalid_port"
            with pytest.raises(ValidationError, match=r".*\ is not a valid port number.$"):
                validator.validate_port_param(port)

        def test_port_is_invalid_number_lower_range(self, port) -> None:
            port = -64738
            with pytest.raises(ValidationError, match=r".*\ is not a valid port number.$"):
                validator.validate_port_param(port)

        def test_port_is_invalid_number_upper_range(self, port) -> None:
            port = 65536
            with pytest.raises(ValidationError, match=r".*\ is not a valid port number.$"):
                validator.validate_port_param(port)

    class TestUserParam:
        def test_user_is_none(self, user) -> None:
            user = None
            with pytest.raises(ValidationError, match=r".*\ must be provided.$"):
                validator.validate_user_param(user)  # type: ignore

        def test_user_is_empty(self, user) -> None:
            user = " "
            with pytest.raises(ValidationError, match=r".*\ cannot be empty.$"):
                validator.validate_user_param(user)

        def test_user_is_invalid(self, user) -> None:
            user = True
            with pytest.raises(ValidationError, match=r".*\ must be a valid string.$"):
                validator.validate_user_param(user)  # type: ignore

    class TestPasswordParam:
        def test_password_is_empty(self, password) -> None:
            password = " "
            with pytest.raises(ValidationError, match=r".*\ cannot be empty.$"):
                validator.validate_password_param(password)

        def test_password_is_invalid(self, password) -> None:
            password = True
            with pytest.raises(ValidationError, match=r".*\ must be a valid string.$"):
                validator.validate_password_param(password)  # type: ignore

    class TestCertParam:
        def test_cert_is_empty(self, cert) -> None:
            cert = " "
            with pytest.raises(ValidationError, match=r".*\ cannot be empty.$"):
                validator.validate_cert_param(cert)

        def test_cert_is_invalid(self, cert) -> None:
            cert = True
            with pytest.raises(ValidationError, match=r".*\ must be a valid string.$"):
                validator.validate_cert_param(cert)  # type: ignore

    class TestKeyParam:
        def test_key_is_empty(self, key) -> None:
            key = " "
            with pytest.raises(ValidationError, match=r".*\ cannot be empty.$"):
                validator.validate_key_param(key)

        def test_key_is_invalid(self, key) -> None:
            key = True
            with pytest.raises(ValidationError, match=r".*\ must be a valid string.$"):
                validator.validate_key_param(key)  # type: ignore

    class TestTokensParam:
        def test_tokens_is_empty(self, tokens) -> None:
            tokens = " "
            with pytest.raises(ValidationError, match=r".*\ cannot be empty.$"):
                validator.validate_tokens_param(tokens)

        def test_tokens_is_invalid(self, tokens) -> None:
            tokens = True
            with pytest.raises(ValidationError, match=r".*\ must be a valid string.$"):
                validator.validate_tokens_param(tokens)  # type: ignore

    class TestAutoReconnectParam:
        def test_auto_reconnect_is_none(self, reconnect) -> None:
            reconnect = None
            with pytest.raises(ValidationError, match=r".*\ can only be True or False, not None.$"):
                validator.validate_auto_reconnect_param(reconnect)  # type: ignore

        def test_auto_reconnect_is_invalid(self, reconnect) -> None:
            reconnect = "invalid_auto_reconnect"
            with pytest.raises(ValidationError, match=r".*\ can only be True or False.$"):
                validator.validate_auto_reconnect_param(reconnect)  # type: ignore

    class TestVerboseParam:
        def test_verbose_is_empty(self, verbose) -> None:
            verbose = None
            with pytest.raises(ValidationError, match=r"^The verbose option can only be a number from"):
                validator.validate_verbose_param(verbose)  # type: ignore

        def test_verbose_is_invalid(self, verbose) -> None:
            verbose = "invalid_verbose"
            with pytest.raises(ValidationError, match=r"^The verbose option can only be a number from"):
                validator.validate_verbose_param(verbose)  # type: ignore

        def test_verbose_is_above_limit(self, verbose) -> None:
            verbose = 9999
            with pytest.raises(ValidationError, match=r"^The verbose option can only be a number from"):
                validator.validate_verbose_param(verbose)
