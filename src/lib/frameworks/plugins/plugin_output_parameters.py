from typing import List, Union, Optional, TYPE_CHECKING
from ..gui.gui import GUIFramework
from ....utils import mumble_utils
from ....constants import LogOutputIdentifiers
from .message_relay_definitions import MessageRelayDefinitions
import logging

if TYPE_CHECKING:
    from ...command import Command
    from pymumble_py3.channels import Channel
    from pymumble_py3.users import User


logger = logging.getLogger(__name__)


def output_me(messages: Union[str, List[str]], data: "Command") -> None:
    _me = mumble_utils.get_user_by_id(data.actor)
    if not _me:
        logger.error(
            f"[{LogOutputIdentifiers.PLUGINS_COMMANDS}]: '{data.command}' command display error: the user was not found with the provided id."
        )
        return
    GUIFramework.gui(
        text=messages,
        target_users=mumble_utils.get_user_by_id(data.actor),
        user_id=data.actor,
    )


def output_user(messages: Union[str, List[str]], data: "Command") -> None:
    _parameter = _get_parameter(data, MessageRelayDefinitions.USER)
    if _parameter is None:
        logger.error(
            f"[{LogOutputIdentifiers.PLUGINS_COMMANDS}]: '{data.command}' command display error: the '{MessageRelayDefinitions.USER}' "
            "parameter was not provided."
        )
        return
    _user = _get_user(data, _parameter)
    if not _user:
        logger.error(
            f"[{LogOutputIdentifiers.PLUGINS_COMMANDS}]: '{data.command}' command display error: the '{MessageRelayDefinitions.USER}' "
            "could not be retrieved."
        )
        return
    GUIFramework.gui(
        messages,
        target_users=_user,
        user_id=data.actor,
    )


def output_broadcast(messages: Union[str, List[str]], data: "Command") -> None:
    _all_channels: List["Channel"] = mumble_utils.get_all_channels()
    if not _all_channels:
        logger.error(f"[{LogOutputIdentifiers.PLUGINS_COMMANDS}]: '{data.command}' command display error: the channel tree could not be retrieved.")
        return
    GUIFramework.gui(
        messages,
        target_channels=_all_channels,
        user_id=data.actor,
    )


def output_users(messages: Union[str, List[str]], data: "Command") -> None:
    _parameter = _get_parameter(data, MessageRelayDefinitions.USERS)
    if _parameter is None:
        logger.error(
            f"[{LogOutputIdentifiers.PLUGINS_COMMANDS}]: '{data.command}' command display error: the '{MessageRelayDefinitions.USERS}' "
            "parameter was not provided."
        )
        return
    parameter_split = _parameter.split("=", 1)
    if len(parameter_split) != 2:
        GUIFramework.gui(
            f"'{data._command}' command display warning: an invalid list of user names was provided.",
            target_users=mumble_utils.get_user_by_id(data.actor),
        )
        return
    user_names = [user.strip().replace("_", " ") for user in parameter_split[1].split(",")]
    if not user_names:
        GUIFramework.gui(
            f"'{data._command}' command display warning: no users were provided.",
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
            f"'{data._command}' command display warning: cannot find specified user '{_user}'.",
            target_users=mumble_utils.get_user_by_id(data.actor),
        )
    GUIFramework.gui(
        messages,
        target_users=_found_users,
        user_id=data.actor,
    )


def output_channel(messages: Union[str, List[str]], data: "Command") -> None:
    _parameter = _get_parameter(data, MessageRelayDefinitions.CHANNEL)
    if _parameter is None:
        logger.error(
            f"[{LogOutputIdentifiers.PLUGINS_COMMANDS}]: '{data.command}' command display error: the '{MessageRelayDefinitions.CHANNEL}' "
            "parameter was not provided."
        )
        return
    _channel = _get_channel(data, _parameter)
    if not _channel:
        logger.error(f"[{LogOutputIdentifiers.PLUGINS_COMMANDS}]: '{data.command}' command display error: the channel could not be retrieved.")
        return
    GUIFramework.gui(
        messages,
        target_channels=_channel,
        user_id=data.actor,
    )


