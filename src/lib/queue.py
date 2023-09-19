import logging
from typing import List, Optional, Any

from ..exceptions import ServiceError


logger = logging.getLogger(__name__)


class Queue:
    _queue: List[Any] = []
    _max_size: int = 0

    DEFAULT_QUEUE_LIMIT: int = 100

    def __init__(self, max_size: Optional[int] = DEFAULT_QUEUE_LIMIT) -> None:
        if not isinstance(max_size, int) or max_size < 0:
            raise ServiceError(
                "Cannot initialize queue: the provided max size must be a non-negative number.",
                logger=logger,
            )
        if max_size is not None:
            self._max_size = max_size
        else:
            self._max_size = self.DEFAULT_QUEUE_LIMIT

    @property
    def size(self) -> int:
        return len(self._queue)

    @property
    def max_size(self) -> int:
        return self._max_size

    @property
    def queue(self) -> List[Any]:
        return self._queue

    def enqueue_many(self, messages: List[Any]) -> bool:
        for message in messages:
            if not self.enqueue(message):
                return False
        return True

    def enqueue(self, message: Any) -> bool:
        if self.size >= self.max_size:
            logger.warning(f"Unable to enqueue item to the processing queue: {message}")
            return False
        self._queue.append(message)
        return True

    def dequeue(self) -> Optional[Any]:
        if self.size == 0:
            return None
        return self.queue.pop(0)
