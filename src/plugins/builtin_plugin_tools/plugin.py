import logging
from typing import TYPE_CHECKING, Optional

from src.constants import LogOutputIdentifiers
from src.lib.frameworks.plugins.plugin import PluginBase
from src.settings import settings
from src.utils import mumble_utils

from .utility.constants import ParameterDefinitions

logger = logging.getLogger(__name__)


if TYPE_CHECKING:
    from src.lib.command import Command


class Plugin(PluginBase):
    command = PluginBase.makeCommandRegister()

    def __init__(self, plugin_name: str) -> None:
        self._plugin_name = plugin_name
        logger.debug(f"[{LogOutputIdentifiers.PLUGINS}]: Initializing plugin: '{self._plugin_name}'")
        super().__init__(self._plugin_name)

        self.initialize_parameters(settings.commands.callbacks.get_callbacks(self._plugin_name))
        logger.debug(f"[{LogOutputIdentifiers.PLUGINS}]: Plugin '{self._plugin_name}' ready.")

    @command(
        parameters=ParameterDefinitions.Plugin.get_definitions(),
        parameters_required=True,
        exclusive_parameters=ParameterDefinitions.Plugin.get_definitions(),
    )
    def plugin(self, data: "Command"):
        # Example:
        # !plugin.active "builtin_core"  -> Displays a message showing the status of the specified plugin.
        # !plugin.stop "plugin1"  -> Stops the specified plugin if it is running.
        # !plugin.start "plugin1"  -> Starts the specified plugin if it is not running.
        # !plugin.restart "plugin1"  -> Restarts the specified plugin.
        _parameters = self.verify_parameters(self.plugin.__name__, data)
        if _parameters is None:
            return

    def _get_plugin(self, data: "Command") -> Optional["PluginBase"]:
        _plugin_name: str = data.message.strip()
        if not _plugin_name:
            mumble_utils.echo(
                f"'{data._command}' command warning: an invalid plugin name was provided.",
                target_users=mumble_utils.get_user_by_id(data.actor),
            )
            return
        _plugin: Optional["PluginBase"] = settings.plugins.get_registered_plugin(_plugin_name)
        if _plugin is None:
            mumble_utils.echo(
                f"'{data._command}' command error: the plugin '{_plugin_name}' could not be found.",
                target_users=mumble_utils.get_user_by_id(data.actor),
            )
            return
        return _plugin

    def _parameter_plugin_stop(self, data: "Command", parameter: str) -> None:
        _plugin = self._get_plugin(data)
        if not _plugin:
            return

        _status, _message = _plugin.stop()
        if not _status:
            mumble_utils.echo(
                f"'{data._command}' command error: {_message}",
                target_users=mumble_utils.get_user_by_id(data.actor),
            )
            return
        mumble_utils.echo(
            _message,
            target_users=mumble_utils.get_user_by_id(data.actor),
        )

    def _parameter_plugin_start(self, data: "Command", parameter: str) -> None:
        _plugin = self._get_plugin(data)
        if not _plugin:
            return

        _status, _message = _plugin.start()
        if not _status:
            mumble_utils.echo(
                f"'{data._command}' command error: {_message}",
                target_users=mumble_utils.get_user_by_id(data.actor),
            )
            return
        mumble_utils.echo(
            _message,
            target_users=mumble_utils.get_user_by_id(data.actor),
        )

    def _parameter_plugin_restart(self, data: "Command", parameter: str) -> None:
        _plugin = self._get_plugin(data)
        if not _plugin:
            return

        _status, _message = _plugin.restart()
        if not _status:
            mumble_utils.echo(
                f"'{data._command}' command error: {_message}",
                target_users=mumble_utils.get_user_by_id(data.actor),
            )
            return
        mumble_utils.echo(
            _message,
            target_users=mumble_utils.get_user_by_id(data.actor),
        )

    def _parameter_plugin_active(self, data: "Command", parameter: str) -> None:
        _registered_plugins = settings.plugins.get_registered_plugins()
        if not _registered_plugins:
            mumble_utils.echo(
                f"'{data._command}' command warning: no active plugins were found.",
                target_users=mumble_utils.get_user_by_id(data.actor),
            )
            return
        _plugin = _registered_plugins.get(data.message.strip())
        if not _plugin:
            mumble_utils.echo(
                f"'{data._command}' command warning: no plugin name was provided.",
                target_users=mumble_utils.get_user_by_id(data.actor),
            )
            return
        mumble_utils.echo(
            f"Plugin '{data.message.strip()}' active: {_plugin.is_running}",
            target_users=mumble_utils.get_user_by_id(data.actor),
        )
