import asyncio
import logging
import time
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

from pymumble_py3.channels import Channel
from pymumble_py3.errors import UnknownChannelError
from pymumble_py3.users import User

from sqlalchemy import select

from ..lib.database.models.permission_group import PermissionGroupTable
from ..lib.database.models.user import UserTable
from ..exceptions import ServiceError
from ..settings import settings
from ..constants import DefaultPermissionGroups, LogOutputIdentifiers

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from pymumble_py3 import Mumble

    from ..murmur_connection import MurmurConnection
    from ..services.database_service import DatabaseService


def echo(
    text: str,
    user_id: Optional[int] = None,
    delay: Optional[int] = None,
    target_channels: Optional[Union[List["Channel"], "Channel"]] = None,
    target_users: Optional[Union[List["User"], "User"]] = None,
    log_severity: int = logging.DEBUG,
    raw_text: Optional[str] = None,
) -> None:
    if text is None:
        logger.warning("Unable to echo message: 'text' value is missing.")
        return
    if target_channels is None:
        target_channels = []
    if target_users is None:
        target_users = []
    if isinstance(target_channels, Channel):
        target_channels = [target_channels]
    if isinstance(target_users, User):
        target_users = [target_users]
    if raw_text is None:
        raw_text = text

    if user_id:
        _user = get_user_by_id(user_id)
        if not _user:
            _user = "n/a"
        else:
            _user = _user["name"]
    else:
        _user = "Mumimo"

    _delay = 0
    if delay is not None and delay > 0:
        _delay = delay

    if target_channels:
        if _delay > 0:
            time.sleep(_delay)
        for channel in target_channels:
            channel.send_text_message(text.strip())
            logger.log(
                level=log_severity,
                msg=f"'{_user}' echoed [Channel->{channel['name']}]: {raw_text.strip()}",
            )
    elif target_users:
        if _delay > 0:
            time.sleep(_delay)
        for user in target_users:
            user.send_text_message(text.strip())
            logger.log(
                level=log_severity,
                msg=f"'{_user}' echoed [User->{user['name']}]: {raw_text.strip()}",
            )
    else:
        _channel: Optional["Channel"] = get_my_channel()
        if _channel is None:
            logger.warning("Channel object was not found: the current channel could not be retrieved.")
            return None
        if _delay > 0:
            time.sleep(_delay)
        _channel.send_text_message(text.strip())
        logger.log(
            level=log_severity,
            msg=f"'{_user}' echoed [Channel->{_channel['name']}]: {raw_text.strip()}",
        )


def get_user_by_id(id: int) -> Optional["User"]:
    _inst: Optional["Mumble"] = Management.get_connection_instance()
    if _inst is not None:
        try:
            return _inst.users[id]
        except KeyError:
            return None
    return None


def get_user_by_name(name: str) -> Optional["User"]:
    _inst: Optional["Mumble"] = Management.get_connection_instance()
    if _inst is not None:
        try:
            for user in _inst.users.values():
                if user["name"] == name:
                    return user
        except KeyError:
            return None
    return None


def get_channel_by_user(user: Union["User", str]) -> Optional["Channel"]:
    if isinstance(user, str):
        _user: Optional["User"] = get_user_by_name(user)
        if _user is None:
            return None
    else:
        _user: Optional["User"] = user

    _inst: Optional["Mumble"] = Management.get_connection_instance()
    if _inst is not None:
        try:
            return _inst.channels[_user["channel_id"]]
        except KeyError:
            return None
    return None


def get_my_channel() -> Optional["Channel"]:
    _inst: Optional["Mumble"] = Management.get_connection_instance()
    if _inst is not None:
        _myself = _inst.users.myself
        if _myself is not None:
            return _inst.channels[_myself["channel_id"]]
    return None


def get_all_channels() -> List["Channel"]:
    _channels: List["Channel"] = []
    _inst: Optional["Mumble"] = Management.get_connection_instance()
    if _inst is not None:
        for _, channel in enumerate(_inst.channels.items()):
            _channel: "Channel" = channel[1]
            _channels.append(_channel)
        return _channels
    return []


def get_channel_by_name(channel_name: str) -> Optional["Channel"]:
    _inst: Optional["Mumble"] = Management.get_connection_instance()
    if _inst is not None:
        try:
            return _inst.channels.find_by_name(channel_name.strip())
        except UnknownChannelError:
            return None
    return None


