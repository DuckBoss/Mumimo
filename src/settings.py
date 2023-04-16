from typing import TYPE_CHECKING, Dict, Optional

from .lib.singleton import singleton

if TYPE_CHECKING:
    from .client_state import ClientState
    from .config import Config
    from .lib.command_callbacks import CommandCallbacks
    from .lib.plugins.plugin import PluginBase
    from .log_config import LogConfig
    from .murmur_connection import MurmurConnection


@singleton
class MumimoSettings:
    connection: "Connection"
    plugins: "Plugins"
    configs: "Configs"
    commands: "Commands"
    state: "State"

    class Connection:
        _murmur_connection: Optional["MurmurConnection"] = None

        def set_murmur_connection(self, murmur_connection: "MurmurConnection") -> None:
            self._murmur_connection = murmur_connection

        def get_murmur_connection(self) -> Optional["MurmurConnection"]:
            return self._murmur_connection

    class Plugins:
        _registered_plugins: Dict[str, "PluginBase"] = {}

        def get_registered_plugins(self) -> Dict[str, "PluginBase"]:
            return self._registered_plugins

        def set_registered_plugin(self, plugin_name: str, plugin: "PluginBase") -> None:
            self._registered_plugins[plugin_name] = plugin

    class Configs:
        _mumimo_cfg: Optional["Config"] = None
        _log_cfg: Optional["LogConfig"] = None

        def get_mumimo_config(self) -> Optional["Config"]:
            return self._mumimo_cfg

        def set_mumimo_config(self, cfg: "Config") -> None:
            self._mumimo_cfg = cfg

        def get_log_config(self) -> Optional["LogConfig"]:
            return self._log_cfg

        def set_log_config(self, cfg: "LogConfig") -> None:
            self._log_cfg = cfg

    class State:
        _client_state: Optional["ClientState"] = None

        def get_client_state(self) -> Optional["ClientState"]:
            return self._client_state

        def set_client_state(self, client_state: "ClientState") -> None:
            self._client_state = client_state

    class Commands:
        _cmd_callbacks: Optional["CommandCallbacks"] = None

        def get_command_callbacks(self) -> Optional["CommandCallbacks"]:
            return self._cmd_callbacks

        def set_command_callbacks(self, callbacks: "CommandCallbacks") -> None:
            self._cmd_callbacks = callbacks

    def __init__(self) -> None:
        self.commands = self.Commands()
        self.configs = self.Configs()
        self.connection = self.Connection()
        self.plugins = self.Plugins()
        self.state = self.State()


settings = MumimoSettings()
