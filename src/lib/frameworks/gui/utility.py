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

    @staticmethod
    def subscript(text):
        return f"<sub>{text}</sub>"


class FontModifiers:
    @staticmethod
    def color(color: str) -> str:
        return f'color="{color}"'

    @staticmethod
    def face(face: str) -> str:
        return f'face="{face}"'

    @staticmethod
    def bgcolor(bgcolor: str) -> str:
        return f'bgcolor="{bgcolor}"'


class AlignmentModifiers:
    @staticmethod
    def align(align: str) -> str:
        return f'align="{align}"'
