import logging
from typing import List, Optional

from ..exceptions import ServiceError
from ..lib.command import Command


logger = logging.getLogger(__name__)


class CommandQueue:
    _queue: List[Command] = []
    _max_size: int = 0

    DEFAULT_COMMAND_QUEUE_LIMIT: int = 100

    def __init__(self, max_size: Optional[int] = DEFAULT_COMMAND_QUEUE_LIMIT) -> None:
        if not isinstance(max_size, int) or max_size < 0:
            raise ServiceError(
                "Cannot initialize command queue: the provided max size must be a non-negative number.",
                logger=logger,
            )
        if max_size is not None:
            self._max_size = max_size
        else:
            self._max_size = self.DEFAULT_COMMAND_QUEUE_LIMIT

    @property
    def size(self) -> int:
        return len(self._queue)

    @property
    def max_size(self) -> int:
        return self._max_size

    @property
    def queue(self) -> List[Command]:
        return self._queue

    def enqueue_many(self, commands: List[Command]) -> bool:
        for command in commands:
            if not self.enqueue(command):
                return False
        return True

    def enqueue(self, command: Command) -> bool:
        if self.size >= self.max_size:
            logger.warning(f"Unable to enqueue command to the processing queue: {command.command}")
            return False
        self._queue.append(command)
        return True

    def dequeue(self) -> Optional[Command]:
        if self.size == 0:
            return None
        return self.queue.pop(0)
