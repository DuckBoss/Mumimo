from typing import List


class ParameterDefinitions:
    class Image:
        GRAYSCALE: str = "grayscale"
        INVERT: str = "invert"
        COMPRESS: str = "compress"
        COLORSHIFT: str = "colorshift"
        BLUR: str = "blur"
        BRIGHTNESS: str = "brightness"
        CONTRAST: str = "contrast"

        BROADCAST: str = "broadcast"
        CHANNEL: str = "channel"
        CHANNELS: str = "channels"
        USER: str = "user"
        USERS: str = "users"
        ME: str = "me"

        @staticmethod
        def get_definitions() -> List[str]:
            return [
                ParameterDefinitions.Image.GRAYSCALE,
                ParameterDefinitions.Image.INVERT,
                ParameterDefinitions.Image.COMPRESS,
                ParameterDefinitions.Image.COLORSHIFT,
                ParameterDefinitions.Image.BLUR,
                ParameterDefinitions.Image.BRIGHTNESS,
                ParameterDefinitions.Image.CONTRAST,
                ParameterDefinitions.Image.BROADCAST,
                ParameterDefinitions.Image.CHANNEL,
                ParameterDefinitions.Image.CHANNELS,
                ParameterDefinitions.Image.USER,
                ParameterDefinitions.Image.USERS,
                ParameterDefinitions.Image.ME,
            ]
