class TextModifiers:
    @staticmethod
    def bold(text: str) -> str:
        return f"<b>{text}</b>"

    @staticmethod
    def italicize(text):
        return f"<i>{text}</i>"

    @staticmethod
    def underline(text):
        return f"<u>{text}</u>"


class TagModifiers:
    @staticmethod
    def color(color: str) -> str:
        return f"color={color}"

    @staticmethod
    def align(align: str) -> str:
        return f"align={align}"
