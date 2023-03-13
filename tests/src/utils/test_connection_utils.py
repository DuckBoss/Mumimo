from unittest.mock import patch

from src.utils import connection_utils


class TestSupportedPlatforms:
    @patch("platform.system")
    def test_is_supported_platform_linux(self, mock_platform):
        mock_platform.return_value = "Linux"
        is_supported = connection_utils.is_supported_platform()
        assert is_supported is True

    @patch("platform.system")
    def test_is_supported_platform_macos(self, mock_platform):
        mock_platform.return_value = "Darwin"
        is_supported = connection_utils.is_supported_platform()
        assert is_supported is True

    @patch("platform.system")
    def test_is_not_supported_platform_windows(self, mock_platform):
        mock_platform.return_value = "Windows"
        is_supported = connection_utils.is_supported_platform()
        assert is_supported is False

    @patch("platform.system")
    def test_is_not_supported_platform_java(self, mock_platform):
        mock_platform.return_value = "Java"
        is_supported = connection_utils.is_supported_platform()
        assert is_supported is False


class TestParseChannelTokens:
    def test_parse_channel_tokens_is_valid(self) -> None:
        assert connection_utils.parse_channel_tokens("token1 token2") == ["token1", "token2"]

    def test_parse_channel_tokens_is_none(self) -> None:
        assert connection_utils.parse_channel_tokens(None) is None  # type: ignore

    def test_parse_channel_tokens_invalid_values(self) -> None:
        assert connection_utils.parse_channel_tokens(5) is None  # type: ignore

    def test_parse_channel_tokens_extra_spaces(self) -> None:
        assert connection_utils.parse_channel_tokens(" token1   token2  ") == ["token1", "token2"]

    def test_parse_channel_tokens_empty(self) -> None:
        assert connection_utils.parse_channel_tokens("") is None

    def test_parse_channel_tokens_spaces(self) -> None:
        assert connection_utils.parse_channel_tokens("  ") is None
