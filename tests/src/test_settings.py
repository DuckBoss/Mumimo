from typing import Callable, Dict
from unittest.mock import MagicMock

from src.client_state import ClientState
from src.config import Config
from src.lib.command_callbacks import CommandCallbacks
from src.log_config import LogConfig
from src.settings import settings


class TestSettings:
    def test_set_mumimo_config(self):
        _cfg: Config = MagicMock(Config)
        settings.set_mumimo_config = MagicMock()
        settings.set_mumimo_config(_cfg)
        settings.set_mumimo_config.assert_called_once_with(_cfg)

    def test_get_mumimo_config(self):
        _cfg: Config = MagicMock(Config)
        settings.set_mumimo_config(_cfg)
        settings.get_mumimo_config = MagicMock()
        _ = settings.get_mumimo_config()
        settings.get_mumimo_config.assert_called_once()

    def test_set_log_config(self):
        _cfg: LogConfig = MagicMock(LogConfig)
        settings.set_log_config = MagicMock()
        settings.set_log_config(_cfg)
        settings.set_log_config.assert_called_once_with(_cfg)

    def test_get_log_config(self):
        _cfg: LogConfig = MagicMock(LogConfig)
        settings.set_log_config(_cfg)
        settings.get_log_config = MagicMock()
        _ = settings.get_log_config()
        settings.get_log_config.assert_called_once()

    def test_set_client_state(self):
        _client_state: ClientState = MagicMock(ClientState)
        settings.set_client_state = MagicMock()
        settings.set_client_state(_client_state)
        settings.set_client_state.assert_called_once_with(_client_state)

    def test_get_client_state(self):
        _client_state: ClientState = MagicMock(ClientState)
        settings.set_log_config(_client_state)
        settings.get_log_config = MagicMock()
        _ = settings.get_log_config()
        settings.get_log_config.assert_called_once()

    def test_get_registered_plugins(self):
        _registered_plugins: Dict[str, Callable] = MagicMock(Dict[str, Callable])
        settings._registered_plugins = _registered_plugins
        settings.get_registered_plugins = MagicMock()
        _ = settings.get_registered_plugins()
        settings.get_registered_plugins.assert_called_once()

    def test_set_command_callbacks(self):
        _callbacks: CommandCallbacks = MagicMock(CommandCallbacks)
        settings.set_command_callbacks = MagicMock()
        settings.set_command_callbacks(_callbacks)
        settings.set_command_callbacks.assert_called_once_with(_callbacks)

    def test_get_command_callbacks(self):
        _callbacks: CommandCallbacks = MagicMock(CommandCallbacks)
        settings.set_command_callbacks(_callbacks)
        settings.get_command_callbacks = MagicMock()
        _ = settings.get_command_callbacks()
        settings.get_command_callbacks.assert_called_once()
