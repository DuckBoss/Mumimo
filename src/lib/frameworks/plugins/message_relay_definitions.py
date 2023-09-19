from typing import List


class MessageRelayDefinitions:
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
            MessageRelayDefinitions.DELAY,
            MessageRelayDefinitions.BROADCAST,
            MessageRelayDefinitions.MYCHANNEL,
            MessageRelayDefinitions.CHANNEL,
            MessageRelayDefinitions.CHANNELS,
            MessageRelayDefinitions.USER,
            MessageRelayDefinitions.USERS,
            MessageRelayDefinitions.ME,
        ]
