import copy
import pathlib
from logging import getLogger
from typing import Any, Optional

import toml


_logger = getLogger(__name__)


class LogConfig(dict):
    _config_file_path: Optional[pathlib.Path] = None
    _initial_config: Optional["LogConfig"] = None

    def __init__(self, file_name: Optional[str] = None) -> None:
        super().__init__()
        if file_name is not None:
            self._config_file_path = pathlib.Path.cwd() / file_name

    def read(self, file_name: Optional[str] = None) -> "LogConfig":
        if file_name is None:
            if self._config_file_path is None:
                raise IOError("Unable to read config file because no file was specified.")
            self._read_from_file(self._config_file_path)
            return self
        search_path = pathlib.Path.cwd() / file_name
        if search_path.exists() and search_path.is_file():
            self._read_from_file(search_path)
            return self
        raise IOError(f"Unable to read config file at: {search_path}")

    def _read_from_file(self, file_path: pathlib.Path):
        try:
            with open(str(file_path.resolve()), "r", encoding="utf-8") as file_handler:
                contents = toml.load(file_handler, _dict=dict)
                self.update(contents)
                self._config_file_path = file_path
                if self._initial_config is None:
                    self._initial_config = LogConfig()
                    self._initial_config._config_file_path = self._config_file_path
                    self._initial_config.update(self)
        except toml.TomlDecodeError as exc:
            raise IOError(f"Unable to read config file at: {file_path}.") from exc
        except IOError as exc:
            raise IOError(f"Unable to open config file to read at: {file_path}.") from exc

    def save(
        self,
        file_name: Optional[str] = None,
        modified_only: bool = False,
        modified_field_name: Optional[str] = None,
    ) -> str:
        target_path = None
        if file_name is not None:
            target_path = file_name
        elif self._config_file_path is not None:
            target_path = str(self._config_file_path.resolve())
        else:
            raise IOError("Unable to save data to a config file because no file was specified.")

        try:
            saved_data = None
            with open(target_path, "w", encoding="utf-8") as file_handler:
                if not modified_only:
                    saved_data = toml.dump(self, file_handler)
                else:
                    if not modified_field_name:
                        raise IOError("Unable to save modified data to a config file because the field name is invalid.")
                    field = self.get(modified_field_name)
                    if field is None:
                        raise IOError("Unable to save modified data to a config file because the field name does not exist.")
                    if self._initial_config is None:
                        raise IOError("Unable to save modified data to a config file because no file has been initialized.")
                    self._initial_config.set(modified_field_name, field)
                    saved_data = toml.dump(self._initial_config, file_handler)
            if saved_data is None:
                raise IOError(f"Unable to save data to a config file at: {target_path}")
        except IOError as exc:
            raise IOError(f"Unable to save config file at: {target_path}", _logger) from exc
        return saved_data

    def reset(self, field_name: str) -> bool:
        return self.set(field_name, None, create_keys_if_not_exists=False)

    def get(self, field_name: str, fallback: Optional[Any] = None) -> Any:
        if not field_name:
            return None
        field = self._get_field(field_name)
        if field is None:
            if fallback is not None:
                return fallback
            return None
        return field

    def _get_field(self, field_name: str):
        field_sections = field_name.split(".")
        fields_copy = copy.deepcopy(self)
        try:
            for key in field_sections:
                fields_copy = fields_copy[key]
        except KeyError:
            return None
        return fields_copy

    def set(self, field_name: str, field_value: Optional[Any] = None, create_keys_if_not_exists: bool = False) -> bool:
        if not field_name:
            return False
        return self._set_field(field_name, field_value, create_keys_if_not_exists)

    def _set_field(self, field_name: str, field_value: Optional[Any] = None, create_keys_if_not_exists: bool = False):
        if not create_keys_if_not_exists and self.get(field_name) is None:
            return False
        field_sections = field_name.split(".")
        for key in field_sections[:-1]:
            self = self.setdefault(key, {})
        self[field_sections[-1]] = field_value
        return True
