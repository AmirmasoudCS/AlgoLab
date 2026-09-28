from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class PriorityBacking(Enum):
    """Which internal representation maintains the priority ordering."""

    HEAP = "heap"
    SORTED_LIST = "sorted_list"


@dataclass
class PriorityEntry:
    """A single stored value and its priority."""

    value: object
    priority: float


class PriorityQueue:
    """
    A priority queue supporting two interchangeable backings:

    - HEAP: array-backed binary heap (bubble up on insert, bubble down
      on extract). O(log n) insert, O(log n) extract, O(1) peek.
    - SORTED_LIST: a plain list kept sorted by priority at all times,
      so insert finds and shifts into the correct position. O(n)
      insert, O(1) extract, O(1) peek.

    Both backings guarantee the highest-priority entry sits at index 0
    at all times, which is what makes peek() identical for either one.

    Switching backing clears the queue rather than trying to convert
    between representations in place -- the same reasoning HashTable
    uses when switching collision strategy: a heap array and a sorted
    list aren't the same structure wearing different clothes.
    """

    def __init__(
        self,
        backing: PriorityBacking = PriorityBacking.HEAP,
        min_priority_first: bool = True,
    ) -> None:
        self._backing = backing
        # True: lower priority number is served first (a common convention
        # for task schedulers, where priority 1 often means "most urgent").
        # False: higher priority number is served first (closer to Heap's
        # own Max-heap framing elsewhere in this app).
        self._min_priority_first = min_priority_first

        self._entries: list[PriorityEntry] = []

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def backing(self) -> PriorityBacking:
        return self._backing

    @property
    def min_priority_first(self) -> bool:
        return self._min_priority_first

    @property
    def size(self) -> int:
        return len(self._entries)

    @property
    def is_empty(self) -> bool:
        return not self._entries

    @property
    def entries(self) -> list[PriorityEntry]:
        """
        Return the entries in their current internal order: heap-array
        order for HEAP, fully sorted order for SORTED_LIST. Index 0 is
        always the highest-priority entry for either backing.
        """

        return list(self._entries)

    # ------------------------------------------------------------------
    # Configuration
    # ------------------------------------------------------------------

    def set_backing(self, backing: PriorityBacking) -> None:
        if backing == self._backing:
            return

        self._backing = backing
        self.clear()

    def set_priority_order(self, min_priority_first: bool) -> None:
        if min_priority_first == self._min_priority_first:
            return

        self._min_priority_first = min_priority_first
        self.clear()

    def clear(self) -> None:
        self._entries.clear()

    # ------------------------------------------------------------------
    # Comparison
    # ------------------------------------------------------------------

    def _has_priority(self, first: PriorityEntry, second: PriorityEntry) -> bool:
        """Return True when `first` should be served before `second`."""

        if self._min_priority_first:
            return first.priority < second.priority

        return first.priority > second.priority

    # ------------------------------------------------------------------
    # Operations
    # ------------------------------------------------------------------

    def insert(self, value: object, priority: float) -> int:
        """Insert a value with a priority. Returns the index it landed at."""

        entry = PriorityEntry(value=value, priority=priority)

        if self._backing is PriorityBacking.HEAP:
            self._entries.append(entry)
            self._bubble_up(len(self._entries) - 1)
            # Identity lookup (is, not ==): PriorityEntry uses ordinary
            # dataclass equality, so if another entry elsewhere in the
            # heap happens to share the same value and priority,
            # `.index(entry)` would silently return that other one's
            # position instead of the one we just inserted.
            return next(
                index
                for index, existing in enumerate(self._entries)
                if existing is entry
            )

        # SORTED_LIST: find the first position whose entry does not
        # outrank the new one, and insert there. Everything after that
        # position shifts right by one, same as list.insert() always
        # does; entries before it keep their positions unchanged.
        index = 0
        while index < len(self._entries) and self._has_priority(
            self._entries[index], entry
        ):
            index += 1

        self._entries.insert(index, entry)
        return index

    def peek(self) -> PriorityEntry:
        """Return the highest-priority entry without removing it.

        Raises:
            IndexError: If the queue is empty.
        """

        if self.is_empty:
            raise IndexError("Cannot peek at an empty priority queue.")

        return self._entries[0]

    def extract(self) -> PriorityEntry:
        """Remove and return the highest-priority entry.

        Raises:
            IndexError: If the queue is empty.
        """

        if self.is_empty:
            raise IndexError("Cannot extract from an empty priority queue.")

        if self._backing is PriorityBacking.HEAP:
            top = self._entries[0]

            last = self._entries.pop()

            if self._entries:
                self._entries[0] = last
                self._bubble_down(0)

            return top

        # SORTED_LIST: the highest-priority entry is always at index 0.
        return self._entries.pop(0)

    # ------------------------------------------------------------------
    # Heap helpers (used only when backing is HEAP)
    # ------------------------------------------------------------------

    def _bubble_up(self, index: int) -> None:
        while index > 0:
            parent_index = self._parent_index(index)

            if not self._has_priority(
                self._entries[index], self._entries[parent_index]
            ):
                break

            self._entries[index], self._entries[parent_index] = (
                self._entries[parent_index],
                self._entries[index],
            )

            index = parent_index

    def _bubble_down(self, index: int) -> None:
        size = len(self._entries)

        while True:
            left_index = self._left_index(index)
            right_index = self._right_index(index)

            priority_index = index

            if left_index < size and self._has_priority(
                self._entries[left_index], self._entries[priority_index]
            ):
                priority_index = left_index

            if right_index < size and self._has_priority(
                self._entries[right_index], self._entries[priority_index]
            ):
                priority_index = right_index

            if priority_index == index:
                break

            self._entries[index], self._entries[priority_index] = (
                self._entries[priority_index],
                self._entries[index],
            )

            index = priority_index

    @staticmethod
    def _parent_index(index: int) -> int:
        return (index - 1) // 2

    @staticmethod
    def _left_index(index: int) -> int:
        return 2 * index + 1

    @staticmethod
    def _right_index(index: int) -> int:
        return 2 * index + 2