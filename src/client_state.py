from enum import Enum
from typing import TYPE_CHECKING, Optional

from .services.cmd_processing_service import CommandProcessingService

if TYPE_CHECKING:
    from pymumble_py3.mumble import Mumble


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

    _audio_properties: AudioProperties
    _cmd_service: CommandProcessingService

    def __init__(self, mumble_instance: "Mumble") -> None:
        self._audio_properties = self.AudioProperties(mumble_instance)
        self._cmd_service = CommandProcessingService(mumble_instance)

    @property
    def audio_properties(self) -> AudioProperties:
        return self._audio_properties

    @property
    def cmd_service(self) -> CommandProcessingService:
        return self._cmd_service
