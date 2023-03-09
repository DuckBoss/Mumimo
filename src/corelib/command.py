from typing import List, Optional


class Command:
    _command: Optional[str]
    _message: str
    _parameters: List[str]
    _channel_id: int
    _session_id: int
    _actor: int

    def __init__(
        self,
        command: Optional[str] = None,
        parameters: Optional[List[str]] = None,
        message: str = "",
        actor: int = -1,
        channel_id: Optional[int] = -1,
        session_id: Optional[int] = -1,
    ) -> None:
        self._command = command
        self._message = message
        self._actor = actor

        if not isinstance(channel_id, int):
            self._channel_id = -1
        else:
            self._channel_id = channel_id

        if not isinstance(session_id, int):
            self._session_id = -1
        else:
            self._session_id = session_id

        if parameters is None:
            parameters = []
        self._parameters = parameters

    @property
    def command(self) -> Optional[str]:
        return self._command

    @command.setter
    def command(self, value: str) -> None:
        self._command = value

    @property
    def message(self) -> str:
        return self._message

    @message.setter
    def message(self, value: str) -> None:
        self._message = value

    @property
    def parameters(self) -> List[str]:
        return self._parameters

    @parameters.setter
    def parameters(self, value: List[str]):
        self._parameters = value

    @property
    def actor(self) -> int:
        return self._actor

    @actor.setter
    def actor(self, value: int) -> None:
        self._actor = value

    @property
    def channel_id(self) -> int:
        return self._channel_id

    @channel_id.setter
    def channel_id(self, value: int) -> None:
        self._channel_id = value

    @property
    def session_id(self) -> int:
        return self._session_id

    @session_id.setter
    def session_id(self, value: int) -> None:
        self._session_id = value

    @property
    def is_private(self) -> bool:
        return self._session_id > -1 and self._channel_id == -1
