from unittest.mock import patch

from src.version import validate_version, version


class TestVersion:
    def test_version_exists(self):
        assert isinstance(version(), str)

    def test_version_is_valid(self):
        with patch("src.version.version", return_value="0.0.1"):
            assert validate_version() is True

    def test_version_is_invalid_number_of_digits(self):
        with patch("src.version.version", return_value="0.0.0.1"):
            assert validate_version() is False

    def test_version_is_invalid_characters(self):
        with patch("src.version.version", return_value="y.e.s"):
            assert validate_version() is False

    def test_version_is_invalid_too_many_digits(self):
        with patch("src.version.version", return_value="0000.1.1"):
            assert validate_version() is False

    def test_version_is_invalid_negative_digits(self):
        with patch("src.version.version", return_value="0.-1.1"):
            assert validate_version() is False

    def test_version_is_invalid_not_enough_digits(self):
        with patch("src.version.version", return_value="0.1"):
            assert validate_version() is False

    def test_version_is_invalid_wrong_dot_placement(self):
        with patch("src.version.version", return_value=".0.0.1"):
            assert validate_version() is False
