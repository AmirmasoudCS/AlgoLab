from __future__ import annotations

from abc import ABC, abstractmethod

from .model import CircularQueue


class CircularQueueOperation(ABC):
    """Base class for circular queue operations."""

    @abstractmethod
    def commit(self, queue: CircularQueue) -> object | None:
        """Apply the operation to the given circular queue."""
        raise NotImplementedError


class EnqueueOperation(CircularQueueOperation):
    """Enqueue a value into the circular queue."""

    def __init__(self, value: object) -> None:
        self.value = value

    def commit(self, queue: CircularQueue) -> int:
        return queue.enqueue(self.value)


class DequeueOperation(CircularQueueOperation):
    """Dequeue the front value from the circular queue."""

    def commit(self, queue: CircularQueue) -> object:
        return queue.dequeue()


class PeekOperation(CircularQueueOperation):
    """Peek at the front value without modifying the circular queue."""

    def commit(self, queue: CircularQueue) -> object:
        return queue.peek()