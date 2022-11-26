from unittest.mock import patch

from src.utils import mumimo_utils


class TestSupportedPlatforms:
    @patch("platform.system")
    def test_is_supported_platform_linux(self, mock_platform):
        mock_platform.return_value = "Linux"
        is_supported = mumimo_utils.is_supported_platform()
        assert is_supported is True

    @patch("platform.system")
    def test_is_supported_platform_macos(self, mock_platform):
        mock_platform.return_value = "Darwin"
        is_supported = mumimo_utils.is_supported_platform()
        assert is_supported is True

    @patch("platform.system")
    def test_is_not_supported_platform_windows(self, mock_platform):
        mock_platform.return_value = "Windows"
        is_supported = mumimo_utils.is_supported_platform()
        assert is_supported is False

    @patch("platform.system")
    def test_is_not_supported_platform_java(self, mock_platform):
        mock_platform.return_value = "Java"
        is_supported = mumimo_utils.is_supported_platform()
        assert is_supported is False
