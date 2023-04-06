import logging
from typing import List, Optional

from src.lib.plugins.plugin import PluginBase

logger = logging.getLogger(__name__)


class Plugin(PluginBase):
    command = PluginBase.makeCommandRegister()

    def __init__(self) -> None:
        logger.debug(f"Initializing plugin: '{__name__}'")
        super().__init__()
        logger.debug(f"Plugin '{__name__}' initialized.")

    def start(self):
        raise NotImplementedError

    def stop(self):
        raise NotImplementedError

    def quit(self):
        raise NotImplementedError

    @command(parameters=["all", "channel", "me"])
    def testcmd(self, parameters: Optional[List[str]] = None):
        # Example:
        # !echo.delay.broadcast 5 "exiting for the day!"
        # Or maybe:
        # !echo.delay=5.broadcast "exiting for the day!"

        logger.debug("Executed testcmd command.")

    @command()
    def testcmdnoparams(self):
        logger.debug("Executed testcmdnoparams command.")
