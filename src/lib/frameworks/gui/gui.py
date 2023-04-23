import logging

from typing import Optional, Union, List
from .constants import TextTypes
from .utility import TagModifiers
from ....utils import mumble_utils


logger = logging.getLogger(__name__)


class GUIFramework:
    class ContentBox:
        is_open: bool
        settings: "Settings"

        _box_open: str
        _box_close: str
        _box_rows: List[str]

        def __init__(self, settings: Optional["Settings"] = None) -> None:
            if settings is not None:
                self.settings = settings
            else:
                self.settings = self.Settings()
            self.is_open = False
            self._box_open = ""
            self._box_close = ""
            self._box_rows = []

        def open(self, settings: Optional["Settings"] = None) -> bool:
            if self.is_open:
                return False
            if settings is None:
                settings = self.settings
            self._box_open = f'<table bgcolor="{self.settings.background_color}" align="{self.settings.background_color}">'
            self.is_open = True
            return True

        def close(self) -> bool:
            if not self.is_open:
                return False
            self._box_close = "</table>"
            self.is_open = False
            return True

        def add_row(self, text: str, settings: Optional["Settings"] = None) -> bool:
            if not self.is_open:
                return False
            if settings is None:
                settings = self.settings
            _row_type = f"{'tr' if self.settings.text_type == TextTypes.BODY else 'th'}"
            self._box_rows.append(
                f'<{_row_type} {TagModifiers.align(self.settings.text_align)} {TagModifiers.color(settings.text_color)}">{text}</{_row_type}>'
            )
            return True

        def compile(self) -> str:
            _msg = f"{self._box_open}{''.join(self._box_rows)}{self._box_close}"
            self._box_open = ""
            self._box_close = ""
            self._box_rows = []
            self.is_open = False

            return _msg

        class Settings:
            text_type: TextTypes = TextTypes.HEADER
            text_color: str = "yellow"
            text_align: str = "center"
            background_color: str = "black"

    def __init__(self) -> None:
        logger.debug("Initialized GUI Framework.")

    @staticmethod
    def gui(
        text: Union[List[str], str],
        settings: Optional[ContentBox.Settings] = None,
        **kwargs,
    ) -> None:
        raw_text = text
        if isinstance(text, str):
            raw_text = [text]

        _content = GUIFramework.ContentBox(settings=settings)
        _content.open()
        for idx, row in enumerate(raw_text):
            _content.add_row(row)
        _content.close()

        _compiled_text: str = _content.compile()
        raw_text = "".join(text)
        kwargs["raw_text"] = raw_text

        logger.debug("Compiled GUI: " + _compiled_text)
        mumble_utils.echo(_compiled_text, **kwargs)
