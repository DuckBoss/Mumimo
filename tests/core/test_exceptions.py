import pytest

from src import exceptions


class TestExceptions:
    def test_raise_logged_error(self):
        with pytest.raises(exceptions.LoggedException, match="test"):
            raise exceptions.LoggedException("test", logger=None)

    def test_raise_validation_error(self):
        with pytest.raises(exceptions.ValidationError, match="test"):
            raise exceptions.ValidationError("test", logger=None)

    def test_raise_generic_error(self):
        with pytest.raises(exceptions.GenericError, match="test"):
            raise exceptions.GenericError("test", logger=None)

    def test_raise_connectivity_error(self):
        with pytest.raises(exceptions.ConnectivityError, match="test"):
            raise exceptions.ConnectivityError("test", logger=None)

    def test_raise_service_error(self):
        with pytest.raises(exceptions.ServiceError, match="test"):
            raise exceptions.ServiceError("test", logger=None)

    def test_raise_config_error(self):
        with pytest.raises(exceptions.ConfigError, match="test"):
            raise exceptions.ConfigError("test", logger=None)

    def test_raise_config_read_error(self):
        with pytest.raises(exceptions.ConfigReadError, match="test"):
            raise exceptions.ConfigReadError("test", logger=None)

    def test_raise_config_write_error(self):
        with pytest.raises(exceptions.ConfigWriteError, match="test"):
            raise exceptions.ConfigWriteError("test", logger=None)
