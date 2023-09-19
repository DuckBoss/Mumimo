from typing import List


class ParameterDefinitions:
    class Move:
        TO_CHANNEL: str = "to_channel"
        TO_USER: str = "to_user"
        TO_ME: str = "to_me"

        @staticmethod
        def get_definitions() -> List[str]:
            return [
                ParameterDefinitions.Move.TO_CHANNEL,
                ParameterDefinitions.Move.TO_USER,
                ParameterDefinitions.Move.TO_ME,
            ]

    class Themes:
        SWITCH: str = "switch"
        LIST: str = "list"
        NEW: str = "new"
        DELETE: str = "delete"
        UPDATE: str = "update"
        SHOW: str = "show"
        RESET: str = "reset"
        RESETALL: str = "resetall"

        @staticmethod
        def get_definitions() -> List[str]:
            return [
                ParameterDefinitions.Themes.SWITCH,
                ParameterDefinitions.Themes.LIST,
                ParameterDefinitions.Themes.NEW,
                ParameterDefinitions.Themes.DELETE,
                ParameterDefinitions.Themes.UPDATE,
                ParameterDefinitions.Themes.SHOW,
                ParameterDefinitions.Themes.RESET,
                ParameterDefinitions.Themes.RESETALL,
            ]
