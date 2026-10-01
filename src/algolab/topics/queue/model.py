from __future__ import annotations

from algolab.core.serialization import checked_scalar_items


class Queue:
    """A simple FIFO queue implementation."""

    # Upper bound on items accepted when loading a file (see
    # Stack.MAX_LOADED_ITEMS for the reasoning).
    MAX_LOADED_ITEMS = 1000

    def __init__(self) -> None:
        self._items: list[object] = []

    @property
    def size(self) -> int:
        """Return the number of items in the queue."""
        return len(self._items)

    @property
    def is_empty(self) -> bool:
        """Return True when the queue is empty."""
        return not self._items

    @property
    def front(self) -> object | None:
        """Return the front item without removing it."""
        if self.is_empty:
            return None

        return self._items[0]

    @property
    def rear(self) -> object | None:
        """Return the rear item without removing it."""
        if self.is_empty:
            return None

        return self._items[-1]

    def enqueue(self, value: object) -> None:
        """Add a value to the rear of the queue."""
        self._items.append(value)

    def dequeue(self) -> object:
        """Remove and return the front value.

        Raises:
            IndexError: If the queue is empty.
        """
        if self.is_empty:
            raise IndexError("Cannot dequeue from an empty queue.")

        return self._items.pop(0)

    def peek(self) -> object:
        """Return the front value without removing it.

        Raises:
            IndexError: If the queue is empty.
        """
        if self.is_empty:
            raise IndexError("Cannot peek at an empty queue.")

        return self._items[0]

    def clear(self) -> None:
        """Remove all items from the queue."""
        self._items.clear()

    def to_list(self) -> list[object]:
        """Return the queue contents from front to rear."""
        return self._items.copy()

    def to_dict(self) -> dict:
        """Return a JSON-serializable snapshot (items front to rear)."""
        return {"items": self.to_list()}

    @classmethod
    def from_dict(cls, data: object) -> Queue:
        """Build a queue from a dict produced by to_dict().

        Raises:
            ValueError: If the data is malformed.
        """
        items = checked_scalar_items(data, "Queue", cls.MAX_LOADED_ITEMS)

        queue = cls()
        queue._items = items

        return queue

    def replace_with(self, other: Queue) -> None:
        """Take over another queue's contents (it should not be reused)."""
        self._items = other._items