class Management:
    class UserManagement:
        @staticmethod
        async def add_user(actor: Dict[str, Any]) -> None:
            _db_service: Optional["DatabaseService"] = settings.database.get_database_instance()
            if not _db_service:
                raise ServiceError("Unable to add new user: the database service could not retrieve the database instance.", logger=logger)

            _actor: Optional["User"] = get_user_by_name(actor["name"])
            if not _actor:
                raise ServiceError("Unable to add new user: the user could not be retrieved from the actor name.")

            async with _db_service.session() as session:
                _user_query = await session.execute(select(UserTable).filter_by(name=_actor["name"]))
                _user_info: Optional[UserTable] = _user_query.scalar()
                if _user_info:
                    logger.warning(f"Unable to add new user: the user '{_actor['name']}' already exists in the database.")
                else:
                    _user_info = UserTable(name=actor["name"])
                    _permission_query = await session.execute(select(PermissionGroupTable).filter_by(name=DefaultPermissionGroups.DEFAULT_GUEST))
                    _permission_info: Optional[PermissionGroupTable] = _permission_query.scalar()
                    if not _permission_info:
                        raise ServiceError(
                            f"Unable to add new user: the default permission '{DefaultPermissionGroups.DEFAULT_GUEST}' is not in the database."
                        )
                    _user_info.permission_groups.append(_permission_info)
                    session.add(_user_info)
                    await session.commit()
                    logger.debug(f"[{LogOutputIdentifiers.DB_USERS}]: Added new user to the database -> [{_actor['name']}]")

            _client_state = settings.state.get_client_state()
            if not _client_state:
                raise ServiceError("Unable to add new user: the client state could not be retrieved.")
            _server_state = _client_state.server_properties.state
            if _server_state.add_user(_actor):
                logger.debug(f"Added new user '{_actor['name']}' to the server state.")
            else:
                logger.error(f"Unable to add new user '{_actor['name']}' to the server state.")
                await session.rollback()
                return

        @staticmethod
        async def remove_user(actor: Dict[str, Any]) -> None:
            _db_service: Optional["DatabaseService"] = settings.database.get_database_instance()
            if not _db_service:
                raise ServiceError("Unable to remove user: the database service could not retrieve the database instance.", logger=logger)

            _actor: Optional["User"] = get_user_by_name(actor["name"])
            if not _actor:
                raise ServiceError("Unable to remove user: the user could not be retrieved from the actor name.")

            async with _db_service.session() as session:
                _user_query = await session.execute(select(UserTable).filter_by(name=_actor["name"]))
                _user_info: Optional[UserTable] = _user_query.scalar()
                if not _user_info:
                    logger.warning(f"Unable to remove user: the user '{_actor['name']}' does not exist in the database.")
                else:
                    _user_info = UserTable(name=actor["name"])
                    await session.delete(_user_info)
                    await session.commit()
                    logger.debug(f"[{LogOutputIdentifiers.DB_USERS}]: Removed user from the database -> [{_actor['name']}]")

            _client_state = settings.state.get_client_state()
            if not _client_state:
                raise ServiceError("Unable to remove user: the client state could not be retrieved.")
            _server_state = _client_state.server_properties.state
            if _server_state.remove_user(_actor):
                logger.debug(f"Removed user '{_actor['name']}' to the server state.")
            else:
                logger.error(f"Unable to remove user '{_actor['name']}' from the server state.")
                await session.rollback()
                return

    @staticmethod
    def get_connection_instance() -> Optional["Mumble"]:
        _conn: Optional["MurmurConnection"] = settings.connection.get_murmur_connection()
        if _conn is not None:
            _inst = _conn.connection_instance
            if _inst is not None:
                return _inst
        return None

    @staticmethod
    async def exit_server():
        import sys

        logger.info("Gracefully exiting Mumimo client...")
        all_plugins: Dict[str, Any] = settings.plugins.get_registered_plugins()
        logger.info("Gracefully exiting plugins...")
        for _, plugin in all_plugins.items():
            plugin.quit()
        _murmur_instance = settings.connection.get_murmur_connection()
        if _murmur_instance is not None:
            logger.info("Disconnecting from Murmur server...")
            if _murmur_instance.stop():
                logger.info("Disconnected from Murmur server.")
            _db_service = settings.database.get_database_instance()
            if _db_service:
                await _db_service.close(clean=True)
        _async_runners = await asyncio.gather()
        for runner in _async_runners:
            runner.cancel("Mumimo shutting down.")
        logger.info("Mumimo client closed.")
        sys.exit(0)
