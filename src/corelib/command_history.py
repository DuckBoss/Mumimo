from copy import deepcopy
from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from .command import Command


class CommandHistory:
    _history: List["Command"]
    _limit: int

    DEFAULT_HISTORY_LIMIT: int = 1000

    @property
    def history(self) -> List["Command"]:
        return self._history

    @property
    def length(self) -> int:
        return len(self._history)

    @property
    def limit(self) -> int:
        return self._limit

    @limit.setter
    def limit(self, value: int) -> None:
        if value <= 0:
            self._limit = self.DEFAULT_HISTORY_LIMIT
            return
        self._limit = value

    def __init__(self, history_limit: Optional[int] = DEFAULT_HISTORY_LIMIT) -> None:
        self._history = []
        if history_limit is not None:
            self.limit = history_limit
        else:
            self.limit = self.DEFAULT_HISTORY_LIMIT

    def get_last(self, last_n: int = 1) -> List["Command"]:
        if last_n < 1:
            return []
        reverse_history = list(reversed(self._history))
        return reverse_history[:last_n]

    def add(self, command: "Command") -> Optional["Command"]:
        if self.length >= self.limit:
            return None
        to_add = deepcopy(command)
        self._history.append(to_add)
        return to_add

    def pop(self, idx: int) -> Optional["Command"]:
        try:
            return self._history.pop(idx)
        except IndexError:
            return None

    def clear(self) -> None:
        self._history.clear()
