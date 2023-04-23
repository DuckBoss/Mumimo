import logging

from typing import Optional, Union, List
from .constants import TextTypes
from .utility import FontModifiers, AlignmentModifiers
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

        def open(self, settings: Optional["Settings"] = None, **kwargs) -> bool:
            if self.is_open:
                return False
            if settings is None:
                settings = self.settings
            settings.update(**kwargs)
            self._box_open = f'<table bgcolor="{settings.table_bg_color}" align="{settings.table_align}" cellspacing="1" cellpadding="5">'
            self.is_open = True
            return True

        def close(self) -> bool:
            if not self.is_open:
                return False
            self._box_close = "</table>"
            self.is_open = False
            return True

        def add_row(self, text: str, settings: Optional["Settings"] = None, **kwargs) -> bool:
            if not self.is_open:
                return False
            if settings is None:
                settings = self.settings
            settings.update(**kwargs)
            _row_type = f"{'td' if settings.text_type == TextTypes.BODY else 'th'}"
            self._box_rows.append(
                f"<tr {FontModifiers.bgcolor(settings.row_bg_color)}>"
                f"<{_row_type} {AlignmentModifiers.align(settings.row_align)}>"
                f"<font {FontModifiers.color(settings.text_color)}>{text}</font>"
                f"</{_row_type}>"
                f"</tr>"
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

            table_align: str = "center"
            table_bg_color: str = "black"

            row_align: str = "left"
            row_bg_color: str = "black"

            def __init__(self, **kwargs) -> None:
                self.update(**kwargs)

            def update(self, **kwargs) -> "GUIFramework.ContentBox.Settings":
                self.text_type = kwargs.get("text_type", self.text_type)
                self.text_color = kwargs.get("text_color", self.text_color)
                self.text_align = kwargs.get("text_align", self.text_align)

                self.table_align = kwargs.get("table_align", self.table_align)
                self.table_bg_color = kwargs.get("table_bg_color", self.table_bg_color)

                self.row_align = kwargs.get("row_align", self.row_align)
                self.row_bg_color = kwargs.get("bg_color", self.row_bg_color)
                return self

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
        _content.open(**kwargs)
        for idx, row in enumerate(raw_text):
            _content.add_row(row, **kwargs)
        _content.close()

        _compiled_text: str = _content.compile()
        raw_text = "".join(text)
        kwargs["raw_text"] = raw_text

        logger.debug("Compiled GUI: " + _compiled_text)
        mumble_utils.echo(_compiled_text, **kwargs)
