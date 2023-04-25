import logging
import pathlib
from typing import List, Optional, Dict, Any
from src.settings import settings
from src.exceptions import PluginError
from src.constants import MumimoCfgFields
from src.config import Config

logger = logging.getLogger(__name__)


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
        raise PluginError("Unable to switch themes: mumimo config could not be retrieved from settings.", logger=logger)

    _success_switch: bool = _config.set(MumimoCfgFields.SETTINGS.GUI.SELECTED_THEME, theme)
    _saved_data: str = _config.save(
        modified_only=True,
        modified_field_name=MumimoCfgFields.SETTINGS.GUI.SELECTED_THEME,
    )
    return _success_switch and _saved_data is not None


def delete_theme(theme: str) -> bool:
    theme = theme.strip().replace(" ", "_")

    if _get_theme(theme) is None:
        logger.error(f"Failed to delete gui theme: theme '{theme}' does not exist.")
        return False

    _themes: Optional["Config"] = settings.configs.get_gui_themes()
    if not _themes:
        logger.error("Failed to delete gui theme: the gui themes could not be retrieved from settings.")
        return False

    del _themes[theme]
    _themes.save()
    logger.debug(f"Deleted gui theme: {theme}.")
    return True


def new_theme(theme: str) -> bool:
    _template_theme = _get_template_theme()
    _themes: Optional["Config"] = settings.configs.get_gui_themes()
    if not _themes:
        logger.error("Failed to create new gui theme: the gui themes could not be retrieved from settings.")
        return False

    theme = theme.strip().replace(" ", "_")
    if _themes.get(theme, None):
        f"Failed to create new gui theme: theme '{theme}' already exists."
        return False

    # Create new theme from default template.
    _new_theme: Dict[str, Any] = {theme: _template_theme}
    _themes.update(_new_theme)
    # Save new theme to the toml file.
    _themes.save()
    logger.debug(f"Created new gui theme from template: {theme}.")

    return True


def update_theme(theme: str, items: Dict[str, Any]) -> bool:
    _themes: Optional["Config"] = settings.configs.get_gui_themes()
    if not _themes:
        logger.error("Failed to update gui theme: the gui themes could not be retrieved from settings.")
        return False

    theme = theme.strip().replace(" ", "_")
    _selected_theme = _themes.get(theme, None)
    if not _selected_theme:
        logger.error(f"Failed to update gui theme: theme '{theme}' does not exist.")
        return False

    for key, value in items.items():
        if key in _selected_theme.keys():
            _selected_theme[key] = value
    _themes.update({theme: _selected_theme})

    _themes.save()
    logger.debug(f"Updated gui theme '{theme}' with values [{', '.join('{}={}'.format(*x) for x in items.items())}]")

    return True


def _get_template_theme() -> "Config":
    _config: Optional["Config"] = settings.configs.get_mumimo_config()
    if not _config:
        raise PluginError("Unable to get template theme: mumimo config could not be retrieved from settings.", logger=logger)

    _plugin_path = _config.get(MumimoCfgFields.SETTINGS.PLUGINS.PLUGINS_PATH, None)
    if not _plugin_path:
        raise PluginError("Unable to get template theme: mumimo config does not have a defined plugin path.")

    _theme_template_path = pathlib.Path.cwd() / _plugin_path / "builtin_core/resources/gui_custom_theme_template.toml"
    _theme_cfg: "Config" = Config(_theme_template_path)
    if _theme_cfg is None:
        raise PluginError(f"Unable to get template theme: gui custom theme template file is missing. Expected path: {_theme_template_path}")
    _theme_cfg.read()

    _template = _theme_cfg.get("template", None)
    if _template is None:
        raise PluginError("Unable to get template theme: 'template' section is missing in gui custom theme template file.")

    return _template


def _get_theme(theme: str) -> Optional["Config"]:
    if not theme:
        logger.error("Failed to get gui theme: no theme name provided.")
        return None

    _themes: Optional["Config"] = settings.configs.get_gui_themes()
    if not _themes:
        logger.error("Failed to get gui theme: the gui themes could not be retrieved from settings.")
        return None

    _theme = _themes.get(theme, None)
    if not _theme:
        logger.error(f"Failed to get gui theme: theme '{theme}' does not exist.")
        return None

    return _theme
