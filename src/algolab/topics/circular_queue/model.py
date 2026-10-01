from __future__ import annotations

from algolab.core.serialization import (
    check_dict,
    check_int,
    checked_list,
    check_scalar,
)


class CircularQueue:
    """
    A fixed-capacity queue backed by a circular (wraparound) array.

    Tracked via a front index plus an explicit size counter, rather
    than the more common "front == rear means empty OR full" trick,
    which needs an extra sentinel or a wasted slot to disambiguate.
    An explicit size counter avoids that ambiguity outright and keeps
    every capacity slot usable.
    """

    # Upper bound on capacity accepted when loading a file. (The screen
    # itself only offers 3 to 16 and enforces that on load.)
    MAX_LOADED_CAPACITY = 64

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

    def to_dict(self) -> dict:
        """Return a JSON-serializable snapshot of the physical ring.

        The exact slot layout is saved (not just the logical contents),
        because where FRONT sits after some wraparound is part of what
        this structure is teaching.
        """

        return {
            "capacity": self._capacity,
            "front": self._front,
            "size": self._size,
            "slots": list(self._slots),
        }

    @classmethod
    def from_dict(cls, data: object) -> CircularQueue:
        """Build a queue from a dict produced by to_dict().

        Beyond types and ranges, the occupied slots must be exactly the
        `size` slots starting at `front` (wrapping), and every other slot
        must be empty, so the ring is always internally consistent.

        Raises:
            ValueError: If the data is malformed or inconsistent.
        """

        check_dict(data, "Circular queue")

        capacity = check_int(data.get("capacity"), "Capacity")

        if not 1 <= capacity <= cls.MAX_LOADED_CAPACITY:
            raise ValueError(
                f"Capacity must be between 1 and {cls.MAX_LOADED_CAPACITY}."
            )

        front = check_int(data.get("front"), "Front")
        size = check_int(data.get("size"), "Size")

        if not 0 <= front < capacity:
            raise ValueError("Front must be a valid slot index.")

        if not 0 <= size <= capacity:
            raise ValueError("Size must be between 0 and the capacity.")

        slots = checked_list(
            data, "Circular queue", cls.MAX_LOADED_CAPACITY, key="slots"
        )

        if len(slots) != capacity:
            raise ValueError(
                f"Expected {capacity} slots but found {len(slots)}."
            )

        occupied = {(front + offset) % capacity for offset in range(size)}

        for index, value in enumerate(slots):
            check_scalar(value, f"Slot {index}")

            if index in occupied and value is None:
                raise ValueError(f"Slot {index} should hold a value.")

            if index not in occupied and value is not None:
                raise ValueError(f"Slot {index} should be empty.")

        queue = cls(capacity)
        queue._slots = list(slots)
        queue._front = front
        queue._size = size

        return queue

    def replace_with(self, other: CircularQueue) -> None:
        """Take over another queue's ring (it should not be reused)."""

        self._capacity = other._capacity
        self._slots = other._slots
        self._front = other._front
        self._size = other._size