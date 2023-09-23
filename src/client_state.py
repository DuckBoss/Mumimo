import asyncio
import logging
from enum import Enum
from typing import TYPE_CHECKING, Optional, Dict, Union, Any

from .utils import mumble_utils
from .constants import LogOutputIdentifiers


logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from pymumble_py3.mumble import Mumble
    from pymumble_py3.users import User
    from pymumble_py3.channels import Channel


class ClientState:
    class AudioProperties:
        class AudioState:
            class MuteState(Enum):
                UNMUTED = 0
                MUTED = 1

            class DeafenState(Enum):
                UNDEAFENED = 0
                DEAFENED = 1

            _mute_state: MuteState
            _deafen_state: DeafenState

            def __init__(self) -> None:
                self._mute_state = self.MuteState.UNMUTED
                self._deafen_state = self.DeafenState.UNDEAFENED

            @property
            def mute_state(self):
                return self._mute_state

            @property
            def deafen_state(self):
                return self._deafen_state

            def mute(self):
                self._mute_state = self.MuteState.MUTED

            def unmute(self):
                self._mute_state = self.MuteState.UNMUTED

            def deafen(self):
                self._deafen_state = self.DeafenState.DEAFENED

            def undeafen(self):
                self._deafen_state = self.DeafenState.UNDEAFENED

        _state: Optional[AudioState]
        _connection: Optional["Mumble"]

        def __init__(self, mumble_instance: "Mumble") -> None:
            self._state = self.AudioState()
            self._connection = mumble_instance

        @property
        def state(self) -> Optional[AudioState]:
            return self._state

        # region Mute
        def mute(self) -> bool:
            if self.state is None:
                return False
            if not self._check_client_mute():
                return False
            self.state.mute()
            return True

        def _check_client_mute(self) -> bool:
            if self._connection is None:
                return False
            if self._connection.users.myself is None:
                return False
            self._connection.users.myself.mute()
            return self._connection.users.myself.get_property("self_mute") is True
        # endregion

        # region Unmute
        def unmute(self) -> bool:
            if self.state is None:
                return False
            if not self._check_client_unmute():
                return False
            self.state.unmute()
            return True

        def _check_client_unmute(self) -> bool:
            if self._connection is None:
                return False
            if self._connection.users.myself is None:
                return False
            self._connection.users.myself.unmute()
            return self._connection.users.myself.get_property("self_mute") is False
        # endregion Unmute

        # region Deafen
        def deafen(self) -> bool:
            if self.state is None:
                return False
            if not self._check_client_deafen():
                return False
            self.state.deafen()
            return True

        def _check_client_deafen(self) -> bool:
            if self._connection is None:
                return False
            if self._connection.users.myself is None:
                return False
            self._connection.users.myself.deafen()
            return self._connection.users.myself.get_property("self_deaf") is True
        # endregion Deafen

        # region Undeafen
        def undeafen(self) -> bool:
            if self.state is None:
                return False
            if not self._check_client_undeafen():
                return False
            self.state.undeafen()
            return True

        def _check_client_undeafen(self) -> bool:
            if self._connection is None:
                return False
            if self._connection.users.myself is None:
                return False
            self._connection.users.myself.undeafen()
            return self._connection.users.myself.get_property("self_deaf") is False
        # endregion Undeafen

    class ServerProperties:
        class ServerState:
            _users: Dict[str, "User"]
            _channels: Dict[str, "Channel"]
            _listening_channels: Dict[str, "Channel"]

            def __init__(self) -> None:
                self._users = {}
                self._channels = {}
                self._listening_channels = {}

            # region Channel
            def add_channel(self, connection: "Mumble", channel: "Channel") -> bool:
                _myself = connection.users.myself
                if not _myself:
                    return False
                if not channel:
                    return False
                self._channels[channel["channel_id"]] = channel
                _myself.add_listening_channels([channel["channel_id"]])
                self._listening_channels[channel["channel_id"]] = channel
                return True

            def remove_channel(self, connection: "Mumble", channel: "Channel") -> bool:
                _myself = connection.users.myself
                if not _myself:
                    return False
                if not channel:
                    return False
                del self._channels[channel["channel_id"]]
                _myself.remove_listening_channels([channel["channel_id"]])
                self._listening_channels[channel["channel_id"]] = channel
                return True
            # endregion

            # region User
            def add_user(self, user: Union["User", str, int]) -> bool:
                if isinstance(user, str):
                    _user = mumble_utils.get_user_by_name(user)
                elif isinstance(user, int):
                    _user = mumble_utils.get_user_by_id(user)
                else:
                    _user = user
                if not _user:
                    return False
                self._users[_user["name"]] = _user
                return True

            def remove_user(self, user: Union["User", str, int]) -> bool:
                if isinstance(user, str):
                    marked = None
                    for _name, _user in self._users.items():
                        if _name == user:
                            marked = _name
                    if marked:
                        del self._users[marked]
                        return True
                elif isinstance(user, int):
                    marked = None
                    for _name, _user in self._users.items():
                        if _user["session"] == user:
                            marked = _name
                    if marked:
                        del self._users[marked]
                        return True
                else:
                    _user: "User" = user
                    if not _user:
                        return False
                    del self._users[_user["name"]]
                    return True
                return False
            # endregion

        _state: ServerState
        _connection: Optional["Mumble"]

        def __init__(self, mumble_instance: "Mumble") -> None:
            self._state = self.ServerState()
            self._connection = mumble_instance

        @property
        def state(self) -> ServerState:
            return self._state

        # region CLBK: MUMBLE_ON_CONNECT
        def on_server_connect(self, data) -> None:
            logger.debug(f"[{LogOutputIdentifiers.MUMBLE_ON_CONNECT}]: {data}")

        def on_server_disconnect(self) -> None:
            logger.debug(f"[{LogOutputIdentifiers.MUMBLE_ON_DISCONNECT}]: disconnected from server.")
        # endregion

        # region CLBK: MUMBLE_ON_USER_CREATED
        def on_user_created(self, data: Dict[str, Any]) -> None:
            # When a new user connected is detected, attempt to add the user to the database first
            # If the user is already in the database, just add it to the active client state.
            asyncio.run(mumble_utils.Management.User.add_user(data))

        def on_user_removed(self, data: Dict[str, Any], message: str) -> None:
            # When a user disconnection is detected, just remove it from the active client state.
            # We don't remove it from the database because that would remove user information everytime
            # the user disconnects from the server.
            if self.state.remove_user(user=data["name"]):
                logger.debug(
                    f"[{LogOutputIdentifiers.MUMBLE_ON_DISCONNECT}]: user '{data['name']}' disconnected: \
                        removed user '{data['name']}' from the server state: user removal message: '{message}'."
                )
                return
            logger.error(f"Unable to remove user '{data['name']}' from the server state: {data}.")
        # endregion

        # region CLBK: MUMBLE_ON_CHANNEL_CREATED
        def on_channel_created(self, channel: "Channel") -> None:
            # When channel creation is detected, just add it to the client state.
            # We don't add it to the database because channels contain no information
            # that should be persistently stored.
            if not self._connection:
                logger.error(f"Unable to add new channel '{channel['name']}-{channel['channel_id']}' to the server state: "
                             f"mumble instance not found.")
                return
            if self.state.add_channel(self._connection, channel=channel):
                logger.debug(f"[{LogOutputIdentifiers.MUMBLE_ON_CHANNEL_CREATED}]: channel '{channel['name']}-{channel['channel_id']}' created: "
                             f"added channel '{channel['name']}-{channel['channel_id']}' to the server state.")
                return
            logger.error(f"Unable to add new channel '{channel['name']}-{channel['channel_id']}' to the server state.")
        # endregion

        # region CLBK: MUMBLE_ON_CHANNEL_REMOVED
        def on_channel_removed(self, channel: "Channel") -> None:
            # When channel removal is detected, just remove it from the client state.
            # There is nothing to remove from the database related to channels.
            if not self._connection:
                logger.error(f"Unable to remove channel '{channel['name']}-{channel['channel_id']}' from the server state: "
                             f"mumble instance not found.")
                return
            if self.state.remove_channel(self._connection, channel=channel):
                logger.debug(f"[{LogOutputIdentifiers.MUMBLE_ON_CHANNEL_REMOVED}]: channel '{channel['name']}-{channel['channel_id']}' removed: "
                             f"removed channel '{channel['name']}-{channel['channel_id']}' from the server state.")
                return
            logger.error(f"Unable to remove channel '{channel['name']}-{channel['channel_id']}' from the server state.")
        # endregion

    _audio_properties: AudioProperties
    _server_properties: ServerProperties

    def __init__(self, mumble_instance: "Mumble") -> None:
        self._audio_properties = self.AudioProperties(mumble_instance)
        self._server_properties = self.ServerProperties(mumble_instance)

    @property
    def audio_properties(self) -> AudioProperties:
        return self._audio_properties

    @property
    def server_properties(self) -> ServerProperties:
        return self._server_properties
