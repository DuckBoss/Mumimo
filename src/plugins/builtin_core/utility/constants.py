from typing import List


class ParameterDefinitions:
    class Echo:
        DELAY: str = "delay"
        BROADCAST: str = "broadcast"
        MYCHANNEL: str = "mychannel"
        CHANNEL: str = "channel"
        CHANNELS: str = "channels"
        USER: str = "user"
        USERS: str = "users"
        ME: str = "me"

        @staticmethod
        def get_definitions() -> List[str]:
            return [
                ParameterDefinitions.Echo.DELAY,
                ParameterDefinitions.Echo.BROADCAST,
                ParameterDefinitions.Echo.MYCHANNEL,
                ParameterDefinitions.Echo.CHANNEL,
                ParameterDefinitions.Echo.CHANNELS,
                ParameterDefinitions.Echo.USER,
                ParameterDefinitions.Echo.USERS,
                ParameterDefinitions.Echo.ME,
            ]

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

        @staticmethod
        def get_definitions() -> List[str]:
            return [
                ParameterDefinitions.Themes.SWITCH,
                ParameterDefinitions.Themes.LIST,
                ParameterDefinitions.Themes.NEW,
                ParameterDefinitions.Themes.DELETE,
                ParameterDefinitions.Themes.UPDATE,
            ]
