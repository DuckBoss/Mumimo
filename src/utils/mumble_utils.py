import logging
from typing import TYPE_CHECKING, List, Optional

from ..settings import settings

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from pymumble_py3 import Mumble
    from pymumble_py3.channels import Channel
    from pymumble_py3.users import User

    from ..murmur_connection import MurmurConnection


def echo(text: str, target_type, user_id: Optional[int]) -> None:
    if None in (text, target_type):
        return
    if target_type == "channel":
        _channel: Optional["Channel"] = get_my_channel()
        if _channel is None:
            logger.warning("Channel object was not found: the current channel could not be retrieved.")
            return None
        _channel.send_text_message(text.strip())
        logger.debug(f"Echoed [Channel->{_channel['name']}]: {text.strip()}")
    elif target_type == "broadcast":
        _channels: List["Channel"] = get_all_channels()
        if not _channels:
            logger.warning("Channel objects were not found: the channel tree could not be retrieved.")
            return None
        for channel in _channels:
            channel.send_text_message(text.strip())
        logger.debug(f"Echoed [Broadcast]: {text.strip()}")
        return
    elif target_type == "me":
        if not isinstance(user_id, int):
            logger.warning("User object was not found: the user id must be a non-negative integer.")
            return None
        if user_id < 0:
            logger.warning("User object was not found: the user id must be a non-negative integer.")
            return None
        _user: Optional["User"] = get_user_by_id(user_id)
        if _user is None:
            logger.warning("User object was not found: user id not recognized.")
            return None
        _user.send_text_message(text.strip())
        logger.debug(f"Echoed [Me->{_user['name']}]: {text.strip()}")


def get_user_by_id(id: int) -> Optional["User"]:
    _inst: Optional["Mumble"] = get_connection_instance()
    if _inst is not None:
        try:
            return _inst.users[id]
        except KeyError:
            return None
    return None


def get_my_channel() -> Optional["Channel"]:
    _inst: Optional["Mumble"] = get_connection_instance()
    if _inst is not None:
        _myself = _inst.users.myself
        if _myself is not None:
            return _inst.channels[_myself["channel_id"]]
    return None


def get_all_channels() -> List["Channel"]:
    _channels: List["Channel"] = []
    _inst: Optional["Mumble"] = get_connection_instance()
    if _inst is not None:
        for _, channel in enumerate(_inst.channels.items()):
            _channel: "Channel" = channel[1]
            _channels.append(_channel)
        return _channels
    return []


def get_connection_instance() -> Optional["Mumble"]:
    _conn: Optional["MurmurConnection"] = settings.connection.get_murmur_connection()
    if _conn is not None:
        _inst = _conn.connection_instance
        if _inst is not None:
            return _inst
    return None
