import logging
from typing import TYPE_CHECKING

from src.constants import LogOutputIdentifiers
from src.lib.frameworks.plugins.plugin import PluginBase
from src.settings import settings

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

    @command(parameters=[])
    def soundboard(self, data: "Command") -> None:
        pass
