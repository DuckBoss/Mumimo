from unittest.mock import patch

from pymumble_py3 import Mumble

from src.client_state import ClientState
from src.murmur_connection import MurmurConnection


class TestClientState:
    @patch.object(MurmurConnection, "connection_instance")
    def test_client_state_init(self, mumble_instance: Mumble) -> None:
        client_state = ClientState(mumble_instance)
        assert client_state is not None

    @patch.object(MurmurConnection, "connection_instance")
    def test_audio_properties_init(self, mumble_instance: Mumble) -> None:
        client_state = ClientState(mumble_instance)
        assert client_state.audio_properties is not None


class TestAudioState:
    def test_audio_state_init(self) -> None:
        audio_state = ClientState.AudioProperties.AudioState()
        assert audio_state is not None

    def test_audio_state_mute(self) -> None:
        audio_state = ClientState.AudioProperties.AudioState()
        audio_state.mute()
        assert audio_state.mute_state == ClientState.AudioProperties.AudioState.MuteState.MUTED

    def test_audio_state_unmute(self) -> None:
        audio_state = ClientState.AudioProperties.AudioState()
        audio_state.unmute()
        assert audio_state.mute_state == ClientState.AudioProperties.AudioState.MuteState.UNMUTED

    def test_audio_state_deafen(self) -> None:
        audio_state = ClientState.AudioProperties.AudioState()
        audio_state.deafen()
        assert audio_state.deafen_state == ClientState.AudioProperties.AudioState.DeafenState.DEAFENED

    def test_audio_state_undeafen(self) -> None:
        audio_state = ClientState.AudioProperties.AudioState()
        audio_state.undeafen()
        assert audio_state.deafen_state == ClientState.AudioProperties.AudioState.DeafenState.UNDEAFENED


class TestAudioProperties:
    @patch.object(MurmurConnection, "connection_instance")
    def test_audio_properties_init(self, mumble_instance) -> None:
        client_state = ClientState(mumble_instance)
        audio_properties = client_state.audio_properties
        assert audio_properties is not None

    @patch.object(MurmurConnection, "connection_instance")
    def test_audio_properties_mute(self, mumble_instance) -> None:
        client_state = ClientState(mumble_instance)
        audio_properties = client_state.audio_properties

        with patch.object(ClientState.AudioProperties, "unmute", return_value=True, side_effect=audio_properties.state.unmute()):
            assert audio_properties.unmute() is True
            assert audio_properties._state.mute_state.value == ClientState.AudioProperties.AudioState.MuteState.UNMUTED.value
        with patch.object(ClientState.AudioProperties, "mute", return_value=True, side_effect=audio_properties.state.mute()):
            assert audio_properties.mute() is True
            assert audio_properties._state.mute_state.value == ClientState.AudioProperties.AudioState.MuteState.MUTED.value

    @patch.object(MurmurConnection, "connection_instance")
    def test_audio_properties_unmute(self, mumble_instance: Mumble) -> None:
        client_state = ClientState(mumble_instance)
        audio_properties = client_state.audio_properties

        with patch.object(ClientState.AudioProperties, "mute", return_value=True, side_effect=audio_properties.state.mute()):
            assert audio_properties.mute() is True
            assert audio_properties._state.mute_state.value == ClientState.AudioProperties.AudioState.MuteState.MUTED.value
        with patch.object(ClientState.AudioProperties, "unmute", return_value=True, side_effect=audio_properties.state.unmute()):
            assert audio_properties.unmute() is True
            assert audio_properties._state.mute_state.value == ClientState.AudioProperties.AudioState.MuteState.UNMUTED.value

    @patch.object(MurmurConnection, "connection_instance")
    def test_audio_properties_deafen(self, mumble_instance: Mumble) -> None:
        client_state = ClientState(mumble_instance)
        audio_properties = client_state.audio_properties

        with patch.object(ClientState.AudioProperties, "undeafen", return_value=True, side_effect=audio_properties.state.undeafen()):
            assert audio_properties.undeafen() is True
            assert audio_properties._state.deafen_state.value == ClientState.AudioProperties.AudioState.DeafenState.UNDEAFENED.value
        with patch.object(ClientState.AudioProperties, "deafen", return_value=True, side_effect=audio_properties.state.deafen()):
            assert audio_properties.deafen() is True
            assert audio_properties._state.deafen_state.value == ClientState.AudioProperties.AudioState.DeafenState.DEAFENED.value

    @patch.object(MurmurConnection, "connection_instance")
    def test_audio_properties_undeafen(self, mumble_instance: Mumble) -> None:
        client_state = ClientState(mumble_instance)
        audio_properties = client_state.audio_properties

        with patch.object(ClientState.AudioProperties, "deafen", return_value=True, side_effect=audio_properties.state.deafen()):
            assert audio_properties.deafen() is True
            assert audio_properties._state.deafen_state.value == ClientState.AudioProperties.AudioState.DeafenState.DEAFENED.value
        with patch.object(ClientState.AudioProperties, "undeafen", return_value=True, side_effect=audio_properties.state.undeafen()):
            assert audio_properties.undeafen() is True
            assert audio_properties._state.deafen_state.value == ClientState.AudioProperties.AudioState.DeafenState.UNDEAFENED.value
