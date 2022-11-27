import pathlib
import re
from typing import Any, Dict
from unittest.mock import patch

import pytest
import toml

from src.config import Config, ConfigSingleton
from src.exceptions import ConfigReadError, ConfigWriteError


class TestConfig:
    @pytest.fixture(autouse=True)
    def config(self, config_path: str):
        ConfigSingleton().clear()
        singleton = ConfigSingleton(config_path)
        instance = singleton.instance()
        yield instance
        if hasattr(singleton, "_instance"):
            singleton.clear()
        del singleton

    @pytest.fixture(autouse=True)
    def empty_config(self):
        ConfigSingleton().clear()
        singleton = ConfigSingleton()
        instance = singleton.instance()
        yield instance
        if hasattr(singleton, "_instance"):
            singleton.clear()
        del singleton

    @pytest.fixture(autouse=True)
    def config_path(self) -> str:
        return "tests/data/config/test_config.toml"

    @pytest.fixture(autouse=True)
    def alt_config_path(self) -> str:
        return "tests/data/config/test_config_alt.toml"

    @pytest.fixture(autouse=True)
    def broken_config_path(self) -> str:
        return "tests/data/config/test_config_broken.toml"

    @pytest.fixture(autouse=True)
    def invalid_config_path(self) -> str:
        return "invalid/path/to/config/test_config.toml"

    @pytest.fixture(autouse=True)
    def save_config_path(self) -> str:
        return "tests/data/generated/generated_config.toml"

    @pytest.fixture(autouse=True)
    def expected_config_data(self) -> Dict[str, Any]:
        return {
            "test_section_1": {"test_1": "test_1", "test_2": 2, "test_3": ["test_3"], "test_4": True},
            "test_section_2": {"test_1": "test_1", "test_2": 2, "test_3": ["test_3"], "test_4": True},
        }

    @pytest.fixture(autouse=True)
    def expected_alt_config_data(self) -> Dict[str, Any]:
        return {
            "test_section_0": {"test_1": "test_1", "test_2": 2, "test_3": ["test_3"], "test_4": True},
            "test_section_1": {"test_1": "test_1", "test_2": 2, "test_3": ["test_3"], "test_4": True},
        }

    @pytest.fixture(autouse=True)
    def config_save_data(self, expected_config_data: Dict[str, Any]) -> Dict[str, Any]:
        return expected_config_data

    @pytest.fixture(autouse=True)
    def expected_save_data(self):
        return re.sub(
            r"[\t\s]*",
            "",
            """
            [test_section_1]
            test_1 = "test_1"
            test_2 = 2
            test_3 = ["test_3",]
            test_4 = true

            [test_section_2]
            test_1 = "test_1"
            test_2 = 2
            test_3 = ["test_3",]
            test_4 = true
            """.strip(),
        )

    def test_config_init_without_file_path(self, empty_config: Config) -> None:
        assert empty_config._config_file_path is None

    def test_config_init_with_file_path(self, config: Config) -> None:
        assert config._config_file_path is not None

    class TestConfigRead:
        def test_config_read_from_init(self, config: Config, expected_config_data: Dict[str, Any]) -> None:
            config = config.read()
            assert config.items() == expected_config_data.items()

        def test_config_read_from_valid_path(self, empty_config: Config, config_path: str, expected_config_data: Dict[str, Any]) -> None:
            empty_config = empty_config.read(config_path)
            assert empty_config.items() == expected_config_data.items()

        def test_config_read_from_missing_path(self, empty_config: Config) -> None:
            with pytest.raises(ConfigReadError, match=r".*\ no file was specified.$"):
                empty_config.read()

        def test_config_read_from_empty_path(self, empty_config: Config) -> None:
            with pytest.raises(ConfigReadError, match=r"^Unable to read config file at:"):
                empty_config.read("")

        def test_config_read_from_invalid_path(self, empty_config: Config, invalid_config_path: str) -> None:
            with pytest.raises(ConfigReadError, match=r"^Unable to read config file at:"):
                empty_config.read(invalid_config_path)

        def test_config__read_from_file_valid_path(self, empty_config: Config, config_path: str, expected_config_data: Dict[str, Any]) -> None:
            search_path = pathlib.Path.cwd() / config_path
            empty_config._read_from_file(search_path)
            assert empty_config.items() == expected_config_data.items()

        def test_config__read_from_file_empty_path(self, empty_config: Config) -> None:
            search_path = pathlib.Path.cwd() / ""
            with pytest.raises(ConfigReadError, match=r"^Unable to open config file to read at:"):
                empty_config._read_from_file(search_path)

        def test_config__read_from_file_invalid_path(self, empty_config: Config, invalid_config_path: str) -> None:
            search_path = pathlib.Path.cwd() / invalid_config_path
            with pytest.raises(ConfigReadError, match=r"^Unable to open config file to read at:"):
                empty_config._read_from_file(search_path)

        def test_config__read_from_file_invalid_toml(self, empty_config: Config, broken_config_path: str) -> None:
            search_path = pathlib.Path.cwd() / broken_config_path
            with pytest.raises(ConfigReadError, match=r"^Unable to read config file at:"):
                empty_config._read_from_file(search_path)

    class TestConfigSave:
        def _validate_saved_data(self, actual, expected) -> bool:
            return re.sub(r"[\t\s]*", "", actual) == re.sub(r"[\t\s]*", "", expected)

        def test_config_save_no_target_paths(self, empty_config: Config) -> None:
            empty_config._config_file_path = None
            with pytest.raises(ConfigWriteError, match=r"^Unable to save data to a config file"):
                empty_config.save()

        def test_config_save_valid_data_no_file_path(
            self, empty_config: Config, save_config_path: str, config_save_data: Dict[str, Any], expected_save_data: str
        ) -> None:
            empty_config._config_file_path = pathlib.Path.cwd() / save_config_path
            empty_config.update(config_save_data)
            saved_data: str = empty_config.save()
            assert self._validate_saved_data(saved_data, expected_save_data) is True

        def test_config_save_valid_data_with_file_path(
            self, empty_config: Config, save_config_path: str, config_save_data: Dict[str, Any], expected_save_data: str
        ) -> None:
            empty_config.update(config_save_data)
            saved_data: str = empty_config.save(save_config_path)
            assert self._validate_saved_data(saved_data, expected_save_data) is True

        @patch.object(toml, "dump")
        def test_config_save_toml_dump_failed(self, toml_return, empty_config: Config, save_config_path: str) -> None:
            toml_return.return_value = None
            empty_config._config_file_path = pathlib.Path.cwd() / save_config_path
            with pytest.raises(ConfigWriteError, match=r"^Unable to save data to a config file at:"):
                empty_config.save()

        def test_config_save_invalid_path(self, empty_config: Config, invalid_config_path: str) -> None:
            empty_config._config_file_path = pathlib.Path.cwd() / invalid_config_path
            with pytest.raises(ConfigWriteError, match=r"^Unable to save config file at:"):
                empty_config.save()

    class TestConfigReset:
        def test_config_reset_valid_field(self, empty_config: Config) -> None:
            empty_config.update({"field": "test"})
            assert empty_config.reset("field") is True
            assert empty_config.get("field") is None

        def test_config_reset_invalid_field(self, empty_config: Config) -> None:
            assert empty_config.reset("field") is False

    class TestConfigSet:
        def test_config_set_valid_field(self, empty_config: Config) -> None:
            empty_config.update({"field": "test1"})
            assert empty_config.set("field", "test2") is True
            assert empty_config.get("field") == "test2"

        def test_config_set_new_field(self, empty_config: Config) -> None:
            empty_config.set("field", "test")
            assert empty_config.get("field") == "test"

        def test_config_set_invalid_field(self, empty_config: Config) -> None:
            assert empty_config.set(None, "") is False  # type: ignore
