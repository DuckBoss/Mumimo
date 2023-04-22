from typing import List


class ParameterDefinitions:
    class Plugin:
        ACTIVE: str = "active"
        STOP: str = "stop"
        START: str = "start"
        RESTART: str = "restart"

        @staticmethod
        def get_definitions() -> List[str]:
            return [
                ParameterDefinitions.Plugin.ACTIVE,
                ParameterDefinitions.Plugin.STOP,
                ParameterDefinitions.Plugin.START,
                ParameterDefinitions.Plugin.RESTART,
            ]
