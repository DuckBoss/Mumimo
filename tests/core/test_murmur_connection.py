from typing import Dict, Union
from unittest.mock import patch

import pytest

from src.constants import SYS_CERT, SYS_DEBUG, SYS_HOST, SYS_KEY, SYS_PASS, SYS_PORT, SYS_RECONNECT, SYS_TOKENS, SYS_USER
from src.exceptions import ValidationError
from src.murmur_connection import MurmurConnection


class TestMurmurConnection:
    @pytest.fixture(autouse=True)
    def correct_params(self) -> Dict[str, Union[str, bool]]:
        return {
            SYS_HOST: "127.0.0.1",
            SYS_PORT: "64738",
            SYS_USER: "test",
            SYS_PASS: "test",
            SYS_CERT: "path/to/cert",
            SYS_TOKENS: "token1 token2",
            SYS_KEY: "path/to/key",
            SYS_RECONNECT: False,
            SYS_DEBUG: False,
        }

    @pytest.fixture(autouse=True)
    def incorrect_params(self) -> Dict[str, Union[str, bool]]:
        return {
            SYS_HOST: "hello",
            SYS_PORT: "hello",
            SYS_USER: "test",
            SYS_PASS: "test",
            SYS_CERT: "path/to/cert",
            SYS_TOKENS: "token1 token2",
            SYS_KEY: "path/to/key",
            SYS_RECONNECT: False,
            SYS_DEBUG: False,
        }

    @patch.object(MurmurConnection, "_validate_connection_params")
    def test_murmur_connection_without_init_params(self, mock_setup) -> None:
        mock_setup.return_value = None
        connection = MurmurConnection()
        assert connection._connection_params is None

    @patch.object(MurmurConnection, "_validate_connection_params")
    def test_murmur_connection_with_init_params(self, mock_setup, correct_params: Dict[str, Union[str, bool]]) -> None:
        mock_setup.return_value = None
        connection = MurmurConnection(correct_params)
        assert connection._connection_params is not None

    @patch.object(MurmurConnection, "_setup")
    def test_murmur_connection_validate_correct_params(self, mock_validate, correct_params: Dict[str, Union[str, bool]]) -> None:
        mock_validate.return_value = None
        connection = MurmurConnection(correct_params)
        connection._validate_connection_params(correct_params)
        assert connection is not None

    @patch.object(MurmurConnection, "_setup")
    def test_murmur_connection_validate_incorrect_params(self, mock_validate, incorrect_params: Dict[str, Union[str, bool]]) -> None:
        mock_validate.return_value = None
        connection = MurmurConnection(incorrect_params)
        with pytest.raises(ValidationError, match=r".*\ is not a valid host ip or url.$"):
            connection._validate_connection_params(incorrect_params)

    @patch.object(MurmurConnection, "_connect_instance")
    @patch.object(MurmurConnection, "_loop")
    def test_murmur_connection_connect_to_murmur_with_init_params(
        self, mock_instance, mock_loop, correct_params: Dict[str, Union[str, bool]]
    ) -> None:
        mock_instance.return_value = None
        mock_loop.return_value = None
        connection = MurmurConnection(correct_params)
        connection.connect()
        assert connection._connection_params == correct_params

    @patch.object(MurmurConnection, "_connect_instance")
    @patch.object(MurmurConnection, "_loop")
    def test_murmur_connection_connect_to_murmur_with_connect_params(
        self, mock_instance, mock_loop, correct_params: Dict[str, Union[str, bool]]
    ) -> None:
        mock_instance.return_value = None
        mock_loop.return_value = None
        connection = MurmurConnection()
        connection.connect(correct_params)
        assert connection._connection_params == correct_params
