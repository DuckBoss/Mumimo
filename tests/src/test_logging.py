import logging
import pathlib
import shutil
import sys
from unittest.mock import patch

import pytest

import src.logging as log
from src.log_config import LogConfig


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
        _cfg = {
            "output": {
                "file": {
                    "enable": False,
                    "level": "DEBUG",
                    "path": "tests/data/generated/logs/",
                    "format": "(%(asctime)s)[%(name)s][%(levelname)s]::%(message)s",
                    "name": "mumimo_test_%s.log",
                    "message_privacy": True,
                },
                "console": {
                    "format": "[%(levelname)s]::%(message)s",
                    "message_privacy": True,
                },
            }
        }
        cfg = LogConfig("/tmp/mumimo_test.toml")
        cfg.update(_cfg)
        return cfg

    def test_logger_already_initialized(self):
        log._IS_INITIALIZED = True
        assert log.init_logger() is False

    @patch("src.logging.logger.root.addHandler")
    @patch("src.logging.logger.root.hasHandlers")
    def test_init_logger(self, mock_logger_handlers, mock_add_handler):
        log._IS_INITIALIZED = False
        mock_logger_handlers.return_value = False
        assert log.init_logger({"log_config_file": "tests/data/config/test_logging.toml"}) is True
        assert mock_add_handler.called is True

    def test_init_logger_no_sys_args(self):
        log._IS_INITIALIZED = False
        assert log.init_logger() is False

    @patch("src.logging.logger.root.addHandler")
    @patch("src.logging.logger.root.hasHandlers")
    def test_init_logger_no_handlers(self, mock_logger_handlers, mock_add_handler):
        log._IS_INITIALIZED = False
        mock_logger_handlers.return_value = True
        log.init_logger({"log_config_file": "tests/data/config/test_logging.toml"})
        assert not mock_add_handler.called

    @patch("src.utils.log_utils.initialize_log_config")
    @patch("src.logging.get_file_handler")
    def test_init_logger_file_log_disabled(self, mock_get_file_handler, mock_init_config, mock_log_config):
        log._IS_INITIALIZED = False
        mock_init_config.return_value = mock_log_config
        mock_init_config.set.return_value = None
        assert log.init_logger({"log_config_file": "tests/data/config/test_logging.toml"}) is True
        assert not mock_get_file_handler.called

    @patch("src.utils.log_utils.privacy_console_redact_all_check")
    @patch("src.utils.log_utils.privacy_file_redact_all_check")
    def test_log_privacy_fully_redacted(self, mock_file_redact, mock_console_redact, get_logger, caplog):
        mock_file_redact.return_value = True
        mock_console_redact.return_value = True
        log.log_privacy(msg="this should not show up", logger=get_logger, level=logging.INFO)
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
