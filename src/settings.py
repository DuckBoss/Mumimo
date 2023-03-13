from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .client_state import ClientState
    from .config import Config
    from .log_config import LogConfig


class MumimoSettings:
    _mumimo_cfg: Optional["Config"] = None
    _log_cfg: Optional["LogConfig"] = None
    _client_state: Optional["ClientState"] = None

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


settings = MumimoSettings()
