from __future__ import annotations

from abc import ABC, abstractmethod

from .model import SortArray


class SortOperation(ABC):
    """Base class for operations performed on a sortable array."""

    @abstractmethod
    def commit(self, array: SortArray) -> None:
        """Apply the operation to the array."""
        raise NotImplementedError


class ApplySortOperation(SortOperation):
    """
    Replace the array's contents with a computed final order.

    Every sorting algorithm simulator works on its own local copy of
    the values while building the step-by-step animation (same
    pattern as every other topic's simulators), then this operation
    commits that final order to the real array once the student has
    finished stepping through it.
    """

    def __init__(self, sorted_values: list[int]) -> None:
        self.sorted_values = list(sorted_values)

    def commit(self, array: SortArray) -> None:
        array.set_values(self.sorted_values)


class RandomizeOperation(SortOperation):
    """Replace the array with a fresh random set of values."""

    def __init__(self, size: int, minimum: int, maximum: int) -> None:
        self.size = size
        self.minimum = minimum
        self.maximum = maximum

    def commit(self, array: SortArray) -> None:
        array.randomize(self.size, self.minimum, self.maximum)


class ClearOperation(SortOperation):
    """Remove every value from the array."""

    def commit(self, array: SortArray) -> None:
        array.clear()