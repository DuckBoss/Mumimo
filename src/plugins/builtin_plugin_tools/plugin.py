import logging
from typing import TYPE_CHECKING

from src.lib.plugins.plugin import PluginBase
from src.settings import settings
from src.utils import mumble_utils

logger = logging.getLogger(__name__)


if TYPE_CHECKING:
    from src.lib.command import Command


class Plugin(PluginBase):
    command = PluginBase.makeCommandRegister()

    def __init__(self) -> None:
        logger.debug(f"Initializing plugin: '{__name__}'")
        super().__init__()
        logger.debug(f"Plugin '{__name__}' initialized.")

    def start(self):
        super().start(__name__)
        logger.debug(f"Plugin '{__name__}'::Running -> {self.is_running}")

    def stop(self):
        super().stop(__name__)

    def quit(self):
        super().quit(__name__)

    @command(parameters=["active"])
    def plugin(self, data: "Command"):
        # Example:
        # !plugin.active "builtin_core"
        _registered_plugins = settings.plugins.get_registered_plugins()
        if not _registered_plugins:
            mumble_utils.echo("No active plugins found.", target_type="me", user_id=data.actor)
            return

        for param in data.parameters:
            if param == "active":
                _plugin = _registered_plugins.get(data.message.strip())
                if not _plugin:
                    mumble_utils.echo(
                        f"Plugin '{data.message.strip()}' not found.",
                        target_type="me",
                        user_id=data.actor,
                    )
                    return
                _msg = f"Plugin '{data.message.strip()}' active: {_plugin.is_running}"
                mumble_utils.echo(_msg, target_type="me", user_id=data.actor)
                return
