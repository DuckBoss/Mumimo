import logging
import time
from typing import TYPE_CHECKING

from src.lib.plugins.plugin import PluginBase
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

    @command(parameters=["delay", "broadcast", "channel", "me"])
    def echo(self, data: "Command"):
        # Example:
        # !echo.channel "hello, channel!"
        # !echo.me "hello, me!"
        # !echo.delay=5.broadcast "hello, all channels!"
        _delay = 0
        _target_type = "channel"
        for param in data.parameters:
            if param.startswith("delay"):
                _delay = int(param.split("=")[1])
            elif param == "broadcast":
                _target_type = "broadcast"
            elif param == "channel":
                _target_type = "channel"
            elif param == "me":
                _target_type = "me"

        if _delay > 0:
            time.sleep(_delay)
        mumble_utils.echo(data.message, target_type=_target_type, user_id=data.actor)

    @command()
    def testcmdnoparams(self, data: "Command"):
        logger.debug("Executed testcmdnoparams command.")
