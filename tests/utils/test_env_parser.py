from typing import Dict, Any

import pytest

from src.utils import env_parser
from src.constants import ENV_ARGS


class TestEnvParserIO:
    @pytest.fixture(autouse=True)
    def env_path(self) -> str:
        return "tests/data/test.env"

    @pytest.fixture(autouse=True)
    def env_dict(self) -> Dict[str, Any]:
        return {
            ENV_ARGS.ENV_HOST: "test_host",
            ENV_ARGS.ENV_PORT: "12345",
            ENV_ARGS.ENV_USER: "test_user",
            ENV_ARGS.ENV_PASS: "test_pass",
            ENV_ARGS.ENV_CERT: "test_cert",
            ENV_ARGS.ENV_KEY: "test_key",
            ENV_ARGS.ENV_TOKENS: "test_token_1 test_token2",
            ENV_ARGS.ENV_SUPER_USER: "test_super_user",
        }

    class TestGetEnvFile:
        def test_get_env_file_invalid_empty_path(self) -> None:
            env_path = ""
            env_file = env_parser.get_env_file(env_path)
            assert env_file is None

        def test_get_env_file_invalid_path(self) -> None:
            env_path = "mytestpath"
            env_file = env_parser.get_env_file(env_path)
            assert env_file is None

        def test_get_env_file_exists(self, env_path: str) -> None:
            env_file = env_parser.get_env_file(env_path)
            assert env_file is not None

    class TestReadEnvFile:
        def test_read_env_file_contents_and_matches_test_data(self, env_path: str, env_dict: Dict[str, str]) -> None:
            env_contents = env_parser.read_env_file(env_path)
            assert env_contents is not None
            assert env_contents.items() == env_dict.items()

        def test_read_env_file_invalid_path(self) -> None:
            env_path = "mytestpath"
            with pytest.raises(Exception, match=r"^Could not find environment file at"):
                env_parser.read_env_file(env_path)

        def test_read_env_file_invalid_empty_path(self) -> None:
            env_path = ""
            with pytest.raises(Exception, match=r"^Could not find environment file at"):
                env_parser.read_env_file(env_path)
