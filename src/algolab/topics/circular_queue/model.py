from __future__ import annotations


class CircularQueue:
    """
    A fixed-capacity queue backed by a circular (wraparound) array.

    Tracked via a front index plus an explicit size counter, rather
    than the more common "front == rear means empty OR full" trick,
    which needs an extra sentinel or a wasted slot to disambiguate.
    An explicit size counter avoids that ambiguity outright and keeps
    every capacity slot usable.
    """

    def __init__(self, capacity: int = 8) -> None:
        if capacity < 1:
            raise ValueError("Capacity must be at least 1.")

        self._capacity = capacity
        self._slots: list[object | None] = [None] * capacity
        self._front = 0
        self._size = 0

    @property
    def capacity(self) -> int:
        return self._capacity

    @property
    def size(self) -> int:
        return self._size

    @property
    def is_empty(self) -> bool:
        return self._size == 0

    @property
    def is_full(self) -> bool:
        return self._size == self._capacity

    @property
    def front_index(self) -> int | None:
        return self._front if not self.is_empty else None

    @property
    def rear_index(self) -> int | None:
        if self.is_empty:
            return None

        return (self._front + self._size - 1) % self._capacity

    def enqueue(self, value: object) -> int:
        """Add a value at the rear. Returns the slot index it landed in.

        Raises:
            IndexError: If the queue is already at capacity.
        """

        if self.is_full:
            raise IndexError(
                f"Circular queue is full (capacity {self._capacity})."
            )

        insert_index = (self._front + self._size) % self._capacity

        self._slots[insert_index] = value
        self._size += 1

        return insert_index

    def dequeue(self) -> object:
        """Remove and return the front value, advancing FRONT (with wraparound).

        Raises:
            IndexError: If the queue is empty.
        """

        if self.is_empty:
            raise IndexError("Cannot dequeue from an empty circular queue.")

        value = self._slots[self._front]
        self._slots[self._front] = None

        self._front = (self._front + 1) % self._capacity
        self._size -= 1

        return value

    def peek(self) -> object:
        """Return the front value without removing it.

        Raises:
            IndexError: If the queue is empty.
        """

        if self.is_empty:
            raise IndexError("Cannot peek at an empty circular queue.")

        return self._slots[self._front]

    def clear(self) -> None:
        """Remove all items, resetting FRONT to slot 0."""

        self._slots = [None] * self._capacity
        self._front = 0
        self._size = 0

    def set_capacity(self, capacity: int) -> None:
        """Change capacity, clearing the queue (existing slot positions
        and wraparound state have no sensible meaning at a different
        capacity, the same reasoning HashTable uses when its capacity
        changes)."""

        if capacity < 1:
            raise ValueError("Capacity must be at least 1.")

        self._capacity = capacity
        self.clear()

    def to_list(self) -> list[object]:
        """Return the logical contents, front to rear."""

        return [
            self._slots[(self._front + offset) % self._capacity]
            for offset in range(self._size)
        ]

    def slots_snapshot(self) -> tuple[object | None, ...]:
        """
        Return the raw physical array (fixed length == capacity, None
        for empty slots), for rendering the actual ring of slots
        rather than just the logical front-to-rear contents.
        """

        return tuple(self._slots)