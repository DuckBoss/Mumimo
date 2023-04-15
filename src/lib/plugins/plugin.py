from abc import ABC, abstractmethod
from typing import List, Optional


class PluginBase(ABC):
    @classmethod
    def makeCommandRegister(cls):
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

    @abstractmethod
    def start(self):
        raise NotImplementedError

    @abstractmethod
    def stop(self):
        raise NotImplementedError

    @abstractmethod
    def quit(self):
        raise NotImplementedError
