from typing import Dict

import pytest

from src.utils import env_parser


class TestEnvParserIO:
    @pytest.fixture(autouse=True)
    def env_path(self) -> str:
        return "tests/data/test.env"

    @pytest.fixture(autouse=True)
    def env_dict(self) -> Dict[str, str]:
        return {"TEST": "test"}

    def test_get_env_file_rel(self, env_path: str) -> None:
        env_file_rel = env_parser.get_env_file(env_path)
        assert env_file_rel is not None

    def test_get_env_file_abs(self, env_path: str) -> None:
        env_file_abs = None
        env_file_rel = env_parser.get_env_file(env_path)
        if env_file_rel is not None:
            env_file_abs = env_parser.get_env_file(str(env_file_rel.resolve()))
        assert env_file_abs is not None

    def test_can_read_env_file_contents_and_matches_test_data(self, env_path: str, env_dict: Dict[str, str]) -> None:
        env_contents = env_parser.read_env_file(env_path)
        assert env_contents is not None
        assert env_contents.items() == env_dict.items()
