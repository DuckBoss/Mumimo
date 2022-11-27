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
        if cls._config_instance is not None:
            del cls._config_instance


class Config(dict):
    _config_file_path: Optional[pathlib.Path] = None

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
        except toml.TomlDecodeError as exc:
            raise ConfigReadError(f"Unable to read config file at: {file_path}.") from exc
        except IOError as exc:
            raise ConfigReadError(f"Unable to open config file to read at: {file_path}.") from exc

    def save(self, file_name: Optional[str] = None) -> str:
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
                saved_data = toml.dump(self, file_handler)
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

    def set(self, field_name: str, field_value: Any) -> bool:
        if field_name is None:
            return False
        self[field_name] = field_value
        return True
