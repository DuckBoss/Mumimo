from typing import Dict, Union
from unittest.mock import patch

import pytest

from src.exceptions import ValidationError
from src.murmur_connection import MurmurConnection


class TestMurmurConnection:
    @pytest.fixture(autouse=True)
    def murmur_connection(self):
        instance = MurmurConnection()
        yield instance
        if instance is not None:
            if instance._thread is not None:
                if instance._thread_stop_event is not None:
                    instance._thread_stop_event.set()
                    instance._thread.join()
            instance._thread = None
            instance._connection_instance = None
            instance._connection_params = None
            instance._is_connected = False

    def test_murmur_connection_setup_without_init_params(self, murmur_connection: MurmurConnection) -> None:
        murmur_connection.setup({})  # type: ignore
        assert murmur_connection._connection_params is None

    @patch.object(MurmurConnection, "_validate_sys_args")
    def test_murmur_connection_setup_with_init_params(
        self, mock_validate, murmur_connection: MurmurConnection, valid_connection_params: Dict[str, Union[str, bool]]
    ) -> None:
        mock_validate.return_value = None
        murmur_connection.setup(valid_connection_params)
        assert murmur_connection._connection_params is not None

    @patch.object(MurmurConnection, "setup")
    def test_murmur_connection_validate_correct_connection_sys_args(
        self, mock_setup, murmur_connection: MurmurConnection, valid_connection_params: Dict[str, Union[str, bool]]
    ) -> None:
        mock_setup.return_value = None
        murmur_connection._validate_sys_args(valid_connection_params)
        assert murmur_connection is not None

    @patch.object(MurmurConnection, "setup")
    def test_murmur_connection_validate_incorrect_connection_sys_args(
        self, mock_setup, murmur_connection: MurmurConnection, invalid_connection_params: Dict[str, Union[str, bool]]
    ) -> None:
        mock_setup.return_value = None
        with pytest.raises(ValidationError, match=r".*\ is not a valid host ip or url.$"):
            murmur_connection._validate_sys_args(invalid_connection_params)

    @patch.object(MurmurConnection, "_connect_instance")
    @patch.object(MurmurConnection, "_loop")
    @patch.object(MurmurConnection, "start")
    @patch.object(MurmurConnection, "stop")
    @patch.object(MurmurConnection, "connect")
    def test_murmur_connection_connect_to_murmur_with_init_params(
        self,
        mock_connect,
        mock_stop,
        mock_start,
        mock_loop,
        mock_instance,
        murmur_connection: MurmurConnection,
        valid_connection_params: Dict[str, Union[str, bool]],
    ) -> None:
        mock_instance.return_value = None
        mock_loop.return_value = None
        mock_start.return_value = True
        mock_stop.return_value = True
        mock_connect.return_value = None
        murmur_connection.setup(valid_connection_params)
        murmur_connection.ready()
        murmur_connection.connect()
        murmur_connection.start()
        murmur_connection.stop()
        assert murmur_connection._connection_params == valid_connection_params

    @patch.object(MurmurConnection, "_loop")
    @patch.object(MurmurConnection, "start")
    @patch.object(MurmurConnection, "stop")
    @patch.object(MurmurConnection, "connect")
    def test_murmur_connection_connect_to_murmur_with_connect_params(
        self,
        mock_connect,
        mock_stop,
        mock_start,
        mock_loop,
        murmur_connection: MurmurConnection,
        valid_connection_params: Dict[str, Union[str, bool]],
    ) -> None:
        mock_loop.return_value = None
        mock_start.return_value = True
        mock_stop.return_value = True
        mock_connect.return_value = None
        murmur_connection.setup(valid_connection_params)
        murmur_connection.ready().connect()
        murmur_connection.start()
        murmur_connection.stop()
        assert murmur_connection._connection_params == valid_connection_params

    @patch.object(MurmurConnection, "_connect_instance")
    @patch.object(MurmurConnection, "connect")
    @patch("pymumble_py3.Mumble")
    def test_murmur_connection_threading(
        self, mock_mumble, mock_connect, mock_instance, murmur_connection: MurmurConnection, valid_connection_params: Dict[str, Union[str, bool]]
    ) -> None:
        mock_instance.return_value = None
        mock_connect.return_value = None
        murmur_connection.setup(valid_connection_params)
        murmur_connection.ready()
        murmur_connection.connect()
        murmur_connection._is_connected = True
        murmur_connection.start()
        assert murmur_connection._thread is not None
        murmur_connection._connection_instance = mock_mumble
        murmur_connection.stop()
        assert murmur_connection._thread is None