def output_mychannel(messages: Union[str, List[str]], data: "Command") -> None:
    _channel_user = mumble_utils.get_user_by_id(data.actor)
    if not _channel_user:
        return
    _channel_obj = mumble_utils.get_channel_by_user(_channel_user)
    if _channel_obj:
        GUIFramework.gui(
            messages,
            target_channels=_channel_obj,
            user_id=data.actor,
        )


def output_channels(messages: Union[str, List[str]], data: "Command") -> None:
    _parameter = _get_parameter(data, MessageRelayDefinitions.CHANNELS)
    if _parameter is None:
        logger.error(
            f"[{LogOutputIdentifiers.PLUGINS_COMMANDS}]: '{data.command}' command display error: the '{MessageRelayDefinitions.CHANNELS}' "
            "parameter was not provided."
        )
        return
    parameter_split = _parameter.split("=", 1)
    if len(parameter_split) != 2:
        GUIFramework.gui(
            f"'{data._command}' command display warning: an invalid list of channel names was provided.",
            target_users=mumble_utils.get_user_by_id(data.actor),
        )
        return

    channel_names = [channel.strip().replace("_", " ") for channel in parameter_split[1].split(",")]
    if not channel_names:
        GUIFramework.gui(
            f"'{data._command}' command display warning: no channel names were provided.",
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
            f"'{data._command}' command display warning: cannot find specified channel '{_channel}'.",
            target_users=mumble_utils.get_user_by_id(data.actor),
        )
    GUIFramework.gui(
        messages,
        target_channels=_found_channels,
        user_id=data.actor,
    )


def _get_parameter(data: "Command", parameter: str) -> Optional[str]:
    for param in data.parameters:
        param = param.strip()
        if param.startswith(parameter):
            return param
    return None


def _get_user(data: "Command", parameter: str) -> Optional["User"]:
    parameter_split = parameter.split("=", 1)
    if len(parameter_split) == 2:
        _search_term: str = parameter_split[1].strip().replace("_", " ")
        if not _search_term:
            GUIFramework.gui(
                f"'{data._command}' command display error: an invalid user name was provided.",
                target_users=mumble_utils.get_user_by_id(data.actor),
            )
            return
        _search_user: Optional["User"] = mumble_utils.get_user_by_name(_search_term)
        if _search_user is not None:
            return _search_user
        GUIFramework.gui(
            f"'{data._command}' command display error: cannot find specified user '{_search_term}'.",
            target_users=mumble_utils.get_user_by_id(data.actor),
        )
        return
    GUIFramework.gui(
        f"'{data._command}' command display error: a user name was not provided.",
        target_users=mumble_utils.get_user_by_id(data.actor),
    )


def _get_channel(data: "Command", parameter: str) -> Optional["Channel"]:
    parameter_split = parameter.split("=", 1)
    if len(parameter_split) == 2:
        _search_term: str = parameter_split[1].strip().replace("_", " ")
        if not _search_term:
            GUIFramework.gui(
                f"'{data._command}' command display error: an invalid channel name was provided.",
                target_users=mumble_utils.get_user_by_id(data.actor),
            )
            return
        _search_channel: Optional["Channel"] = mumble_utils.get_channel_by_name(_search_term)
        if _search_channel is not None:
            return _search_channel
        GUIFramework.gui(
            f"'{data._command}' command display error: cannot find specified channel '{_search_term}'.",
            target_users=mumble_utils.get_user_by_id(data.actor),
        )
        return
    GUIFramework.gui(
        f"'{data._command}' command display error: a channel name was not provided.",
        target_users=mumble_utils.get_user_by_id(data.actor),
    )
