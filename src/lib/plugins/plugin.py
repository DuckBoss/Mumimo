import logging
import threading
from abc import ABC, abstractmethod
from functools import wraps
from typing import List, Optional

logger = logging.getLogger(__name__)


class PluginBase(ABC):
    @staticmethod
    def makeCommandRegister():
        # Thanks to ninjagecko/Palo for this idea:
        # https://stackoverflow.com/questions/5707589/calling-functions-by-array-index-in-python/5707605#5707605
        registered_cmds = {}

        def register(parameters: Optional[List[str]] = None):
            if parameters is None:
                parameters = []

            def register_with_parameters(func):
                registered_cmds[func.__name__] = (func, parameters)
                return func

            return register_with_parameters

        register.all = registered_cmds
        return register

    _is_running: bool = False
    _thread_stop_event: threading.Event = threading.Event()

    @property
    def is_running(self):
        return self._is_running

    @abstractmethod
    def start(self, plugin_name: str):
        if not self._is_running:
            logger.debug(f"Starting plugin: {plugin_name}")
            self._is_running = True
            self._thread_stop_event.clear()
            logger.debug(f"Plugin started: {plugin_name}")

    @abstractmethod
    def stop(self, plugin_name: str):
        if self._is_running:
            logger.debug(f"Stopping plugin: {plugin_name}")
            self._thread_stop_event.set()
            self._is_running = False
            logger.debug(f"Plugin stopped: {plugin_name}")

    @abstractmethod
    def quit(self, plugin_name: str):
        if self._is_running:
            self.stop()  # type: ignore
        logger.debug(f"Quitting plugin: {plugin_name}")
