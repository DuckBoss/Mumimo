import pathlib
import re
from typing import Any, Dict
from unittest.mock import patch

import pytest
import toml

from src.config import Config
from src.exceptions import ConfigReadError, ConfigWriteError


class TestConfig:
    @pytest.fixture(autouse=True)
    def config(self, config_path: str) -> Config:
        return Config(config_path)

    @pytest.fixture(autouse=True)
    def empty_config(self) -> Config:
        return Config()

    @pytest.fixture(autouse=True)
    def config_path(self) -> pathlib.Path:
        return pathlib.Path.cwd() / "tests/data/config/test_config.toml"

    @pytest.fixture(autouse=True)
    def alt_config_path(self) -> pathlib.Path:
        return pathlib.Path.cwd() / "tests/data/config/test_config_alt.toml"

    @pytest.fixture(autouse=True)
    def broken_config_path(self) -> pathlib.Path:
        return pathlib.Path.cwd() / "tests/data/config/test_config_broken.toml"

    @pytest.fixture(autouse=True)
    def invalid_config_path(self) -> pathlib.Path:
        return pathlib.Path.cwd() / "invalid/path/to/config/test_config.toml"

    @pytest.fixture(autouse=True)
    def save_config_path(self) -> pathlib.Path:
        return pathlib.Path.cwd() / "tests/data/generated/generated_config.toml"

    @pytest.fixture(autouse=True)
    def expected_config_data(self) -> Dict[str, Any]:
        return {
            "test_section_1": {"test_1": "test_1", "test_2": 2, "test_3": ["test_3"], "test_4": True, "nested": {"test_1": "test_1"}},
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

            [test_section_1.nested]
            test_1 = "test_1"
            """.strip(),
        )

    @pytest.fixture(autouse=True)
    def expected_save_data_modified_only(self):
        return re.sub(
            r"[\t\s]*",
            "",
            """
            [test]
            test_1 = false
            test_2 = true
            """.strip(),
        )

    def test_config_init_without_file_path(self, empty_config: Config, caplog) -> None:
        assert empty_config._config_file_path is None

    def test_config_init_with_file_path(self, config: Config) -> None:
        assert config._config_file_path is not None

    class TestConfigRead:
        def test_config_read_from_init(self, config: Config, expected_config_data: Dict[str, Any]) -> None:
            config = config.read()
            assert config.items() == expected_config_data.items()

        def test_config_read_from_valid_path(self, empty_config: Config, config_path: pathlib.Path, expected_config_data: Dict[str, Any]) -> None:
            empty_config = empty_config.read(config_path)
            assert empty_config.items() == expected_config_data.items()

        def test_config_read_from_missing_path(self, empty_config: Config) -> None:
            empty_config._config_file_path = None
            with pytest.raises(ConfigReadError, match=r".*\ no file was specified.$"):
                empty_config.read()

        def test_config_read_from_invalid_path(self, empty_config: Config, invalid_config_path: pathlib.Path) -> None:
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

        def test_config_save_modified_data_only(self, empty_config: Config, save_config_path: str, expected_save_data_modified_only: str) -> None:
            original_config = {"test": {"test_1": True, "test_2": True}}
            updates = {"test": {"test_1": False, "test_2": True}}
            empty_config.update(original_config)
            empty_config._config_file_path = pathlib.Path.cwd() / save_config_path
            empty_config._initial_config = Config()
            empty_config._initial_config._config_file_path = empty_config._config_file_path
            empty_config._initial_config.update(empty_config)
            empty_config.update(updates)
            saved_data: str = empty_config.save(modified_only=True, modified_field_name="test.test_1")
            assert self._validate_saved_data(saved_data, expected_save_data_modified_only) is True

        def test_config_save_modified_data_only_missing_initial_config(self, empty_config: Config, save_config_path: str) -> None:
            original_config = {"test": {"test_1": True, "test_2": True}}
            updates = {"test": {"test_1": False, "test_2": True}}
            empty_config._initial_config = None
            empty_config.update(original_config)
            empty_config._config_file_path = pathlib.Path.cwd() / save_config_path
            empty_config.update(updates)
            with pytest.raises(ConfigWriteError, match=r"because no file has been initialized.$"):
                empty_config.save(modified_only=True, modified_field_name="test.test_1")

        def test_config_save_modified_data_only_no_section_provided(self, empty_config: Config, save_config_path: str) -> None:
            original_config = {"test": {"test_1": True, "test_2": True}}
            updates = {"test": {"test_1": False, "test_2": True}}
            empty_config.update(original_config)
            empty_config._config_file_path = pathlib.Path.cwd() / save_config_path
            empty_config._initial_config = Config()
            empty_config._initial_config._config_file_path = empty_config._config_file_path
            empty_config._initial_config.update(empty_config)
            empty_config.update(updates)
            with pytest.raises(ConfigWriteError, match=r"the field name is invalid.$"):
                empty_config.save(modified_only=True, modified_field_name="")

        def test_config_save_modified_data_only_invalid_field_provided(self, empty_config: Config, save_config_path: str) -> None:
            original_config = {"test": {"test_1": True, "test_2": True}}
            updates = {"test": {"test_1": False, "test_2": True}}
            empty_config.update(original_config)
            empty_config._config_file_path = pathlib.Path.cwd() / save_config_path
            empty_config._initial_config = Config()
            empty_config._initial_config._config_file_path = empty_config._config_file_path
            empty_config._initial_config.update(empty_config)
            empty_config.update(updates)
            with pytest.raises(ConfigWriteError, match=r"the field name does not exist.$"):
                empty_config.save(modified_only=True, modified_field_name="testing123")

        def test_config_save_modified_data_only_invalid_nested_field_provided(self, empty_config: Config, save_config_path: str) -> None:
            original_config = {"test": {"test_1": True, "test_2": True}}
            updates = {"test": {"test_1": False, "test_2": True}}
            empty_config.update(original_config)
            empty_config._config_file_path = pathlib.Path.cwd() / save_config_path
            empty_config._initial_config = Config()
            empty_config._initial_config._config_file_path = empty_config._config_file_path
            empty_config._initial_config.update(empty_config)
            empty_config.update(updates)
            with pytest.raises(ConfigWriteError, match=r"the field name does not exist.$"):
                empty_config.save(modified_only=True, modified_field_name="test.testing123")

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

        def test_config_reset_valid_nested_field(self, empty_config: Config) -> None:
            empty_config.update({"outer": {"inner": "test"}})
            assert empty_config.reset("outer.inner") is True
            assert empty_config.get("outer.inner") is None

        def test_config_reset_invalid_field_is_empty(self, empty_config: Config) -> None:
            assert empty_config.reset("") is False

        def test_config_reset_invalid_field_does_not_exist(self, empty_config: Config) -> None:
            assert empty_config.reset("field") is False

        def test_config_reset_invalid_nested_field_does_not_exist(self, empty_config: Config) -> None:
            empty_config.update({"outer": {"inner": "test"}})
            assert empty_config.reset("outer.invalid_inner") is False

    class TestConfigSet:
        def test_config_set_field_value_when_section_exists(self, empty_config: Config) -> None:
            empty_config.update({"main": {"field": "test1"}})
            assert empty_config.set("main.field", "test2") is True
            assert empty_config.get("main.field") == "test2"

        def test_config_set_field_value_fails_when_nested_field_does_not_exist(self, empty_config: Config) -> None:
            empty_config.update({"main": {"field": "test1"}})
            assert empty_config.set("main.new_field", "test2") is False
            assert empty_config.get("main.new_field") is None

        def test_config_set_new_nested_field_with_value_when_field_does_not_exist(self, empty_config: Config) -> None:
            empty_config.update({"main": {}})
            assert empty_config.set("main.new_field", "test2", create_keys_if_not_exists=True) is True
            assert empty_config.get("main.new_field") == "test2"

        def test_config_set_new_nested_field_with_none_when_field_does_not_exist(self, empty_config: Config) -> None:
            empty_config.update({"main": {}})
            assert empty_config.set("main.field", None, create_keys_if_not_exists=True) is True
            assert empty_config.get("main.field") is None
            assert empty_config == {"main": {"field": None}}

        def test_config_set_new_nested_field_with_empty_string_when_field_does_not_exist(self, empty_config: Config) -> None:
            empty_config.update({"main": {}})
            assert empty_config.set("main.field", "", create_keys_if_not_exists=True) is True
            assert empty_config.get("main.field") == ""
            assert empty_config == {"main": {"field": ""}}

        def test_config_set_new_nested_field_with_empty_dict_when_field_does_not_exist(self, empty_config: Config) -> None:
            empty_config.update({"main": {}})
            assert empty_config.set("main.field", {}, create_keys_if_not_exists=True) is True
            assert empty_config.get("main.field") == {}
            assert empty_config == {"main": {"field": {}}}

        def test_config_set_new_section_and_nested_field_when_not_exists(self, empty_config: Config) -> None:
            assert empty_config.set("new_section.field", "test", create_keys_if_not_exists=True) is True
            assert empty_config.get("new_section.field") == "test"
            assert empty_config == {"new_section": {"field": "test"}}

        def test_config_set_new_section_when_not_exists(self, empty_config: Config) -> None:
            assert empty_config.set("new_section", {}, create_keys_if_not_exists=True) is True
            assert empty_config.get("new_section") == {}
            assert empty_config == {"new_section": {}}

        def test_config_set_empty_field_name(self, empty_config: Config) -> None:
            assert empty_config.set("") is False

        def test_config_set_none_field_name(self, empty_config: Config) -> None:
            assert empty_config.set(None) is False  # type: ignore

    class TestConfigGet:
        def test_config_get_field(self, empty_config: Config) -> None:
            empty_config.update({"main": {"test": None}})
            assert empty_config.get("main") == {"test": None}

        def test_config_get_field_does_not_exist(self, empty_config: Config) -> None:
            assert empty_config.get("main") is None

        def test_config_get_field_does_not_exist_fallback(self, empty_config: Config) -> None:
            assert empty_config.get("main", fallback={"test": None}) == {"test": None}

        def test_config_get_exception_when_field_name_is_none(self, empty_config: Config) -> None:
            assert empty_config.get(field_name=None) is None  # type: ignore

        def test_config_get_nested_field_when_parent_field_does_not_exist(self, empty_config: Config) -> None:
            empty_config.update({"main": {"test": None}})
            assert empty_config.get("test.test") is None

        def test_config_get_nested_field(self, empty_config: Config) -> None:
            empty_config.update({"main": {"test": "value"}})
            assert empty_config.get("main.test") == "value"

        def test_config_get_nested_field_does_not_exist(self, empty_config: Config) -> None:
            empty_config.update({"main": {"test": "val"}})
            assert empty_config.get("main.new_test") is None

        def test_config_get_nested_field_does_not_exist_fallback(self, empty_config: Config) -> None:
            empty_config.update({"main": {"test": "val"}})
            assert empty_config.get("main.new_test", fallback={"new_test": "val"}) == {"new_test": "val"}
