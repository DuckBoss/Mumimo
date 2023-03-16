import logging
import pathlib
import shutil
import sys
from unittest.mock import patch

import pytest

import src.logging as log


class TestLogging:
    @pytest.fixture(autouse=True)
    def get_logger(self):
        log._IS_INITIALIZED = False
        assert log.init_logger({"log_config_file": "tests/data/config/test_logging.toml"}) is True
        assert log._IS_INITIALIZED is True
        yield logging.getLogger(__name__)
        log._IS_INITIALIZED = False
        generated_logs_path = pathlib.Path("tests/data/generated/logs")
        if generated_logs_path.exists():
            shutil.rmtree(generated_logs_path)

    @pytest.fixture(autouse=True)
    def mock_log_config(self):
        return {
            "output": {
                "file": {
                    "enable": True,
                    "level": "DEBUG",
                    "path": "tests/data/generated/logs/",
                    "format": "(%(asctime)s)[%(name)s][%(levelname)s]::%(message)s",
                    "name": "mumimo_test_%s.log",
                    "message_privacy": True,
                    "enable_stack_trace": False,
                },
                "console": {
                    "format": "[%(levelname)s]::%(message)s",
                    "message_privacy": True,
                },
            }
        }

    def test_logger_already_initialized(self):
        log._IS_INITIALIZED = True
        assert log.init_logger() is False

    @patch("src.utils.log_utils.privacy_console_redact_all_check")
    @patch("src.utils.log_utils.privacy_file_redact_all_check")
    def test_log_privacy_fully_redacted(self, mock_file_redact, mock_console_redact, get_logger, caplog):
        mock_file_redact.return_value = True
        mock_console_redact.return_value = True
        log.log_privacy(msg="test_print_redacted", logger=get_logger, level=logging.INFO)
        assert len(caplog.records) == 0

    @patch("src.logging._log_console_handler")
    @patch("src.logging._log_file_handler")
    @patch("src.utils.log_utils.privacy_console_redact_all_check")
    @patch("src.utils.log_utils.privacy_file_redact_all_check")
    def test_log_privacy(self, mock_file_redact, mock_console_redact, mock_file_handler, mock_console_handler, get_logger, caplog):
        mock_file_redact.return_value = False
        mock_console_redact.return_value = False
        mock_file_handler.return_value = logging.FileHandler("/tmp/mumimo_temp.log")
        mock_console_handler.return_value = logging.StreamHandler(sys.stdout)

        log.log_privacy(msg="test_print_privacy", logger=get_logger, level=logging.INFO)
        assert caplog.records[0].levelno == logging.INFO
        assert "test_print_privacy" in caplog.text
