from typing import List


class ParameterDefinitions:
    class Plugin:
        STATUS: str = "status"
        STOP: str = "stop"
        START: str = "start"
        RESTART: str = "restart"

        @staticmethod
        def get_definitions() -> List[str]:
            return [
                ParameterDefinitions.Plugin.STATUS,
                ParameterDefinitions.Plugin.STOP,
                ParameterDefinitions.Plugin.START,
                ParameterDefinitions.Plugin.RESTART,
            ]
