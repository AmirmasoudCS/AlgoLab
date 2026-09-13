from __future__ import annotations

from abc import ABC, abstractmethod

from .model import Heap


class HeapOperation(ABC):
    """Base class for operations performed on a heap."""

    @abstractmethod
    def commit(self, heap: Heap) -> object | None:
        """Apply the operation to the heap."""
        raise NotImplementedError


class InsertOperation(HeapOperation):
    """Insert a value into the heap."""

    def __init__(self, value: object) -> None:
        self.value = value

    def commit(self, heap: Heap) -> None:
        """Insert the value into the heap."""
        heap.insert(self.value)


class PeekOperation(HeapOperation):
    """Inspect the root value without removing it."""

    def commit(self, heap: Heap) -> object:
        """Return the root value."""
        return heap.peek()


class ExtractOperation(HeapOperation):
    """Remove and return the root value."""

    def commit(self, heap: Heap) -> object:
        """Extract and return the root value."""
        return heap.extract()


class BuildHeapOperation(HeapOperation):
    """Build a heap from a collection of values."""

    def __init__(self, values: list[object]) -> None:
        self.values = values.copy()

    def commit(self, heap: Heap) -> None:
        """Build the heap from the provided values."""
        heap.build_heap(self.values)


class ClearOperation(HeapOperation):
    """Remove all values from the heap."""

    def commit(self, heap: Heap) -> None:
        """Clear the heap."""
        heap.clear()