import logging
from typing import List, Optional, Tuple, Union

from .command import Command
from .queue import Queue

logger = logging.getLogger(__name__)


class MessageQueue(Queue):
    _queue: List[Tuple[Union[str, List[str]], Command]] = []
    _max_size: int = 0

    DEFAULT_QUEUE_LIMIT: int = 100

    def __init__(self, max_size: Optional[int] = DEFAULT_QUEUE_LIMIT) -> None:
        super().__init__(max_size)

    @property
    def queue(self) -> List[Tuple[Union[str, List[str]], Command]]:
        return self._queue

    def enqueue_many(self, messages: List[Tuple[Union[str, List[str]], Command]]) -> bool:
        for message in messages:
            if not self.enqueue(message):
                return False
        return True

    def enqueue(self, message: Tuple[Union[str, List[str]], Command]) -> bool:
        if self.size >= self.max_size:
            logger.warning(f"Unable to enqueue message to the output queue: {message[1].command}.{message[0]}")
            return False
        self._queue.append(message)
        return True

    def dequeue(self) -> Optional[Tuple[Union[str, List[str]], Command]]:
        if self.size == 0:
            return None
        return self.queue.pop(0)
