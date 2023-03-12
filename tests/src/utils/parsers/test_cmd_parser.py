from typing import Optional
from unittest.mock import patch

import pytest

from src.corelib.command import Command
from src.utils.parsers import cmd_parser
from src.exceptions import ServiceError


class TestCmdParser:
    @pytest.fixture(autouse=True)
    @patch("src.config.Config")
    @patch("src.settings.MumimoSettings.get_mumimo_config")
    def mock_cfg_instance(self, mock_get_cfg, mock_cfg):
        mock_get_cfg.return_value = mock_cfg
        return mock_cfg

    class TestParseCommand:
        @pytest.fixture(autouse=True)
        def std_mock_text(self):
            mock_text = self.MockText()
            mock_text.actor = 0
            mock_text.channel_id = 0
            mock_text.session = None
            mock_text.message = "test_message"
            return mock_text

        class MockText:
            message: Optional[str]
            actor: Optional[int]
            channel_id: Optional[int]
            session: Optional[int]

        @patch("src.settings.MumimoSettings.get_mumimo_config")
        def test_parse_command_cfg_does_not_exist(self, mock_cfg, std_mock_text):
            mock_cfg.return_value = None
            mock_text = std_mock_text
            with pytest.raises(ServiceError, match="^Unable to process commands:"):
                _ = cmd_parser.parse_command(mock_text)

        def test_parse_command_valid_text_channel(self, mock_cfg_instance, std_mock_text) -> None:
            mock_text = std_mock_text
            cmd_result = cmd_parser.parse_command(mock_text)
            assert cmd_result is not None
            assert cmd_result.actor == 0
            assert cmd_result.channel_id == 0
            assert cmd_result.session_id == -1
            assert cmd_result.message == "test_message"

        def test_parse_command_valid_text_private(self, mock_cfg_instance, std_mock_text) -> None:
            mock_text = std_mock_text
            mock_text.channel_id = None
            mock_text.session = 0
            cmd_result = cmd_parser.parse_command(mock_text)
            assert cmd_result is not None
            assert cmd_result.actor == 0
            assert cmd_result.channel_id == -1
            assert cmd_result.session_id == 0
            assert cmd_result.message == "test_message"

        def test_parse_command_text_is_none(self, mock_cfg_instance) -> None:
            assert cmd_parser.parse_command(None) is None

        def test_parse_command_message_is_none(self, mock_cfg_instance) -> None:
            mock_text = self.MockText()
            mock_text.message = None
            cmd_result = cmd_parser.parse_command(mock_text)
            assert cmd_result is None

        def test_parse_command_message_is_not_command(self, mock_cfg_instance, std_mock_text) -> None:
            mock_text = std_mock_text
            mock_text.message = "test_message"
            mock_cfg_instance.get.return_value = "!"

            cmd_result = cmd_parser.parse_command(mock_text)
            assert cmd_result is not None
            assert cmd_result.message == mock_text.message

        def test_parse_command_message_is_empty_spaces(self, mock_cfg_instance, std_mock_text) -> None:
            mock_text = std_mock_text
            mock_text.message = "  "

            mock_cfg_instance.get.return_value = "!"

            cmd_result = cmd_parser.parse_command(mock_text)
            assert cmd_result is None

        def test_parse_command_message_command_parse_error(self, mock_cfg_instance, std_mock_text) -> None:
            mock_text = std_mock_text
            mock_text.message = "!"

            mock_cfg_instance.get.return_value = "!"

            cmd_result = cmd_parser.parse_command(mock_text)
            assert cmd_result is not None
            assert cmd_result.command is None

        def test_parse_command_message_parameters_parse_error(self, mock_cfg_instance, std_mock_text) -> None:
            mock_text = std_mock_text
            mock_text.message = "!test.param"

            mock_cfg_instance.get.return_value = "!"

            cmd_result = cmd_parser.parse_command(mock_text)
            assert cmd_result is not None
            assert cmd_result.parameters == ["param"]

        def test_parse_command_message_body_parse_error(self, mock_cfg_instance, std_mock_text) -> None:
            mock_text = std_mock_text
            mock_text.message = "!test"

            mock_cfg_instance.get.return_value = "!"

            cmd_result = cmd_parser.parse_command(mock_text)
            assert cmd_result is not None
            assert cmd_result.message == ""

    class TestParseActorName:
        class MockConnectionInstance:
            users = {0: {"name": "test_user"}}

        @patch("pymumble_py3.mumble.Mumble", new_callable=MockConnectionInstance)
        def test_parse_actor_name_valid(self, mock_mumble) -> None:
            mock_command: Command = Command()
            mock_command.actor = 0
            mock_mumble.users[0]["name"] = "test_user"

            cmd_result: str = cmd_parser.parse_actor_name(mock_command, mock_mumble)
            assert cmd_result == self.MockConnectionInstance().users[0]["name"]

        @patch("pymumble_py3.mumble.Mumble", new_callable=MockConnectionInstance)
        def test_parse_actor_name_invalid_actor_id(self, mock_mumble) -> None:
            mock_command: Command = Command()
            mock_command.actor = 1

            cmd_result: str = cmd_parser.parse_actor_name(mock_command, mock_mumble)
            assert cmd_result == "Server"

        @patch("pymumble_py3.mumble.Mumble", new_callable=MockConnectionInstance)
        def test_parse_actor_name_actor_is_none(self, mock_mumble) -> None:
            mock_command: Command = Command()
            mock_command.actor = 0
            mock_mumble.users[0]["name"] = None

            cmd_result: str = cmd_parser.parse_actor_name(mock_command, mock_mumble)
            assert cmd_result == "Unavailable"

    class TestParseChannelName:
        class MockConnectionInstance:
            channels = {0: {"name": "test_channel"}}

        @patch("pymumble_py3.mumble.Mumble", new_callable=MockConnectionInstance)
        def test_parse_channel_name_valid(self, mock_mumble) -> None:
            mock_command: Command = Command()
            mock_command.channel_id = 0
            mock_mumble.channels[0]["name"] = "test_channel"

            cmd_result: str = cmd_parser.parse_channel_name(mock_command, mock_mumble)
            assert cmd_result == self.MockConnectionInstance().channels[0]["name"]

        @patch("pymumble_py3.mumble.Mumble", new_callable=MockConnectionInstance)
        def test_parse_channel_name_invalid_channel_id(self, mock_mumble) -> None:
            mock_command: Command = Command()
            mock_command.channel_id = 1

            cmd_result: str = cmd_parser.parse_channel_name(mock_command, mock_mumble)
            assert cmd_result == "Server"

        @patch("pymumble_py3.mumble.Mumble", new_callable=MockConnectionInstance)
        def test_parse_channel_name_invalid_private_message(self, mock_mumble) -> None:
            mock_command: Command = Command()
            mock_command.channel_id = -1
            mock_command.session_id = 0

            cmd_result: str = cmd_parser.parse_channel_name(mock_command, mock_mumble)
            assert cmd_result == "Private"

        @patch("pymumble_py3.mumble.Mumble", new_callable=MockConnectionInstance)
        def test_parse_channel_name_channel_is_none(self, mock_mumble) -> None:
            mock_command: Command = Command()
            mock_command.channel_id = 0
            mock_mumble.channels[0]["name"] = None

            cmd_result: str = cmd_parser.parse_channel_name(mock_command, mock_mumble)
            assert cmd_result == "Unavailable"

    class TestParseMessageImageData:
        def test_parse_message_image_data_message_has_image_data(self) -> None:
            mock_command: Command = Command()
            mock_command.message = '<img src="...">image</img>'

            cmd_result: str = cmd_parser.parse_message_image_data(mock_command)
            assert cmd_result == "Image Data"

        def test_parse_message_image_data_message_has_no_image_data(self) -> None:
            mock_command: Command = Command()
            mock_command.message = "regular_message"

            cmd_result: str = cmd_parser.parse_message_image_data(mock_command)
            assert cmd_result == "regular_message"

        def test_parse_message_image_data_message_is_empty(self) -> None:
            mock_command: Command = Command()
            mock_command.message = ""

            cmd_result: str = cmd_parser.parse_message_image_data(mock_command)
            assert cmd_result == ""

    class TestParseMessageHyperlinkData:
        def test_parse_message_hyperlink_data_message_has_hyperlink_data(self) -> None:
            mock_command: Command = Command()
            mock_command.message = '<a href="...">hyperlink</a>'

            cmd_result: str = cmd_parser.parse_message_hyperlink_data(mock_command)
            assert cmd_result == "Hyperlink Data"

        def test_parse_message_hyperlink_data_message_has_no_hyperlink_data(self) -> None:
            mock_command: Command = Command()
            mock_command.message = "regular_message"

            cmd_result: str = cmd_parser.parse_message_hyperlink_data(mock_command)
            assert cmd_result == "regular_message"

        def test_parse_message_hyperlink_data_message_is_empty(self) -> None:
            mock_command: Command = Command()
            mock_command.message = ""

            cmd_result: str = cmd_parser.parse_message_hyperlink_data(mock_command)
            assert cmd_result == ""
