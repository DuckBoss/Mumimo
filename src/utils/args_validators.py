import logging
from typing import Union

import validators

from ..constants import VERBOSITY_MAX, VERBOSITY_MIN
from ..exceptions import ValidationError

logger = logging.getLogger(__name__)


class SystemArgumentsValidator:
    @staticmethod
    def validate_host_param(host: str) -> None:
        if host is None:
            raise ValidationError("The server host ip/url must be provided.", logger)
        host = host.strip()
        if len(host) == 0:
            raise ValidationError("The server host ip/url cannot be empty.", logger)
        _validate = validators.ipv4(host) or validators.ipv6(host) or validators.url(host)  # pyright: reportGeneralTypeIssues=false
        if isinstance(_validate, validators.ValidationFailure):
            raise ValidationError(f"The provided host: '{host}' is not a valid host ip or url.", logger)

    @staticmethod
    def validate_port_param(port: Union[str, int]) -> None:
        if port is None:
            raise ValidationError("The server port must be provided.", logger)
        if isinstance(port, str) and len(port.strip()) == 0:
            raise ValidationError("The server port cannot be empty.", logger)
        try:
            int_port: int = int(port)
        except ValueError as exc:
            raise ValidationError(f"The server port: '{port}' is not a valid port number.", logger) from exc
        if int_port < 1 or int_port > 65535:
            raise ValidationError(f"The server port: '{port}' is not a valid port number.", logger)

    @staticmethod
    def validate_user_param(user: str) -> None:
        if user is None:
            raise ValidationError("The client user must be provided.", logger)
        if not isinstance(user, str):
            raise ValidationError("The client user must be a valid string.", logger)
        if len(user.strip()) == 0:
            raise ValidationError("The client username cannot be empty.", logger)

    @staticmethod
    def validate_password_param(password: str) -> None:
        if password is not None:
            if not isinstance(password, str):
                raise ValidationError("The server password must be a valid string.", logger)
            if len(password.strip()) == 0:
                raise ValidationError("The server password cannot be empty.", logger)

    @staticmethod
    def validate_cert_param(cert: str) -> None:
        if cert is not None:
            if not isinstance(cert, str):
                raise ValidationError("The client certificate file path must be a valid string.", logger)
            if len(cert.strip()) == 0:
                raise ValidationError("The client certificate file path cannot be empty.", logger)

    @staticmethod
    def validate_key_param(key: str) -> None:
        if key is not None:
            if not isinstance(key, str):
                raise ValidationError("The client key file path must be a valid string.", logger)
            if len(key.strip()) == 0:
                raise ValidationError("The client key file path cannot be empty.", logger)

    @staticmethod
    def validate_tokens_param(tokens: str) -> None:
        if tokens is not None:
            if not isinstance(tokens, str):
                raise ValidationError("The client channels access tokens must be a valid string.", logger)
            if len(tokens.strip()) == 0:
                raise ValidationError("The client channels access tokens cannot be empty.", logger)

    @staticmethod
    def validate_auto_reconnect_param(reconnect: bool) -> None:
        if reconnect is None:
            raise ValidationError("The reconnect option can only be True or False, not None.", logger)
        if not isinstance(reconnect, bool):
            raise ValidationError("The reconnect option can only be True or False.", logger)

    @staticmethod
    def validate_verbose_param(verbose: int) -> None:
        if verbose is None:
            raise ValidationError(f"The verbose option can only be a number from {VERBOSITY_MIN} to {VERBOSITY_MAX}, not None.", logger)
        if not isinstance(verbose, int):
            raise ValidationError(f"The verbose option can only be a number from {VERBOSITY_MIN} to {VERBOSITY_MAX}.", logger)
        if VERBOSITY_MIN > verbose or verbose > VERBOSITY_MAX:
            raise ValidationError(f"The verbose option can only be a number from {VERBOSITY_MIN} to {VERBOSITY_MAX}.", logger)
