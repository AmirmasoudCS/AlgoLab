from __future__ import annotations

from enum import Enum
from typing import Generic, TypeVar

from algolab.core.serialization import check_dict, checked_int_items


T = TypeVar("T")


class HeapType(Enum):
    """The ordering rule used by a heap."""

    MIN = "min"
    MAX = "max"


class Heap(Generic[T]):
    """An array-based binary heap implementation."""

    # Upper bound on values accepted when loading a file.
    MAX_LOADED_ITEMS = 1000

    def __init__(
        self,
        heap_type: HeapType = HeapType.MIN,
    ) -> None:
        self._values: list[T] = []
        self._heap_type = heap_type

    @property
    def values(self) -> list[T]:
        """Return a copy of the heap values."""
        return self._values.copy()

    @property
    def size(self) -> int:
        """Return the number of elements in the heap."""
        return len(self._values)

    @property
    def is_empty(self) -> bool:
        """Return True when the heap contains no elements."""
        return not self._values

    @property
    def heap_type(self) -> HeapType:
        """Return the type of the heap."""
        return self._heap_type

    def insert(self, value: T) -> None:
        """Insert a value into the heap."""
        self._values.append(value)

        self._bubble_up(
            len(self._values) - 1,
        )

    def peek(self) -> T:
        """Return the root value without removing it.

        Raises:
            IndexError: If the heap is empty.
        """
        if self.is_empty:
            raise IndexError(
                "Cannot peek at an empty heap."
            )

        return self._values[0]

    def extract(self) -> T:
        """Remove and return the root value.

        Raises:
            IndexError: If the heap is empty.
        """
        if self.is_empty:
            raise IndexError(
                "Cannot extract from an empty heap."
            )

        if len(self._values) == 1:
            return self._values.pop()

        root = self._values[0]

        self._values[0] = self._values.pop()

        self._bubble_down(0)

        return root

    def build_heap(self, values: list[T]) -> None:
        """Build a heap from the given values."""
        self._values = values.copy()

        first_parent = (
            len(self._values) // 2
        ) - 1

        for index in range(
            first_parent,
            -1,
            -1,
        ):
            self._bubble_down(index)

    def clear(self) -> None:
        """Remove all elements from the heap."""
        self._values.clear()

    def to_dict(self) -> dict:
        """Return a JSON-serializable snapshot.

        The array is saved in its current order (not re-heapified), so
        a loaded heap shows exactly the layout that was saved.
        """

        return {
            "heap_type": self._heap_type.value,
            "values": self._values.copy(),
        }

    @classmethod
    def from_dict(cls, data: object) -> Heap:
        """Build a heap from a dict produced by to_dict().

        Besides types, the array must satisfy the heap property for the
        saved type (no child outranks its parent), because peek() and
        extract() rely on it.

        Raises:
            ValueError: If the data is malformed or not a valid heap.
        """

        check_dict(data, "Heap")

        try:
            heap_type = HeapType(data.get("heap_type"))
        except ValueError:
            raise ValueError("Heap type must be 'min' or 'max'.") from None

        values = checked_int_items(
            data, "Heap", cls.MAX_LOADED_ITEMS, key="values"
        )

        heap = cls(heap_type)
        heap._values = values

        for index in range(1, len(values)):
            parent_index = cls._parent_index(index)

            if heap._has_priority(values[index], values[parent_index]):
                raise ValueError(
                    f"The value at index {index} outranks its parent, so "
                    f"this is not a valid {heap_type.value}-heap."
                )

        return heap

    def _bubble_up(self, index: int) -> None:
        while index > 0:
            parent_index = self._parent_index(index)

            if not self._has_priority(
                self._values[index],
                self._values[parent_index],
            ):
                break

            self._values[index], self._values[parent_index] = (
                self._values[parent_index],
                self._values[index],
            )

            index = parent_index

    def _bubble_down(self, index: int) -> None:
        size = len(self._values)

        while True:
            left_index = self._left_index(index)
            right_index = self._right_index(index)

            priority_index = index

            if (
                left_index < size
                and self._has_priority(
                    self._values[left_index],
                    self._values[priority_index],
                )
            ):
                priority_index = left_index

            if (
                right_index < size
                and self._has_priority(
                    self._values[right_index],
                    self._values[priority_index],
                )
            ):
                priority_index = right_index

            if priority_index == index:
                break

            self._values[index], self._values[priority_index] = (
                self._values[priority_index],
                self._values[index],
            )

            index = priority_index

    def _has_priority(
        self,
        first: T,
        second: T,
    ) -> bool:
        if self._heap_type is HeapType.MIN:
            return first < second

        return first > second

    @staticmethod
    def _parent_index(index: int) -> int:
        return (index - 1) // 2

    @staticmethod
    def _left_index(index: int) -> int:
        return 2 * index + 1

    @staticmethod
    def _right_index(index: int) -> int:
        return 2 * index + 2