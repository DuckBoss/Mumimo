import pathlib
from typing import Any, Optional

import toml

from .exceptions import ConfigReadError, ConfigWriteError


class ConfigSingleton:
    _config_instance: Optional["Config"] = None

    def __new__(cls, *args, **kwargs) -> "ConfigSingleton":
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
            cls._instance._config_instance = Config(*args, **kwargs)
        return cls._instance

    @classmethod
    def instance(cls) -> Optional["Config"]:
        if cls._instance is not None:
            return cls._instance._config_instance
        return None

    @classmethod
    def clear(cls) -> None:
        if cls._instance is not None:
            del cls._instance


class Config(dict):
    _config_file_path: Optional[pathlib.Path] = None
    _initial_config: Optional["Config"] = None

    def __init__(self, file_name: Optional[str] = None) -> None:
        super().__init__()
        if file_name is not None:
            self._config_file_path = pathlib.Path.cwd() / file_name

    def read(self, file_name: Optional[str] = None) -> "Config":
        if file_name is None:
            if self._config_file_path is None:
                raise ConfigReadError("Unable to read config file because no file was specified.")
            self._read_from_file(self._config_file_path)
            return self
        search_path = pathlib.Path.cwd() / file_name
        if search_path.is_file():
            self._read_from_file(search_path)
            return self
        raise ConfigReadError(f"Unable to read config file at: {search_path}")

    def _read_from_file(self, file_path: pathlib.Path):
        try:
            with open(str(file_path.resolve()), "r", encoding="utf-8") as file_handler:
                contents = toml.load(file_handler, _dict=dict)
                self.update(contents)
                self._config_file_path = file_path
                if self._initial_config is None:
                    self._initial_config = Config()
                    self._initial_config._config_file_path = self._config_file_path
                    self._initial_config.update(self)
        except toml.TomlDecodeError as exc:
            raise ConfigReadError(f"Unable to read config file at: {file_path}.") from exc
        except IOError as exc:
            raise ConfigReadError(f"Unable to open config file to read at: {file_path}.") from exc

    def save(
        self,
        file_name: Optional[str] = None,
        modified_only: bool = False,
        modified_field_name: Optional[str] = None,
        modified_sub_field_name: Optional[str] = None,
    ) -> str:
        target_path = None
        if file_name is not None:
            target_path = file_name
        elif self._config_file_path is not None:
            target_path = str(self._config_file_path.resolve())
        else:
            raise ConfigWriteError("Unable to save data to a config file because no file was specified.")

        try:
            saved_data = None
            with open(target_path, "w", encoding="utf-8") as file_handler:
                if not modified_only:
                    saved_data = toml.dump(self, file_handler)
                else:
                    if not modified_field_name:
                        raise ConfigWriteError("Unable to save modified data to a config file because the section name is invalid.")
                    if not modified_sub_field_name:
                        raise ConfigWriteError("Unable to save modified data to a config file because the field name is invalid.")
                    field = self.get(modified_field_name, modified_sub_field_name)
                    if field is None:
                        raise ConfigWriteError("Unable to save modified data to a config file because the field name is invalid.")
                    if self._initial_config is None:
                        raise ConfigWriteError("Unable to save modified data to a config file because no file has been initialized.")
                    self._initial_config[modified_field_name].update({modified_sub_field_name: field})
                    saved_data = toml.dump(self._initial_config, file_handler)
            if saved_data is None:
                raise ConfigWriteError(f"Unable to save data to a config file at: {target_path}")
        except IOError as exc:
            raise ConfigWriteError(f"Unable to save config file at: {target_path}") from exc
        return saved_data

    def reset(self, field_name: str) -> bool:
        field = self.get(field_name)
        if field is not None:
            self[field_name] = None
            return True
        return False

    def get(self, field_name: str, sub_field_name: Optional[str] = None, fallback: Optional[Any] = None) -> Any:
        if sub_field_name is None:
            field = super().get(field_name)
            if field is None:
                if fallback is not None:
                    return fallback
                return None
            return field
        if field_name is None:
            raise ConfigReadError("A field section must be provided to query a subfield.")
        field = super().get(field_name)
        if field is None:
            raise ConfigReadError(f"Unable to find section: {field_name}")
        sub_field = field.get(sub_field_name)
        if sub_field is None:
            if fallback is not None:
                return fallback
            return None
        return sub_field

    def set(self, field_name: str, sub_field_name: Optional[str] = None, sub_field_value: Optional[Any] = None) -> bool:
        if not field_name:
            return False
        if self.get(field_name) is None:
            self[field_name] = {}
            if not sub_field_name:
                return True
        if not sub_field_name:
            return False
        self[field_name][sub_field_name] = sub_field_value
        return True
