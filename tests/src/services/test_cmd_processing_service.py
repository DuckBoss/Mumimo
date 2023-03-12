from unittest.mock import PropertyMock, patch

import pytest

from src.corelib.command import Command
from src.exceptions import ServiceError
from src.services.cmd_processing_service import CommandProcessingService


class TestCommandProcessingService:
    @pytest.fixture(autouse=True)
    @patch("pymumble_py3.mumble.Mumble")
    def get_cmd_processing_service(self, mock_mumble) -> CommandProcessingService:
        return CommandProcessingService(mock_mumble)

    class TestServiceInit:
        @patch("src.config.Config")
        @patch("pymumble_py3.mumble.Mumble")
        def test_init_command_processing_service(self, mock_mumble, mock_config) -> None:
            mock_config.get.return_value = 10
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

        @patch("src.services.cmd_processing_service.CommandProcessingService.connection_instance", new_callable=PropertyMock)
        @patch("src.services.cmd_processing_service.debug")
        @patch("src.utils.parsers.cmd_parser.parse_command")
        @patch("src.settings.MumimoSettings.get_mumimo_config")
        def test_process_cmd_valid_text(self, mock_cfg, mock_parse_command, mock_debug, mock_connection_instance, get_cmd_processing_service) -> None:
            mock_debug.return_value = None
            mock_connection_instance.return_value = self.MockMumble()
            mock_parse_command.return_value = Command("test_cmd", ["param_1", "param_2"], "test_msg", 0, 0, -1)
            service: CommandProcessingService = get_cmd_processing_service
            assert service.process_cmd("") is None

        @patch("src.services.cmd_processing_service.CommandProcessingService.connection_instance", new_callable=PropertyMock)
        @patch("src.services.cmd_processing_service.debug")
        @patch("src.utils.parsers.cmd_parser.parse_command")
        @patch("src.settings.MumimoSettings.get_mumimo_config")
        def test_process_cmd_valid_text_cmd_history_is_none(
            self, mock_cfg, mock_parse_command, mock_debug, mock_connection_instance, get_cmd_processing_service
        ) -> None:
            mock_debug.return_value = None
            mock_connection_instance.return_value = self.MockMumble()
            mock_parse_command.return_value = Command("test_cmd", ["param_1", "param_2"], "test_msg", 0, 0, -1)
            service: CommandProcessingService = get_cmd_processing_service
            assert service.process_cmd("") is None

        def test_process_cmd_text_is_none(self, get_cmd_processing_service) -> None:
            with pytest.raises(ServiceError, match="^Received text message"):
                service: CommandProcessingService = get_cmd_processing_service
                service.process_cmd(None)