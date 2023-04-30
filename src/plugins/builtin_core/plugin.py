import logging
import time
from typing import TYPE_CHECKING, List, Optional

from pymumble_py3.channels import Channel
from pymumble_py3.users import User

from src.constants import LogOutputIdentifiers
from src.lib.frameworks.plugins.plugin import PluginBase
from src.settings import settings
from src.utils import mumble_utils
from src.lib.frameworks.gui.gui import GUIFramework

from .utility.constants import ParameterDefinitions
from .utility import theme_utils

logger = logging.getLogger(__name__)


if TYPE_CHECKING:
    from src.lib.command import Command


class Plugin(PluginBase):
    command = PluginBase.makeCommandRegister()

    def __init__(self, plugin_name: str) -> None:
        self._plugin_name = plugin_name
        logger.debug(f"[{LogOutputIdentifiers.PLUGINS}]: Initializing plugin: '{self._plugin_name}'")
        super().__init__(self._plugin_name)

        self.initialize_parameters(settings.commands.callbacks.get_callbacks(self._plugin_name))
        logger.debug(f"[{LogOutputIdentifiers.PLUGINS}]: Plugin '{self._plugin_name}' ready.")

    @command(
        parameters=ParameterDefinitions.Echo.get_definitions(),
    )
    def echo(self, data: "Command") -> None:
        # Example:
        # !echo "hello, channel!"  -> Without a target parameter, by default echoes to the bot channel.
        # !echo.delay=5 "hello, after delay!"  -> Specify a delay of 5 seconds before sending the message to the bot channel.
        #
        # Display types:
        # !echo.me "hello, me!"  -> Echoes the message to the sender of the command.
        # !echo.mychannel "hello, my channel!"  -> Echoes the message to the channel the sender is in.
        # !echo.channel=custom_channel "hello, specified channel!"  -> Echoes the message to the specified channel.
        # !echo.channels=channel1,channel2 "hello, specified channels!"  -> Echoes the message to the specified channels.
        # !echo.user=username "hello, specified user!"  -> Echoes the message to the specified user.
        # !echo.users=username1,username2 "hello, specified users!"  -> Echoes the message to the specified users.
        # !echo.broadcast "hello, everyone!"  -> Echoes the message to all channels in the server.
        _parameters = self.verify_parameters(self.echo.__name__, data)
        if _parameters is None:
            return

        _delay = _parameters.get(ParameterDefinitions.Echo.DELAY, None)
        if _delay and _delay > 0:
            time.sleep(_delay)

        if not any(x in self.command_parameters[self.echo.__name__] for x in _parameters.keys()):
            if not data.message.strip():
                GUIFramework.gui(
                    f"'{data.command}' command error: a target channel must be specified when no parameters are used.",
                    target_users=mumble_utils.get_user_by_id(data.actor),
                    user_id=data.actor,
                )
                return
            _channel = mumble_utils.get_my_channel()
            GUIFramework.gui(
                data.message,
                target_channels=_channel,
                user_id=data.actor,
            )

    @command(
        parameters=ParameterDefinitions.Move.get_definitions(),
        exclusive_parameters=ParameterDefinitions.Move.get_definitions(),
    )
    def move(self, data: "Command") -> None:
        # Example:
        # !move "channel name"  -> Without a target parameter, by default moves the bot to the specified channel.
        # !move.channel=channel_name  -> Moves the bot to the specified channel.
        # !move.to_user=user_name  -> Moves the bot to the specified users channel.
        # !move.to_me  -> Moves the bot to the command senders channel.
        _parameters = self.verify_parameters(self.move.__name__, data)
        if _parameters is None:
            return

        if not any(x in self.command_parameters[self.move.__name__] for x in _parameters.keys()):
            _target_channel = data.message.strip().replace("_", " ")
            if not _target_channel:
                GUIFramework.gui(
                    f"'{data._command}' command error: a target channel must be specified when no parameters are used.",
                    target_users=mumble_utils.get_user_by_id(data.actor),
                    user_id=data.actor,
                )
                return
            _search_channel: Optional["Channel"] = mumble_utils.get_channel_by_name(_target_channel)
            if _search_channel is None:
                GUIFramework.gui(
                    f"'{data._command}' command error: cannot find specified channel '{_target_channel}'.",
                    target_users=mumble_utils.get_user_by_id(data.actor),
                    user_id=data.actor,
                )
                return
            _search_channel.move_in()

    @command(
        parameters=ParameterDefinitions.Themes.get_definitions(),
        exclusive_parameters=ParameterDefinitions.Themes.get_definitions(),
        parameters_required=True,
    )
    def themes(self, data: "Command") -> None:
        # Example:
        # !themes.list  -> Displays a list of the available gui themes.
        # !themes.switch "theme_name" -> Switches the gui theme to the selected theme.
        # !themes.new "theme_name"  -> Creates a new theme from a template theme.
        # !themes.delete "theme_name"  -> Deletes the specified theme, and falls back to a default theme if it was in use.
        # !themes.show "theme_name"  -> Shows the config data for the specified theme.
        # !themes.update="theme_name" item1=value1...  -> Updates a specified theme with the specified new values.
        # !themes.reset "theme_name" -> Resets the specified theme back to default options.
        # !themes.resetall -> Resets all the themes back to the default set of themes and options.

        _parameters = self.verify_parameters(self.themes.__name__, data)
        if _parameters is None:
            return

    def _parameter_themes_list(self, data: "Command", parameter: str) -> None:
        _theme_list = theme_utils.list_themes()
        if not _theme_list:
            logger.error(f"[{LogOutputIdentifiers.PLUGINS_COMMANDS}]: '{data.command}' command error: the themes list could not be retrieved.")
            return
        _msgs: List[str] = ["Available themes: "]
        for idx, theme in enumerate(_theme_list):
            _msgs.append(f"{idx+1}) {theme}")
        GUIFramework.gui(
            text=_msgs,
            target_users=mumble_utils.get_user_by_id(data.actor),
        )

    def _parameter_themes_switch(self, data: "Command", parameter: str) -> None:
        _new_theme = data.message.strip()
        _available_themes = theme_utils.list_themes()
        if not _new_theme or _new_theme not in _available_themes:
            _msgs: List[str] = [
                "Invalid theme. ",
                "Here are the available themes to choose from: ",
            ]
            for idx, theme in enumerate(theme_utils.list_themes()):
                _msgs.append(f"{idx+1}) {theme}")
            GUIFramework.gui(
                text=_msgs,
                target_users=mumble_utils.get_user_by_id(data.actor),
            )
            return
        _switched_themes = theme_utils.switch_themes(_new_theme)
        if not _switched_themes:
            logger.error(f"[{LogOutputIdentifiers.PLUGINS_COMMANDS}]: '{data.command}' command error: the theme could not be switched.")
            return
        GUIFramework.gui(
            text=f"Switched theme to: {data.message.strip()}",
            target_users=mumble_utils.get_user_by_id(data.actor),
        )

    def _parameter_themes_new(self, data: "Command", parameter: str) -> None:
        _new_theme = data.message.strip().replace(" ", "_")
        if not theme_utils.new_theme(_new_theme):
            logger.error(f"[{LogOutputIdentifiers.PLUGINS_COMMANDS}]: '{data.command}' command error: failed to create theme.")
            GUIFramework.gui(
                text=f"Failed to create new theme: {_new_theme}",
                target_users=mumble_utils.get_user_by_id(data.actor),
            )
            return
        GUIFramework.gui(
            text=f"Created new theme: {_new_theme}",
            target_users=mumble_utils.get_user_by_id(data.actor),
        )

    def _parameter_themes_reset(self, data: "Command", parameter: str) -> None:
        _selected_theme = data.message.strip().replace(" ", "_")
        if not theme_utils.reset_theme(_selected_theme):
            logger.error(f"[{LogOutputIdentifiers.PLUGINS_COMMANDS}]: '{data.command}' command error: failed to reset theme.")
            GUIFramework.gui(
                text=f"Failed to reset theme: {_selected_theme}",
                target_users=mumble_utils.get_user_by_id(data.actor),
            )
            return
        GUIFramework.gui(
            text=f"Resetted selected theme: {_selected_theme}",
            target_users=mumble_utils.get_user_by_id(data.actor),
        )

    def _parameter_themes_resetall(self, data: "Command", parameter: str) -> None:
        if not theme_utils.reset_all_themes():
            logger.error(f"[{LogOutputIdentifiers.PLUGINS_COMMANDS}]: '{data.command}' command error: failed to reset all themes.")
            GUIFramework.gui(
                text="Failed to reset all themes.",
                target_users=mumble_utils.get_user_by_id(data.actor),
            )
            return
        GUIFramework.gui(
            text="Resetted all themes to defaults.",
            target_users=mumble_utils.get_user_by_id(data.actor),
        )

    def _parameter_themes_delete(self, data: "Command", parameter: str) -> None:
        _delete_theme = data.message.strip().replace(" ", "_")
        if not theme_utils.delete_theme(_delete_theme):
            logger.error(f"[{LogOutputIdentifiers.PLUGINS_COMMANDS}]: '{data.command}' command error: failed to delete theme.")
            GUIFramework.gui(
                text=f"Failed to delete theme: {_delete_theme}",
                target_users=mumble_utils.get_user_by_id(data.actor),
            )
            return
        GUIFramework.gui(
            text=f"Deleted theme: {_delete_theme}",
            target_users=mumble_utils.get_user_by_id(data.actor),
        )

    def _parameter_themes_update(self, data: "Command", parameter: str) -> None:
        parameter_split = parameter.split("=", 1)
        if not len(parameter_split) == 2:
            GUIFramework.gui(
                f"'{data._command}' command error: a user name was not provided.",
                target_users=mumble_utils.get_user_by_id(data.actor),
            )
            return

        _theme_name: str = parameter_split[1].strip().replace("_", " ")
        if not _theme_name:
            GUIFramework.gui(
                f"'{data._command}' command error: an invalid theme name was provided.",
                target_users=mumble_utils.get_user_by_id(data.actor),
            )
            return

        _update_items = data.message.strip().replace(" ", "_")
        if not _update_items:
            GUIFramework.gui(
                f"'{data._command}' command error: invalid update values provided. Update values must follow the format: 'item1=value1, item2=value2, ...'",
                target_users=mumble_utils.get_user_by_id(data.actor),
            )
            return
        _update_items_split = _update_items.split(",")
        _update_items_pairs = {}
        for item in _update_items_split:
            _pairs_split = item.split("=", 1)
            if len(_pairs_split) != 2:
                GUIFramework.gui(
                    f"'{data._command}' command error: invalid update values provided. Update values must follow the format: 'item1=value1, item2=value2, ...'",
                    target_users=mumble_utils.get_user_by_id(data.actor),
                )
                return
            _key, _value = _pairs_split[0], _pairs_split[1]
            _update_items_pairs[_key] = _value

        _theme_updated: bool = theme_utils.update_theme(_theme_name, _update_items_pairs)
        if not _theme_updated:
            GUIFramework.gui(
                f"'{data._command}' command error: unable to update theme. Ensure the theme exists and valid values are provided.",
                target_users=mumble_utils.get_user_by_id(data.actor),
            )
            return
        GUIFramework.gui(
            f"Updated theme: {_theme_name}",
            target_users=mumble_utils.get_user_by_id(data.actor),
        )

    def _parameter_themes_show(self, data: "Command", parameter: str) -> None:
        _theme_name = data.message.strip().replace(" ", "_")
        _selected_theme = theme_utils._get_theme(_theme_name)
        if not _selected_theme:
            logger.error(f"[{LogOutputIdentifiers.PLUGINS_COMMANDS}]: '{data.command}' command error: failed to show theme.")
            GUIFramework.gui(
                text=f"Failed to show theme: {_theme_name}",
                target_users=mumble_utils.get_user_by_id(data.actor),
            )
            return
        _msgs = [f"[{_theme_name}]"]
        for key, value in _selected_theme.items():
            _msgs.append(f"{key}={value}")
        GUIFramework.gui(
            text=_msgs,
            target_users=mumble_utils.get_user_by_id(data.actor),
        )

    def _parameter_move_to_me(self, data: "Command", parameter: str) -> Optional["User"]:
        _me = mumble_utils.get_user_by_id(data.actor)
        if not _me:
            logger.error(f"[{LogOutputIdentifiers.PLUGINS_COMMANDS}]: '{data.command}' command error: the user could not be retrieved.")
            return
        _my_channel: Optional["Channel"] = mumble_utils.get_channel_by_user(_me)
        if not _my_channel:
            GUIFramework.gui(
                f"'{data._command}' command error: unable to find the channel '{_me['name']}' belongs to.",
                target_users=mumble_utils.get_user_by_id(data.actor),
                user_id=data.actor,
            )
            return
        _my_channel.move_in()
        return

    def _parameter_move_to_user(self, data: "Command", parameter: str) -> Optional["User"]:
        _user = self._get_user(data, parameter)
        if not _user:
            logger.error(f"[{LogOutputIdentifiers.PLUGINS_COMMANDS}]: '{data.command}' command error: the user could not be retrieved.")
            return
        _user_channel: Optional["Channel"] = mumble_utils.get_channel_by_user(_user)
        if not _user_channel:
            GUIFramework.gui(
                f"'{data._command}' command error: unable to find the channel '{_user['name']}' belongs to.",
                target_users=mumble_utils.get_user_by_id(data.actor),
                user_id=data.actor,
            )
            return
        _user_channel.move_in()

    def _parameter_move_to_channel(self, data: "Command", parameter: str) -> Optional["Channel"]:
        _channel = self._get_channel(data, parameter)
        if not _channel:
            return
        _channel.move_in()

    def _parameter_echo_me(self, data: "Command", parameter: str) -> None:
        _me = mumble_utils.get_user_by_id(data.actor)
        if not _me:
            logger.error(f"[{LogOutputIdentifiers.PLUGINS_COMMANDS}]: '{data.command}' command error: the user was not found with the provided id.")
            return
        GUIFramework.gui(
            data.message,
            target_users=_me,
            user_id=data.actor,
        )

    def _parameter_echo_broadcast(self, data: "Command", parameter: str) -> None:
        _all_channels: List["Channel"] = mumble_utils.get_all_channels()
        if not _all_channels:
            logger.error(f"[{LogOutputIdentifiers.PLUGINS_COMMANDS}]: '{data.command}' command error: the channel tree could not be retrieved.")
            return
        GUIFramework.gui(
            data.message,
            target_channels=_all_channels,
            user_id=data.actor,
        )

    def _parameter_echo_user(self, data: "Command", parameter: str) -> None:
        _user = self._get_user(data, parameter)
        if not _user:
            logger.error(f"[{LogOutputIdentifiers.PLUGINS_COMMANDS}]: '{data.command}' command error: the user could not be retrieved.")
            return
        GUIFramework.gui(
            data.message,
            target_users=_user,
            user_id=data.actor,
        )

    def _parameter_echo_users(self, data: "Command", parameter: str) -> None:
        parameter_split = parameter.split("=", 1)
        if len(parameter_split) == 2:
            user_names = [user.strip().replace("_", " ") for user in parameter_split[1].split(",")]
            if not user_names:
                GUIFramework.gui(
                    f"'{data._command}' command warning: no users were provided.",
                    target_users=mumble_utils.get_user_by_id(data.actor),
                )
                return
            _found_users: List["User"] = []
            for _user in user_names:
                if not _user:
                    continue
                _search_user: Optional["User"] = mumble_utils.get_user_by_name(_user)
                if _search_user is not None:
                    _found_users.append(_search_user)
                    continue
                GUIFramework.gui(
                    f"'{data._command}' command warning: cannot find specified user '{_user}'.",
                    target_users=mumble_utils.get_user_by_id(data.actor),
                )
            GUIFramework.gui(
                data.message,
                target_users=_found_users,
                user_id=data.actor,
            )
            return
        GUIFramework.gui(
            f"'{data._command}' command warning: an invalid list of user names was provided.",
            target_users=mumble_utils.get_user_by_id(data.actor),
        )

    def _parameter_echo_channel(self, data: "Command", parameter: str) -> None:
        _channel = self._get_channel(data, parameter)
        if not _channel:
            logger.error(f"[{LogOutputIdentifiers.PLUGINS_COMMANDS}]: '{data.command}' command error: the channel could not be retrieved.")
            return
        GUIFramework.gui(
            data.message,
            target_channels=_channel,
            user_id=data.actor,
        )

    def _parameter_echo_mychannel(self, data: "Command", parameter: str) -> None:
        _channel_user = mumble_utils.get_user_by_id(data.actor)
        if not _channel_user:
            return
        _channel_obj = mumble_utils.get_channel_by_user(_channel_user)
        if _channel_obj:
            GUIFramework.gui(
                data.message,
                target_channels=_channel_obj,
                user_id=data.actor,
            )

    def _parameter_echo_channels(self, data: "Command", parameter: str) -> None:
        parameter_split = parameter.split("=", 1)
        if len(parameter_split) == 2:
            channel_names = [channel.strip().replace("_", " ") for channel in parameter_split[1].split(",")]
            if not channel_names:
                GUIFramework.gui(
                    f"'{data._command}' command warning: no channel names were provided.",
                    target_users=mumble_utils.get_user_by_id(data.actor),
                )
                return
            _found_channels: List["Channel"] = []
            for _channel in channel_names:
                if not _channel:
                    continue
                _search_channel: Optional["Channel"] = mumble_utils.get_channel_by_name(_channel)
                if _search_channel is not None:
                    _found_channels.append(_search_channel)
                    continue
                GUIFramework.gui(
                    f"'{data._command}' command warning: cannot find specified channel '{_channel}'.",
                    target_users=mumble_utils.get_user_by_id(data.actor),
                )
            GUIFramework.gui(
                data.message,
                target_channels=_found_channels,
                user_id=data.actor,
            )
            return
        GUIFramework.gui(
            f"'{data._command}' command warning: an invalid list of channel names was provided.",
            target_users=mumble_utils.get_user_by_id(data.actor),
        )

    def _parameter_echo_delay(self, data: "Command", parameter: str) -> Optional[int]:
        parameter_split = parameter.split("=", 1)
        if len(parameter_split) == 2:
            try:
                _delay = int(parameter_split[1])
                if _delay < 0:
                    raise TypeError()
                return _delay
            except ValueError:
                GUIFramework.gui(
                    f"'{data._command}' command warning: the 'delay' parameter must be a non-negative number.",
                    target_users=mumble_utils.get_user_by_id(data.actor),
                )
                return
            except TypeError:
                GUIFramework.gui(
                    f"'{data._command}' command warning: the 'delay' parameter must be a non-negative number.",
                    target_users=mumble_utils.get_user_by_id(data.actor),
                )
                return
        GUIFramework.gui(
            f"'{data._command}' command warning: an invalid 'delay' value was provided.",
            target_users=mumble_utils.get_user_by_id(data.actor),
        )

    def _get_user(self, data: "Command", parameter: str) -> Optional["User"]:
        parameter_split = parameter.split("=", 1)
        if len(parameter_split) == 2:
            _search_term: str = parameter_split[1].strip().replace("_", " ")
            if not _search_term:
                GUIFramework.gui(
                    f"'{data._command}' command error: an invalid user name was provided.",
                    target_users=mumble_utils.get_user_by_id(data.actor),
                )
                return
            _search_user: Optional["User"] = mumble_utils.get_user_by_name(_search_term)
            if _search_user is not None:
                return _search_user
            GUIFramework.gui(
                f"'{data._command}' command error: cannot find specified user '{_search_term}'.",
                target_users=mumble_utils.get_user_by_id(data.actor),
            )
            return
        GUIFramework.gui(
            f"'{data._command}' command error: a user name was not provided.",
            target_users=mumble_utils.get_user_by_id(data.actor),
        )

    def _get_channel(self, data: "Command", parameter: str) -> Optional["Channel"]:
        parameter_split = parameter.split("=", 1)
        if len(parameter_split) == 2:
            _search_term: str = parameter_split[1].strip().replace("_", " ")
            if not _search_term:
                GUIFramework.gui(
                    f"'{data._command}' command error: an invalid channel name was provided.",
                    target_users=mumble_utils.get_user_by_id(data.actor),
                )
                return
            _search_channel: Optional["Channel"] = mumble_utils.get_channel_by_name(_search_term)
            if _search_channel is not None:
                return _search_channel
            GUIFramework.gui(
                f"'{data._command}' command error: cannot find specified channel '{_search_term}'.",
                target_users=mumble_utils.get_user_by_id(data.actor),
            )
            return
        GUIFramework.gui(
            f"'{data._command}' command error: a channel name was not provided.",
            target_users=mumble_utils.get_user_by_id(data.actor),
        )
