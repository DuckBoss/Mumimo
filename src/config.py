import copy
import logging
import pathlib
from typing import Any, Dict, Optional, Union

import toml

from .exceptions import ConfigReadError, ConfigWriteError

_logger = logging.getLogger(__name__)


class Config(dict):
    _config_file_path: Optional[pathlib.Path] = None
    _initial_config: Optional["Config"] = None

    def __init__(self, file_name: Optional[Union[str, pathlib.Path]] = None) -> None:
        super().__init__()
        if file_name is not None:
            if isinstance(file_name, str):
                self._config_file_path = (pathlib.Path.cwd() / file_name).resolve()
            else:
                self._config_file_path = file_name.resolve()

    def read(self, file_name: Optional[pathlib.Path] = None) -> "Config":
        if not file_name:
            if not self._config_file_path:
                raise ConfigReadError("Unable to read config file because no file was specified.", _logger)
            self._read_from_file(self._config_file_path)
            return self
        if file_name.is_file():
            self._read_from_file(file_name)
            return self
        raise ConfigReadError(f"Unable to read config file at: {file_name}", _logger)

    def _read_from_file(self, file_path: pathlib.Path):
        try:
            with open(str(file_path), "r", encoding="utf-8") as file_handler:
                contents: Dict[str, Any] = toml.load(file_handler, _dict=dict)
                self.clear()
                self.update(contents)
                self._config_file_path = file_path
                if self._initial_config is None:
                    self._initial_config = Config()
                    self._initial_config._config_file_path = self._config_file_path
                    self._initial_config.clear()
                    self._initial_config.update(self)
        except toml.TomlDecodeError as exc:
            raise ConfigReadError(f"Unable to read config file at: {file_path}.", _logger) from exc
        except IOError as exc:
            raise ConfigReadError(f"Unable to open config file to read at: {file_path}.", _logger) from exc

    def save(
        self,
        file_path: Optional[pathlib.Path] = None,
        modified_only: bool = False,
        modified_field_name: Optional[str] = None,
    ) -> str:
        target_path = None
        if file_path is not None:
            target_path = file_path
        elif self._config_file_path is not None:
            target_path = self._config_file_path
        else:
            raise ConfigWriteError("Unable to save data to a config file because no file was specified.", _logger)

        try:
            saved_data = None
            with open(str(target_path), "w", encoding="utf-8") as file_handler:
                if not modified_only:
                    saved_data = toml.dump(self, file_handler)
                else:
                    if not modified_field_name:
                        raise ConfigWriteError("Unable to save modified data to a config file because the field name is invalid.", _logger)
                    field = self.get(modified_field_name)
                    if field is None:
                        raise ConfigWriteError("Unable to save modified data to a config file because the field name does not exist.", _logger)
                    if self._initial_config is None:
                        raise ConfigWriteError("Unable to save modified data to a config file because no file has been initialized.", _logger)
                    self._initial_config.set(modified_field_name, field)
                    saved_data = toml.dump(self._initial_config, file_handler)
            if saved_data is None:
                raise ConfigWriteError(f"Unable to save data to a config file at: {target_path}", _logger)
        except IOError as exc:
            raise ConfigWriteError(f"Unable to save config file at: {target_path} | {exc}", _logger) from exc
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
