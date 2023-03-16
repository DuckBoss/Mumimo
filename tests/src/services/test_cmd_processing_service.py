from typing import Any, Dict
from unittest.mock import Mock, PropertyMock, patch

import pytest

from src.config import Config
from src.constants import LogCfgFields
from src.corelib.command import Command
from src.exceptions import ServiceError
from src.log_config import LogConfig
from src.services.cmd_processing_service import CommandProcessingService


class TestCommandProcessingService:
    @pytest.fixture(autouse=True)
    @patch("src.settings.MumimoSettings.get_log_config")
    @patch("src.settings.MumimoSettings.get_mumimo_config")
    @patch("pymumble_py3.mumble.Mumble")
    def get_cmd_processing_service(self, mock_mumble, mock_cfg, mock_log_cfg) -> CommandProcessingService:
        mock_cfg.return_value = Config("tests/data/config/test_config.toml")
        mock_log_cfg.return_value = LogConfig("tests/data/config/test_logging.toml")
        return CommandProcessingService(mock_mumble)

    class TestOutputPrivacyFilter:
        @pytest.fixture(autouse=True)
        def get_privacy_filter(self) -> "CommandProcessingService.OutputPrivacyFilter":
            return CommandProcessingService.OutputPrivacyFilter()

        @pytest.fixture(autouse=True)
        def filled_privacy_dict(self, get_privacy_filter) -> Dict[str, Any]:
            filter = get_privacy_filter.get_privacy_template()
            filter.update(
                {
                    "file": {
                        "message": "test_file_message",
                        "command": "test_file_command",
                        "actor": "test_file_actor",
                        "channel": "test_file_channel",
                        "parameters": ["test_file_param"],
                    },
                    "console": {
                        "message": "test_console_message",
                        "command": "test_console_command",
                        "actor": "test_console_actor",
                        "channel": "test_console_channel",
                        "parameters": ["test_console_param"],
                    },
                }
            )
            return filter

        @pytest.fixture(autouse=True)
        def filled_redacted_privacy_dict(self, get_privacy_filter) -> Dict[str, Any]:
            filter = get_privacy_filter.get_privacy_template()
            filter.update(
                {
                    "file": {
                        "message": "Redacted",
                        "command": "Redacted",
                        "actor": "Redacted",
                        "channel": "Redacted",
                        "parameters": "[Redacted]",
                    },
                    "console": {
                        "message": "Redacted",
                        "command": "Redacted",
                        "actor": "Redacted",
                        "channel": "Redacted",
                        "parameters": "[Redacted]",
                    },
                }
            )
            return filter

        def test_get_privacy_template(self, get_privacy_filter) -> None:
            assert isinstance(get_privacy_filter.get_privacy_template(), dict) is True

        def test_compile_file_privacy_checked_message(self, get_privacy_filter, filled_redacted_privacy_dict) -> None:
            assert (
                get_privacy_filter.compile_file_privacy_checked_message(filled_redacted_privacy_dict)
                == f"{filled_redacted_privacy_dict['file']['channel']}::{filled_redacted_privacy_dict['file']['actor']}::"
                f"[Cmd:{filled_redacted_privacy_dict['file']['command']} | Params:{filled_redacted_privacy_dict['file']['parameters']}]::"
                f"{filled_redacted_privacy_dict['file']['message']}"
            )

        def test_compile_console_privacy_checked_message(self, get_privacy_filter, filled_redacted_privacy_dict) -> None:
            assert (
                get_privacy_filter.compile_file_privacy_checked_message(filled_redacted_privacy_dict)
                == f"{filled_redacted_privacy_dict['console']['channel']}::{filled_redacted_privacy_dict['console']['actor']}::"
                f"[Cmd:{filled_redacted_privacy_dict['console']['command']} | Params:{filled_redacted_privacy_dict['console']['parameters']}]::"
                f"{filled_redacted_privacy_dict['console']['message']}"
            )

        @patch("src.services.cmd_processing_service.CommandProcessingService.OutputPrivacyFilter._redact_message")
        @patch("src.services.cmd_processing_service.CommandProcessingService.OutputPrivacyFilter._redact_channel")
        @patch("src.services.cmd_processing_service.CommandProcessingService.OutputPrivacyFilter._redact_actor")
        @patch("src.services.cmd_processing_service.CommandProcessingService.OutputPrivacyFilter._redact_commands")
        @patch("src.corelib.command.Command")
        @patch("src.log_config.LogConfig")
        @patch("pymumble_py3.mumble.Mumble")
        def test_get_privacy_checked_output(
            self,
            mock_connection_instance,
            mock_log_cfg,
            mock_cmd,
            mock_redact_cmd,
            mock_redact_actor,
            mock_redact_channel,
            mock_redact_msg,
            get_privacy_filter,
        ) -> None:
            mock_redact_cmd.return_value = {
                "file": {"command": "Redacted", "parameters": "Redacted"},
                "console": {"command": "Redacted", "parameters": "Redacted"},
            }
            mock_redact_actor.return_value = {
                "file": {"actor": "Redacted"},
                "console": {"actor": "Redacted"},
            }
            mock_redact_channel.return_value = {
                "file": {"channel": "Redacted"},
                "console": {"channel": "Redacted"},
            }
            mock_redact_msg.return_value = {
                "file": {"message": "[Redacted Message]"},
                "console": {"message": "[Redacted Message]"},
            }
            result: Dict[str, Any] = get_privacy_filter.get_privacy_checked_output(mock_cmd, mock_log_cfg, mock_connection_instance)
            assert all("Redacted" in val for val in result["file"].values()) is True
            assert all("Redacted" in val for val in result["console"].values()) is True

        @patch("src.corelib.command.Command")
        @patch("src.log_config.LogConfig")
        def test__redact_commands(self, mock_log_cfg, mock_cmd, get_privacy_filter) -> None:
            mock_log_cfg.set(LogCfgFields.OUTPUT.FILE.PRIVACY.REDACT_COMMANDS, True)
            mock_log_cfg.set(LogCfgFields.OUTPUT.CONSOLE.PRIVACY.REDACT_COMMANDS, True)
            mock_cmd.return_value = Command("test_redacted_command", ["redact_1", "redact_2"])
            result: Dict[str, Any] = get_privacy_filter._redact_commands(mock_cmd, mock_log_cfg)
            assert result["console"]["command"] == "Redacted"
            assert result["console"]["parameters"] == "Redacted"
            assert result["file"]["command"] == "Redacted"
            assert result["file"]["parameters"] == "Redacted"

        @patch("src.utils.parsers.cmd_parser.parse_actor_name")
        @patch("src.corelib.command.Command")
        @patch("src.log_config.LogConfig")
        @patch("pymumble_py3.mumble.Mumble")
        def test__redact_actor(self, mock_connection_instance, mock_log_cfg, mock_cmd, mock_parser, get_privacy_filter) -> None:
            mock_log_cfg.set(LogCfgFields.OUTPUT.FILE.PRIVACY.REDACT_USER, True)
            mock_log_cfg.set(LogCfgFields.OUTPUT.CONSOLE.PRIVACY.REDACT_USER, True)
            mock_cmd.return_value = Command(actor=0)
            mock_parser.return_value = "test_redacted_actor"
            result: Dict[str, Any] = get_privacy_filter._redact_actor(mock_cmd, mock_log_cfg, mock_connection_instance)
            assert result["console"]["actor"] == "Redacted"
            assert result["file"]["actor"] == "Redacted"

        @patch("src.utils.parsers.cmd_parser.parse_channel_name")
        @patch("src.corelib.command.Command")
        @patch("src.log_config.LogConfig")
        @patch("pymumble_py3.mumble.Mumble")
        def test__redact_channel(self, mock_connection_instance, mock_log_cfg, mock_cmd, mock_parser, get_privacy_filter) -> None:
            mock_log_cfg.set(LogCfgFields.OUTPUT.FILE.PRIVACY.REDACT_CHANNEL, True)
            mock_log_cfg.set(LogCfgFields.OUTPUT.CONSOLE.PRIVACY.REDACT_CHANNEL, True)
            mock_cmd.return_value = Command(channel_id=0)
            mock_parser.return_value = "test_redacted_channel"
            result: Dict[str, Any] = get_privacy_filter._redact_channel(mock_cmd, mock_log_cfg, mock_connection_instance)
            assert result["console"]["channel"] == "Redacted"
            assert result["file"]["channel"] == "Redacted"

        @patch("src.utils.parsers.cmd_parser.parse_message_hyperlink_data")
        @patch("src.utils.parsers.cmd_parser.parse_message_image_data")
        @patch("src.corelib.command.Command")
        @patch("src.log_config.LogConfig")
        def test__redact_message(self, mock_log_cfg, mock_cmd, mock_image_parser, mock_link_parser, get_privacy_filter) -> None:
            msg = "test_redacted_message"
            mock_log_cfg.set(LogCfgFields.OUTPUT.FILE.PRIVACY.REDACT_MESSAGE, True)
            mock_log_cfg.set(LogCfgFields.OUTPUT.CONSOLE.PRIVACY.REDACT_MESSAGE, True)
            mock_cmd.return_value = Command(message=msg)
            mock_image_parser.return_value = msg
            mock_link_parser.return_value = msg
            result: Dict[str, Any] = get_privacy_filter._redact_message(mock_cmd, mock_log_cfg)
            assert result["console"]["message"] == "[Redacted Message]"
            assert result["file"]["message"] == "[Redacted Message]"

    class TestServiceInit:
        @patch("src.settings.MumimoSettings.get_log_config")
        @patch("src.config.Config")
        @patch("pymumble_py3.mumble.Mumble")
        def test_init_command_processing_service(self, mock_mumble, mock_mumimo_config, mock_log_cfg) -> None:
            mock_mumimo_config.get.return_value = 10
            mock_log_cfg.return_value = LogConfig("tests/data/config/test_logging.toml")
            service: CommandProcessingService = CommandProcessingService(mock_mumble)
            assert service is not None

        @patch("src.services.cmd_processing_service.CommandProcessingService.connection_instance", new_callable=PropertyMock)
        @patch("pymumble_py3.mumble.Mumble")
        def test_init_command_processing_service_no_murmur_connection(self, mock_mumble, mock_connection_instance) -> None:
            mock_connection_instance.return_value = None
            with pytest.raises(ServiceError, match="^Unable to retrieve murmur connection:"):
                _ = CommandProcessingService(mock_mumble)

        @patch("src.settings.MumimoSettings.get_mumimo_config")
        @patch("pymumble_py3.mumble.Mumble")
        def test_init_command_processing_service_no_cfg_instance(self, mock_mumble, mock_cfg_instance) -> None:
            mock_cfg_instance.return_value = None
            with pytest.raises(ServiceError, match="^Unable to create command processing service:"):
                _ = CommandProcessingService(mock_mumble)

    class TestProcessCmd:
        class MockMumble:
            users = {0: {"name": "test_user"}}
            channels = {0: {"name": "test_channel"}}

        @patch("src.logging.log_privacy", Mock())
        @patch("src.services.cmd_processing_service.CommandProcessingService.connection_instance", new_callable=PropertyMock)
        @patch("src.settings.MumimoSettings.get_log_config")
        @patch("src.utils.parsers.cmd_parser.parse_command")
        def test_process_cmd_valid_text(self, mock_parse_command, mock_log_cfg, mock_connection_instance, get_cmd_processing_service) -> None:
            mock_connection_instance.return_value = self.MockMumble()
            mock_log_cfg.return_value = LogConfig("tests/data/config/test_logging.toml")
            mock_parse_command.return_value = Command("test_cmd", ["param_1", "param_2"], "test_msg", 0, 0, -1)
            service: CommandProcessingService = get_cmd_processing_service
            assert service.process_cmd("") is None

        @patch("src.services.cmd_processing_service.CommandProcessingService.connection_instance", new_callable=PropertyMock)
        @patch("src.settings.MumimoSettings.get_log_config")
        @patch("src.utils.parsers.cmd_parser.parse_command")
        def test_process_cmd_valid_text_log_cfg_is_none(
            self, mock_parse_command, mock_log_cfg, mock_connection_instance, get_cmd_processing_service
        ) -> None:
            mock_connection_instance.return_value = self.MockMumble()
            mock_log_cfg.return_value = None
            mock_parse_command.return_value = Command("test_cmd", ["param_1", "param_2"], "test_msg", 0, 0, -1)
            with pytest.raises(ServiceError, match="^Unable to process command privacy checks"):
                service: CommandProcessingService = get_cmd_processing_service
                service.process_cmd("")

        @patch("src.services.cmd_processing_service.CommandProcessingService.cmd_history", new_callable=PropertyMock)
        @patch("src.services.cmd_processing_service.CommandProcessingService.connection_instance", new_callable=PropertyMock)
        @patch("src.settings.MumimoSettings.get_log_config")
        @patch("src.utils.parsers.cmd_parser.parse_command")
        def test_process_cmd_valid_text_cmd_history_is_none(
            self, mock_parse_command, mock_log_cfg, mock_connection_instance, mock_cmd_history, get_cmd_processing_service
        ) -> None:
            mock_cmd_history.return_value = None
            mock_connection_instance.return_value = self.MockMumble()
            mock_log_cfg.return_value = LogConfig("tests/data/config/test_logging.toml")
            mock_parse_command.return_value = Command("test_cmd", ["param_1", "param_2"], "test_msg", 0, 0, -1)
            with pytest.raises(ServiceError, match="^Unable to add command"):
                service: CommandProcessingService = get_cmd_processing_service
                service.process_cmd("")

        def test_process_cmd_text_is_none(self, get_cmd_processing_service) -> None:
            with pytest.raises(ServiceError, match="^Received text message"):
                service: CommandProcessingService = get_cmd_processing_service
                service.process_cmd(None)
