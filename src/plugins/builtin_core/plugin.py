import logging
import time
from typing import TYPE_CHECKING, List, Optional, Union

from pymumble_py3.channels import Channel
from pymumble_py3.users import User

from src.constants import LogOutputIdentifiers
from src.lib.frameworks.plugins.plugin import PluginBase
from src.settings import settings
from src.utils import mumble_utils

from .utility.constants import ParameterDefinitions

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

        if _parameters.get(ParameterDefinitions.Echo.BROADCAST, False):
            _all_channels: List["Channel"] = mumble_utils.get_all_channels()
            if not _all_channels:
                logger.warning(
                    f"[{LogOutputIdentifiers.PLUGINS_COMMANDS}]: '{data.command}' command warning: the channel tree could not be retrieved."
                )
            mumble_utils.echo(
                data.message,
                target_channels=_all_channels,
                user_id=data.actor,
            )

        if _parameters.get(ParameterDefinitions.Echo.ME, False):
            _me = mumble_utils.get_user_by_id(data.actor)
            if not _me:
                logger.warning(
                    f"[{LogOutputIdentifiers.PLUGINS_COMMANDS}]: '{data.command}' command warning: the user was not found with the provided id."
                )
            mumble_utils.echo(
                data.message,
                target_users=_me,
                user_id=data.actor,
            )

        _user: Optional["User"] = _parameters.get(ParameterDefinitions.Echo.USER, None)
        if _user:
            mumble_utils.echo(
                data.message,
                target_users=_user,
                user_id=data.actor,
            )

        _users: Optional[List["User"]] = _parameters.get(ParameterDefinitions.Echo.USERS, [])
        if _users:
            mumble_utils.echo(
                data.message,
                target_users=_users,
                user_id=data.actor,
            )

        _channel: Optional["Channel"] = _parameters.get(ParameterDefinitions.Echo.CHANNEL, None)
        if _channel:
            mumble_utils.echo(
                data.message,
                target_channels=_channel,
                user_id=data.actor,
            )

        _channels: Optional[List["Channel"]] = _parameters.get(ParameterDefinitions.Echo.CHANNELS, [])
        if _channels:
            mumble_utils.echo(
                data.message,
                target_channels=_channels,
                user_id=data.actor,
            )

        if not any(x in self.command_parameters[self.echo.__name__] for x in _parameters.keys()):
            if not data.message.strip():
                mumble_utils.echo(
                    f"'{data.command}' command error: a target channel must be specified when no parameters are used.",
                    target_users=mumble_utils.get_user_by_id(data.actor),
                    user_id=data.actor,
                )
                return
            if not _channel:
                _channel = mumble_utils.get_my_channel()
                mumble_utils.echo(
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
            _target_channel = data.message.strip()
            if not _target_channel:
                mumble_utils.echo(
                    f"'{data._command}' command error: a target channel must be specified when no parameters are used.",
                    target_users=mumble_utils.get_user_by_id(data.actor),
                    user_id=data.actor,
                )
                return
            _parameters[ParameterDefinitions.Move.TO_CHANNEL] = _target_channel

        _channel: Optional[Union["Channel", str]] = _parameters.get(ParameterDefinitions.Move.TO_CHANNEL, None)
        if isinstance(_channel, Channel):
            _channel.move_in()
            return
        elif isinstance(_channel, str):
            _channel = _channel.strip().replace("_", " ")
            _search_channel: Optional["Channel"] = mumble_utils.get_channel_by_name(_channel)
            if _search_channel is None:
                mumble_utils.echo(
                    f"'{data._command}' command error: cannot find specified channel '{_channel}'.",
                    target_users=mumble_utils.get_user_by_id(data.actor),
                    user_id=data.actor,
                )
                return
            _search_channel.move_in()
            return

        _user: Optional["User"] = _parameters.get(ParameterDefinitions.Move.TO_USER, None)
        if _user:
            _user_channel: Optional["Channel"] = mumble_utils.get_channel_by_user(_user)
            if not _user_channel:
                mumble_utils.echo(
                    f"'{data._command}' command error: unable to find the channel '{_user['name']}' belongs to.",
                    target_users=mumble_utils.get_user_by_id(data.actor),
                    user_id=data.actor,
                )
                return
            _user_channel.move_in()
            return

        _me: Optional["User"] = _parameters.get(ParameterDefinitions.Move.TO_ME, None)
        if _me:
            _my_channel: Optional["Channel"] = mumble_utils.get_channel_by_user(_me)
            if not _my_channel:
                mumble_utils.echo(
                    f"'{data._command}' command error: unable to find the channel '{_me['name']}' belongs to.",
                    target_users=mumble_utils.get_user_by_id(data.actor),
                    user_id=data.actor,
                )
                return
            _my_channel.move_in()
            return

    def _parameter_move_to_me(self, data: "Command", parameter: str) -> Optional["User"]:
        return mumble_utils.get_user_by_id(data.actor)

    def _parameter_move_to_user(self, data: "Command", parameter: str) -> Optional["User"]:
        return self._get_user(data, parameter)

    def _parameter_move_to_channel(self, data: "Command", parameter: str) -> Optional["Channel"]:
        return self._get_channel(data, parameter)

    def _parameter_echo_me(self, data: "Command", parameter: str) -> bool:
        return True

    def _parameter_echo_broadcast(self, data: "Command", parameter: str) -> bool:
        return True

    def _parameter_echo_user(self, data: "Command", parameter: str) -> Optional["User"]:
        return self._get_user(data, parameter)

    def _parameter_echo_users(self, data: "Command", parameter: str) -> Optional[List["User"]]:
        parameter_split = parameter.split("=", 1)
        if len(parameter_split) == 2:
            user_names = [user.strip().replace("_", " ") for user in parameter_split[1].split(",")]
            if not user_names:
                mumble_utils.echo(
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
                mumble_utils.echo(
                    f"'{data._command}' command warning: cannot find specified user '{_user}'.",
                    target_users=mumble_utils.get_user_by_id(data.actor),
                )
            return _found_users
        mumble_utils.echo(
            f"'{data._command}' command warning: an invalid list of user names was provided.",
            target_users=mumble_utils.get_user_by_id(data.actor),
        )

    def _parameter_echo_channel(self, data: "Command", parameter: str) -> Optional["Channel"]:
        return self._get_channel(data, parameter)

    def _parameter_echo_channels(self, data: "Command", parameter: str) -> Optional[List["Channel"]]:
        parameter_split = parameter.split("=", 1)
        if len(parameter_split) == 2:
            channel_names = [channel.strip().replace("_", " ") for channel in parameter_split[1].split(",")]
            if not channel_names:
                mumble_utils.echo(
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
                mumble_utils.echo(
                    f"'{data._command}' command warning: cannot find specified channel '{_channel}'.",
                    target_users=mumble_utils.get_user_by_id(data.actor),
                )
            return _found_channels
        mumble_utils.echo(
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
                mumble_utils.echo(
                    f"'{data._command}' command warning: the 'delay' parameter must be a non-negative number.",
                    target_users=mumble_utils.get_user_by_id(data.actor),
                )
                return
            except TypeError:
                mumble_utils.echo(
                    f"'{data._command}' command warning: the 'delay' parameter must be a non-negative number.",
                    target_users=mumble_utils.get_user_by_id(data.actor),
                )
                return
        mumble_utils.echo(
            f"'{data._command}' command warning: an invalid 'delay' value was provided.",
            target_users=mumble_utils.get_user_by_id(data.actor),
        )

    def _get_user(self, data: "Command", parameter: str):
        parameter_split = parameter.split("=", 1)
        if len(parameter_split) == 2:
            _search_term: str = parameter_split[1].strip().replace("_", " ")
            if not _search_term:
                mumble_utils.echo(
                    f"'{data._command}' command warning: an invalid user name was provided.",
                    target_users=mumble_utils.get_user_by_id(data.actor),
                )
                return
            _search_user: Optional["User"] = mumble_utils.get_user_by_name(_search_term)
            if _search_user is not None:
                return _search_user
            mumble_utils.echo(
                f"'{data._command}' command warning: cannot find specified user '{_search_term}'.",
                target_users=mumble_utils.get_user_by_id(data.actor),
            )
            return
        mumble_utils.echo(
            f"'{data._command}' command warning: a user name was not provided.",
            target_users=mumble_utils.get_user_by_id(data.actor),
        )

    def _get_channel(self, data: "Command", parameter: str):
        parameter_split = parameter.split("=", 1)
        if len(parameter_split) == 2:
            _search_term: str = parameter_split[1].strip().replace("_", " ")
            if not _search_term:
                mumble_utils.echo(
                    f"'{data._command}' command warning: an invalid channel name was provided.",
                    target_users=mumble_utils.get_user_by_id(data.actor),
                )
                return
            _search_channel: Optional["Channel"] = mumble_utils.get_channel_by_name(_search_term)
            if _search_channel is not None:
                return _search_channel
            mumble_utils.echo(
                f"'{data._command}' command warning: cannot find specified channel '{_search_term}'.",
                target_users=mumble_utils.get_user_by_id(data.actor),
            )
            return
        mumble_utils.echo(
            f"'{data._command}' command warning: a channel name was not provided.",
            target_users=mumble_utils.get_user_by_id(data.actor),
        )
