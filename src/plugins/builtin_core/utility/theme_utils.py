from typing import List, Optional, TYPE_CHECKING
from src.settings import settings
from src.exceptions import PluginError
from src.constants import MumimoCfgFields

if TYPE_CHECKING:
    from src.config import Config


def list_themes() -> List[str]:
    _themes = settings.configs.get_gui_themes()
    if _themes:
        return list(_themes.keys())
    return []


def switch_themes(theme: str) -> bool:
    _themes: List[str] = list_themes()
    if theme not in _themes:
        return False

    _config: Optional["Config"] = settings.configs.get_mumimo_config()
    if not _config:
        raise PluginError("Unable to switch themes: mumimo config could not be retrieved from settings.")

    _success_switch: bool = _config.set(MumimoCfgFields.SETTINGS.GUI.SELECTED_THEME, theme)
    _saved_data: str = _config.save(
        modified_only=True,
        modified_field_name=MumimoCfgFields.SETTINGS.GUI.SELECTED_THEME,
    )
    return _success_switch and _saved_data is not None
