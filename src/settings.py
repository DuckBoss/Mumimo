from typing import TYPE_CHECKING, Callable, Dict, Optional

from .lib.singleton import singleton

if TYPE_CHECKING:
    from .client_state import ClientState
    from .config import Config
    from .lib.command_callbacks import CommandCallbacks
    from .log_config import LogConfig


@singleton
class MumimoSettings:
    _mumimo_cfg: Optional["Config"] = None
    _log_cfg: Optional["LogConfig"] = None
    _client_state: Optional["ClientState"] = None
    _registered_plugins: Dict[str, Callable] = {}
    _cmd_callbacks: Optional["CommandCallbacks"] = None

    def get_mumimo_config(self) -> Optional["Config"]:
        return self._mumimo_cfg

    def set_mumimo_config(self, cfg: "Config") -> None:
        self._mumimo_cfg = cfg

    def get_log_config(self) -> Optional["LogConfig"]:
        return self._log_cfg

    def set_log_config(self, cfg: "LogConfig") -> None:
        self._log_cfg = cfg

    def get_client_state(self) -> Optional["ClientState"]:
        return self._client_state

    def set_client_state(self, client_state: "ClientState") -> None:
        self._client_state = client_state

    def get_registered_plugins(self) -> Dict[str, Callable]:
        return self._registered_plugins

    def get_command_callbacks(self) -> Optional["CommandCallbacks"]:
        return self._cmd_callbacks

    def set_command_callbacks(self, callbacks: "CommandCallbacks") -> None:
        self._cmd_callbacks = callbacks


settings = MumimoSettings()
