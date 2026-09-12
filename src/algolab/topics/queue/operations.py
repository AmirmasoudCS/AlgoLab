from __future__ import annotations

from abc import ABC, abstractmethod

from .model import Queue


class QueueOperation(ABC):
    """Base class for queue operations."""

    @abstractmethod
    def commit(self, queue: Queue) -> object | None:
        """Apply the operation to the given queue."""
        raise NotImplementedError


class EnqueueOperation(QueueOperation):
    """Enqueue a value at the rear of the queue."""

    def __init__(self, value: object) -> None:
        self.value = value

    def commit(self, queue: Queue) -> None:
        queue.enqueue(self.value)


class DequeueOperation(QueueOperation):
    """Dequeue the front value from the queue."""

    def commit(self, queue: Queue) -> object:
        return queue.dequeue()


class PeekOperation(QueueOperation):
    """Peek at the front value without modifying the queue."""

    def commit(self, queue: Queue) -> object:
        return queue.peek()