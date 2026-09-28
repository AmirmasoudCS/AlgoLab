from __future__ import annotations

from abc import ABC, abstractmethod

from .model import PriorityEntry, PriorityQueue


class PriorityQueueOperation(ABC):
    """Base class for priority queue operations."""

    @abstractmethod
    def commit(self, queue: PriorityQueue) -> object | None:
        """Apply the operation to the given priority queue."""
        raise NotImplementedError


class InsertOperation(PriorityQueueOperation):
    """Insert a value with a priority."""

    def __init__(self, value: object, priority: float) -> None:
        self.value = value
        self.priority = priority

    def commit(self, queue: PriorityQueue) -> int:
        return queue.insert(self.value, self.priority)


class ExtractOperation(PriorityQueueOperation):
    """Remove and return the highest-priority entry."""

    def commit(self, queue: PriorityQueue) -> PriorityEntry:
        return queue.extract()


class PeekOperation(PriorityQueueOperation):
    """Peek at the highest-priority entry without modifying the queue."""

    def commit(self, queue: PriorityQueue) -> PriorityEntry:
        return queue.peek()