from unittest.mock import patch

import pytest
from pymumble_py3 import Mumble

from src.client_state import ClientState
from src.config import Config
from src.log_config import LogConfig
from src.murmur_connection import MurmurConnection


class TestClientState:
    @pytest.fixture(autouse=True)
    @patch("src.settings.MumimoSettings.Configs.get_log_config")
    @patch("src.settings.MumimoSettings.Configs.get_mumimo_config")
    @patch.object(MurmurConnection, "connection_instance")
    def get_client_state(self, mumble_instance: Mumble, mock_mumimo_cfg, mock_log_cfg) -> ClientState:
        mock_mumimo_cfg.return_value = Config("tests/data/config/test_config.toml")
        mock_log_cfg.return_value = LogConfig("tests/data/config/test_logging.toml")
        return ClientState(mumble_instance)

    @patch("src.settings.MumimoSettings.Configs.get_log_config")
    @patch("src.settings.MumimoSettings.Configs.get_mumimo_config")
    @patch.object(MurmurConnection, "connection_instance")
    def test_client_state_init(self, mumble_instance: Mumble, mock_mumimo_cfg, mock_log_cfg) -> None:
        mock_mumimo_cfg.return_value = Config("tests/data/config/test_config.toml")
        mock_log_cfg.return_value = LogConfig("tests/data/config/test_logging.toml")
        client_state = ClientState(mumble_instance)
        assert client_state is not None
        assert client_state.audio_properties is not None
        assert client_state.cmd_service is not None

    class TestAudioState:
        def test_audio_state_init(self) -> None:
            audio_state = ClientState.AudioProperties.AudioState()
            assert audio_state is not None

        def test_audio_state_mute(self) -> None:
            audio_state = ClientState.AudioProperties.AudioState()
            audio_state._mute_state = ClientState.AudioProperties.AudioState.MuteState.UNMUTED

            audio_state.mute()
            assert audio_state.mute_state == ClientState.AudioProperties.AudioState.MuteState.MUTED

        def test_audio_state_unmute(self) -> None:
            audio_state = ClientState.AudioProperties.AudioState()
            audio_state._mute_state = ClientState.AudioProperties.AudioState.MuteState.MUTED

            audio_state.unmute()
            assert audio_state.mute_state == ClientState.AudioProperties.AudioState.MuteState.UNMUTED

        def test_audio_state_deafen(self) -> None:
            audio_state = ClientState.AudioProperties.AudioState()
            audio_state._deafen_state = ClientState.AudioProperties.AudioState.DeafenState.UNDEAFENED

            audio_state.deafen()
            assert audio_state.deafen_state == ClientState.AudioProperties.AudioState.DeafenState.DEAFENED

        def test_audio_state_undeafen(self) -> None:
            audio_state = ClientState.AudioProperties.AudioState()
            audio_state._deafen_state = ClientState.AudioProperties.AudioState.DeafenState.DEAFENED

            audio_state.undeafen()
            assert audio_state.deafen_state == ClientState.AudioProperties.AudioState.DeafenState.UNDEAFENED

    class TestAudioProperties:
        def test_audio_properties_init(self, get_client_state: ClientState) -> None:
            audio_properties = get_client_state.audio_properties
            if audio_properties._state:
                assert audio_properties._state.mute_state.value == ClientState.AudioProperties.AudioState.MuteState.UNMUTED.value
                assert audio_properties._state.deafen_state.value == ClientState.AudioProperties.AudioState.DeafenState.UNDEAFENED.value
            else:
                pytest.fail("Something went wrong: the _state value is None")

        def test_audio_properties_state_exists(self, get_client_state: ClientState) -> None:
            audio_properties = get_client_state.audio_properties
            assert audio_properties.state is not None

        def test_audio_properties_state_does_not_exist(self, get_client_state: ClientState) -> None:
            audio_properties = get_client_state.audio_properties
            audio_properties._state = None
            assert audio_properties.state is None

        class TestMute:
            @patch.object(ClientState.AudioProperties, "_check_client_mute")
            def test_audio_properties_mute(self, client_mute_mock, get_client_state: ClientState) -> None:
                client_mute_mock.return_value = True

                audio_properties = get_client_state.audio_properties
                if audio_properties._state:
                    audio_properties._state._mute_state = ClientState.AudioProperties.AudioState.MuteState.UNMUTED

                    assert audio_properties.mute() is True
                    assert audio_properties._state.mute_state.value == ClientState.AudioProperties.AudioState.MuteState.MUTED.value
                else:
                    pytest.fail("Something went wrong: the _state value is None")

            @patch.object(ClientState.AudioProperties, "_check_client_mute")
            def test_audio_properties_mute_invalid_state(self, client_mute_mock, get_client_state: ClientState) -> None:
                client_mute_mock.return_value = True

                audio_properties = get_client_state.audio_properties
                audio_properties._state = None

                assert audio_properties.mute() is False

            @patch.object(ClientState.AudioProperties, "_check_client_mute")
            def test_audio_properties_mute_invalid_mute_check(self, client_mute_mock, get_client_state: ClientState) -> None:
                client_mute_mock.return_value = False

                audio_properties = get_client_state.audio_properties

                assert audio_properties.mute() is False

        class TestUnmute:
            @patch.object(ClientState.AudioProperties, "_check_client_unmute")
            def test_audio_properties_unmute(self, client_unmute_mock, get_client_state: ClientState) -> None:
                client_unmute_mock.return_value = True

                audio_properties = get_client_state.audio_properties
                if audio_properties._state:
                    audio_properties._state._mute_state = ClientState.AudioProperties.AudioState.MuteState.MUTED

                    assert audio_properties.unmute() is True
                    assert audio_properties._state.mute_state.value == ClientState.AudioProperties.AudioState.MuteState.UNMUTED.value
                else:
                    pytest.fail("Something went wrong: the _state value is None")

            @patch.object(ClientState.AudioProperties, "_check_client_unmute")
            def test_audio_properties_unmute_invalid_state(self, client_unmute_mock, get_client_state: ClientState) -> None:
                client_unmute_mock.return_value = True

                audio_properties = get_client_state.audio_properties
                audio_properties._state = None

                assert audio_properties.unmute() is False

            @patch.object(ClientState.AudioProperties, "_check_client_unmute")
            def test_audio_properties_unmute_invalid_unmute_check(self, client_unmute_mock, get_client_state: ClientState) -> None:
                client_unmute_mock.return_value = False

                audio_properties = get_client_state.audio_properties
                audio_properties._state = None

                assert audio_properties.unmute() is False

        class TestDeafen:
            @patch.object(ClientState.AudioProperties, "_check_client_deafen")
            def test_audio_properties_deafen(self, client_deafen_mock, get_client_state: ClientState) -> None:
                client_deafen_mock.return_value = True

                audio_properties = get_client_state.audio_properties
                if audio_properties._state:
                    audio_properties._state._deafen_state = ClientState.AudioProperties.AudioState.DeafenState.UNDEAFENED

                    assert audio_properties.deafen() is True
                    assert audio_properties._state.deafen_state.value == ClientState.AudioProperties.AudioState.DeafenState.DEAFENED.value
                else:
                    pytest.fail("Something went wrong: the _state value is None")

            @patch.object(ClientState.AudioProperties, "_check_client_deafen")
            def test_audio_properties_deafen_invalid_state(self, client_deafen_mock, get_client_state: ClientState) -> None:
                client_deafen_mock.return_value = True

                audio_properties = get_client_state.audio_properties
                audio_properties._state = None

                assert audio_properties.deafen() is False

            @patch.object(ClientState.AudioProperties, "_check_client_deafen")
            def test_audio_properties_deafen_invalid_deafen_check(self, client_deafen_mock, get_client_state: ClientState) -> None:
                client_deafen_mock.return_value = False

                audio_properties = get_client_state.audio_properties
                audio_properties._state = None

                assert audio_properties.deafen() is False

        class TestUndeafen:
            @patch.object(ClientState.AudioProperties, "_check_client_undeafen")
            def test_audio_properties_undeafen(self, client_undeafen_mock, get_client_state: ClientState) -> None:
                client_undeafen_mock.return_value = True

                audio_properties = get_client_state.audio_properties
                if audio_properties._state:
                    audio_properties._state._deafen_state = ClientState.AudioProperties.AudioState.DeafenState.DEAFENED

                    assert audio_properties.undeafen() is True
                    assert audio_properties._state.deafen_state.value == ClientState.AudioProperties.AudioState.DeafenState.UNDEAFENED.value
                else:
                    pytest.fail("Something went wrong: the _state value is None")

            @patch.object(ClientState.AudioProperties, "_check_client_undeafen")
            def test_audio_properties_undeafen_invalid_state(self, client_undeafen_mock, get_client_state: ClientState) -> None:
                client_undeafen_mock.return_value = True

                audio_properties = get_client_state.audio_properties
                audio_properties._state = None

                assert audio_properties.undeafen() is False

            @patch.object(ClientState.AudioProperties, "_check_client_undeafen")
            def test_audio_properties_undeafen_invalid_undeafen_check(self, client_undeafen_mock, get_client_state: ClientState) -> None:
                client_undeafen_mock.return_value = False

                audio_properties = get_client_state.audio_properties
                audio_properties._state = None

                assert audio_properties.undeafen() is False
