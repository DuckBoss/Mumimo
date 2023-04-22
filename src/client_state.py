from enum import Enum
from typing import TYPE_CHECKING, Optional, Dict, Union

from .utils import mumble_utils


if TYPE_CHECKING:
    from pymumble_py3.mumble import Mumble
    from pymumble_py3.users import User


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

        def mute(self) -> bool:
            if self._state is None:
                return False
            if self._check_client_mute():
                self._state.mute()
                return True
            return False

        def _check_client_mute(self) -> bool:
            if self._connection is not None:
                if self._connection.users.myself:
                    self._connection.users.myself.mute()
                    if self._connection.users.myself.get_property("self_mute") is True:
                        return True
            return False

        def unmute(self) -> bool:
            if self._state is None:
                return False
            if self._check_client_unmute():
                self._state.unmute()
                return True
            return False

        def _check_client_unmute(self) -> bool:
            if self._connection is not None:
                if self._connection.users.myself:
                    self._connection.users.myself.unmute()
                    if self._connection.users.myself.get_property("self_mute") is False:
                        return True
            return False

        def deafen(self) -> bool:
            if self._state is None:
                return False
            if self._check_client_deafen():
                self._state.deafen()
                return True
            return False

        def _check_client_deafen(self) -> bool:
            if self._connection is not None:
                if self._connection.users.myself:
                    self._connection.users.myself.deafen()
                    if self._connection.users.myself.get_property("self_deaf") is True:
                        return True
            return False

        def undeafen(self) -> bool:
            if self._state is None:
                return False
            if self._check_client_undeafen():
                self._state.undeafen()
                return True
            return False

        def _check_client_undeafen(self) -> bool:
            if self._connection is not None:
                if self._connection.users.myself:
                    self._connection.users.myself.undeafen()
                    if self._connection.users.myself.get_property("self_deaf") is False:
                        return True
            return False

    class ServerProperties:
        class ServerState:
            _users: Dict[str, "User"]

            def __init__(self) -> None:
                self._users = {}

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
                    _user = mumble_utils.get_user_by_name(user)
                elif isinstance(user, int):
                    _user = mumble_utils.get_user_by_id(user)
                else:
                    _user = user
                if not _user:
                    return False
                del self._users[_user["name"]]
                return True

        _state: Optional[ServerState]
        _connection: Optional["Mumble"]

        def __init__(self, mumble_instance: "Mumble") -> None:
            self._state = self.ServerState()
            self._connection = mumble_instance

        @property
        def state(self) -> Optional[ServerState]:
            return self._state

        def on_server_connect(self, data) -> None:
            print(data)

        def on_user_created(self, data) -> None:
            print(data)

        def on_user_removed(self, data) -> None:
            print(data)

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
