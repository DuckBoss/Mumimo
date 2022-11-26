from typing import Dict, Union
from unittest.mock import patch

import pytest

from src.exceptions import ValidationError
from src.murmur_connection import MurmurConnection, MurmurConnectionSingleton


class TestMurmurConnection:
    @pytest.fixture(autouse=True)
    def murmur_connection(self):
        connection = MurmurConnectionSingleton()
        instance = connection.instance()
        yield instance
        if instance is not None:
            instance._thread = None
            instance._connection_instance = None
            instance._connection_params = None
            instance._is_connected = False
        if hasattr(connection, "_instance"):
            connection.clear()

    def test_murmur_connection_setup_without_init_params(self, murmur_connection) -> None:
        murmur_connection._setup()
        assert murmur_connection._connection_params is None

    @patch.object(MurmurConnection, "_validate_connection_params")
    def test_murmur_connection_setup_with_init_params(
        self, mock_validate, murmur_connection, valid_connection_params: Dict[str, Union[str, bool]]
    ) -> None:
        mock_validate.return_value = None
        murmur_connection._setup(valid_connection_params)
        assert murmur_connection._connection_params is not None

    @patch.object(MurmurConnection, "_setup")
    def test_murmur_connection_validate_correct_params(
        self, mock_setup, murmur_connection, valid_connection_params: Dict[str, Union[str, bool]]
    ) -> None:
        mock_setup.return_value = None
        murmur_connection._validate_connection_params(valid_connection_params)
        assert murmur_connection is not None

    @patch.object(MurmurConnection, "_setup")
    def test_murmur_connection_validate_incorrect_params(
        self, mock_setup, murmur_connection, invalid_connection_params: Dict[str, Union[str, bool]]
    ) -> None:
        mock_setup.return_value = None
        with pytest.raises(ValidationError, match=r".*\ is not a valid host ip or url.$"):
            murmur_connection._validate_connection_params(invalid_connection_params)

    @patch.object(MurmurConnection, "_connect_instance")
    @patch.object(MurmurConnection, "_loop")
    @patch.object(MurmurConnection, "start")
    @patch.object(MurmurConnection, "stop")
    def test_murmur_connection_connect_to_murmur_with_init_params(
        self, mock_instance, mock_loop, mock_start, mock_stop, murmur_connection, valid_connection_params: Dict[str, Union[str, bool]]
    ) -> None:
        mock_instance.return_value = None
        mock_loop.return_value = None
        mock_start.return_value = True
        mock_stop.return_value = True
        murmur_connection._setup(valid_connection_params)
        murmur_connection.connect()
        murmur_connection.start()
        murmur_connection.stop()
        assert murmur_connection._connection_params == valid_connection_params

    @patch.object(MurmurConnection, "_connect_instance")
    @patch.object(MurmurConnection, "_loop")
    @patch.object(MurmurConnection, "start")
    @patch.object(MurmurConnection, "stop")
    def test_murmur_connection_connect_to_murmur_with_connect_params(
        self, mock_instance, mock_loop, mock_start, mock_stop, murmur_connection, valid_connection_params: Dict[str, Union[str, bool]]
    ) -> None:
        mock_instance.return_value = None
        mock_loop.return_value = None
        mock_start.return_value = True
        mock_stop.return_value = True
        murmur_connection.connect(valid_connection_params)
        murmur_connection.start()
        murmur_connection.stop()
        assert murmur_connection._connection_params == valid_connection_params

    @patch.object(MurmurConnection, "_connect_instance")
    @patch("pymumble_py3.Mumble")
    def test_murmur_connection_threading(
        self, mock_connect, mock_mumble, murmur_connection, valid_connection_params: Dict[str, Union[str, bool]]
    ) -> None:
        mock_connect.return_value = None
        murmur_connection._setup(valid_connection_params)
        murmur_connection.connect()
        murmur_connection._is_connected = True
        murmur_connection.start()
        assert murmur_connection._thread is not None
        murmur_connection._connection_instance = mock_mumble
        murmur_connection.stop()
        assert murmur_connection._thread is None
