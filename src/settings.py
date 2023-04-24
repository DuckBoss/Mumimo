import logging
from typing import TYPE_CHECKING, Any, Dict, List, Optional


from .lib.command_callbacks import CommandCallbacks
from .lib.singleton import singleton

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from .client_state import ClientState
    from .config import Config
    from .lib.command import Command
    from .lib.command_history import CommandHistory
    from .lib.frameworks.plugins.plugin import PluginBase
    from .log_config import LogConfig
    from .murmur_connection import MurmurConnection
    from .services.database_service import DatabaseService
    from .services.cmd_processing_service import CommandProcessingService


@singleton
class MumimoSettings:
    connection: "Connection"
    plugins: "Plugins"
    configs: "Configs"
    commands: "Commands"
    state: "State"
    database: "Database"

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

        def get_registered_plugin(self, plugin_name: str) -> Optional["PluginBase"]:
            return self._registered_plugins.get(plugin_name)

        def set_registered_plugin(self, plugin_name: str, plugin: "PluginBase") -> None:
            self._registered_plugins[plugin_name] = plugin

    class Configs:
        _mumimo_cfg: Optional["Config"] = None
        _log_cfg: Optional["LogConfig"] = None
        _gui_themes: Optional["Config"] = None

        def get_mumimo_config(self) -> Optional["Config"]:
            return self._mumimo_cfg

        def set_mumimo_config(self, cfg: "Config") -> None:
            self._mumimo_cfg = cfg

        def get_log_config(self) -> Optional["LogConfig"]:
            return self._log_cfg

        def set_log_config(self, cfg: "LogConfig") -> None:
            self._log_cfg = cfg

        def get_gui_themes(self) -> Optional["Config"]:
            return self._gui_themes

        def set_gui_themes(self, themes: "Config") -> Optional["Config"]:
            self._gui_themes = themes

    class State:
        _client_state: Optional["ClientState"] = None

        def get_client_state(self) -> Optional["ClientState"]:
            return self._client_state

        def set_client_state(self, client_state: "ClientState") -> None:
            self._client_state = client_state

    class Commands:
        history: "History"
        callbacks: "Callbacks"
        services: "Services"

        def __init__(self) -> None:
            self.history = self.History()
            self.callbacks = self.Callbacks()
            self.services = self.Services()

        class Services:
            _cmd_processing_service: Optional["CommandProcessingService"] = None

            def set_cmd_processing_service(self, service: "CommandProcessingService") -> None:
                self._cmd_processing_service = service

            def get_cmd_processing_service(self) -> Optional["CommandProcessingService"]:
                return self._cmd_processing_service

        class History:
            _cmd_history: Optional["CommandHistory"] = None

            def get_command_history(self) -> Optional["CommandHistory"]:
                return self._cmd_history

            def set_command_history(self, history: "CommandHistory") -> None:
                self._cmd_history = history

            def add_command_to_history(self, command: "Command") -> Optional["Command"]:
                if self._cmd_history:
                    return self._cmd_history.add(command)
                return None

        class Callbacks:
            _cmd_callbacks: Optional["CommandCallbacks"] = None

            def get_command_callbacks(self) -> Optional["CommandCallbacks"]:
                return self._cmd_callbacks

            def set_command_callbacks(self, callbacks: "CommandCallbacks") -> None:
                self._cmd_callbacks = callbacks

            def add_command_callbacks(self, callbacks: "CommandCallbacks") -> None:
                if self._cmd_callbacks is None:
                    self._cmd_callbacks = CommandCallbacks()
                self._cmd_callbacks.update(callbacks)

            def get_callback(self, plugin: str, command: str) -> Optional[Dict[str, Any]]:
                _all_callbacks = self.get_command_callbacks()
                if _all_callbacks is None:
                    return None
                return _all_callbacks.get(f"{plugin}.{command}", None)

            def get_callbacks(self, plugin: str) -> List[Dict[str, Any]]:
                _all_callbacks = self.get_command_callbacks()
                if _all_callbacks is None:
                    logger.warning(f"Unable to retrieve callbacks for plugin '{plugin}'.")
                    return []
                _plugin_callbacks = []
                for idx, (_cmd, _clbk) in enumerate(_all_callbacks.items()):
                    if _clbk["plugin"] == plugin:
                        _plugin_callbacks.append(_clbk)
                return _plugin_callbacks

    class Database:
        _database_instance: Optional["DatabaseService"] = None

        def get_database_instance(self) -> Optional["DatabaseService"]:
            return self._database_instance

        def set_database_instance(self, instance: "DatabaseService") -> None:
            self._database_instance = instance

    def __init__(self) -> None:
        self.commands = self.Commands()
        self.configs = self.Configs()
        self.connection = self.Connection()
        self.plugins = self.Plugins()
        self.state = self.State()
        self.database = self.Database()


settings = MumimoSettings()
