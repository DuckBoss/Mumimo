from typing import Any, Dict

import pytest

from src.constants import EnvArgs
from src.utils.parsers import env_parser


class TestEnvParserIO:
    @pytest.fixture(autouse=True)
    def env_path(self) -> str:
        return "tests/data/test.env"

    @pytest.fixture(autouse=True)
    def env_dict(self) -> Dict[str, Any]:
        return {
            EnvArgs.ENV_HOST: "test_host",
            EnvArgs.ENV_PORT: "12345",
            EnvArgs.ENV_USER: "test_user",
            EnvArgs.ENV_PASS: "test_pass",
            EnvArgs.ENV_CERT: "test_cert",
            EnvArgs.ENV_KEY: "test_key",
            EnvArgs.ENV_TOKENS: "test_token_1 test_token2",
            EnvArgs.ENV_SUPER_USER: "test_super_user",
            EnvArgs.ENV_DB_DIALECT: "sqlite",
            EnvArgs.ENV_DB_DRIVER: "aiosqlite",
            EnvArgs.ENV_DB_USER: "test_mumimo",
            EnvArgs.ENV_DB_PASS: "test_mumimo",
            EnvArgs.ENV_DB_HOST: "test_mumimo_db",
            EnvArgs.ENV_DB_NAME: "test_mumimo",
            EnvArgs.ENV_DB_QUERY: "test_mumimo_query",
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
