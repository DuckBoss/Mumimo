import logging
from typing import List, Optional

from .command import Command
from .queue import Queue

logger = logging.getLogger(__name__)


class CommandQueue(Queue):
    _queue: List[Command] = []
    _max_size: int = 0

    DEFAULT_QUEUE_LIMIT: int = 100

    def __init__(self, max_size: Optional[int] = DEFAULT_QUEUE_LIMIT) -> None:
        super().__init__(max_size)

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
