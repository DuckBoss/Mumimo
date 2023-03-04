import logging
import pytest
import src.logging as log
import pathlib
import shutil


class TestLogging:
    @pytest.fixture(autouse=True)
    def get_logger(self):
        log._is_initialized = False
        assert log.init_logger({"log_config_file": "tests/data/config/test_logging.toml"}) is True
        assert log._is_initialized is True
        yield log.get_logger(__name__)
        log._is_initialized = False
        generated_logs_path = pathlib.Path("tests/data/logs")
        shutil.rmtree(generated_logs_path)

    @pytest.fixture(autouse=True)
    def print_fixture(self, get_logger):
        assert get_logger.hasHandlers() is True
        print = log.print(logger=get_logger)
        return print

    @pytest.fixture(autouse=True)
    def debug_fixture(self, get_logger):
        assert get_logger.hasHandlers() is True
        print = log.debug(logger=get_logger)
        return print

    @pytest.fixture(autouse=True)
    def warning_fixture(self, get_logger):
        assert get_logger.hasHandlers() is True
        warn = log.print_warning(logger=get_logger)
        return warn

    @pytest.fixture(autouse=True)
    def error_fixture(self, get_logger):
        assert get_logger.hasHandlers() is True
        err = log.print_error(logger=get_logger)
        return err

    def test_log_print_default(self, print_fixture, caplog):
        print_fixture("test_print_default")
        assert caplog.records[0].levelno == logging.INFO
        assert "test_print_default" in caplog.text

    def test_log_print_debug(self, print_fixture, caplog):
        print_fixture("test_print_debug", level=logging.DEBUG)
        assert caplog.records[0].levelno == logging.DEBUG
        assert "test_print_debug" in caplog.text

    def test_log_print_info(self, print_fixture, caplog):
        print_fixture("test_print_info", level=logging.INFO)
        assert caplog.records[0].levelno == logging.INFO
        assert "test_print_info" in caplog.text

    def test_log_print_warning(self, print_fixture, caplog):
        print_fixture("test_print_warning", level=logging.WARNING)
        assert caplog.records[0].levelno == logging.WARNING
        assert "test_print_warning" in caplog.text

    def test_log_print_error(self, print_fixture, caplog):
        print_fixture("test_print_error", level=logging.ERROR)
        assert caplog.records[0].levelno == logging.ERROR
        assert "test_print_error" in caplog.text

    def test_log_debug(self, debug_fixture, caplog):
        debug_fixture("test_debug")
        assert caplog.records[0].levelno == logging.DEBUG
        assert "test_debug" in caplog.text

    def test_log_error(self, error_fixture, caplog):
        error_fixture("test_error")
        assert caplog.records[0].levelno == logging.ERROR
        assert "test_error" in caplog.text

    def test_log_warning(self, warning_fixture, caplog):
        warning_fixture("test_warning")
        assert caplog.records[0].levelno == logging.WARNING
        assert "test_warning" in caplog.text
