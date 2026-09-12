from __future__ import annotations


class Stack:
    """A simple LIFO stack implementation."""

    def __init__(self) -> None:
        self._items: list[object] = []

    @property
    def size(self) -> int:
        """Return the number of items in the stack."""
        return len(self._items)

    @property
    def is_empty(self) -> bool:
        """Return True when the stack contains no items."""
        return not self._items

    @property
    def top(self) -> object | None:
        """Return the top item without removing it."""
        if self.is_empty:
            return None

        return self._items[-1]

    def push(self, value: object) -> None:
        """Add a value to the top of the stack."""
        self._items.append(value)

    def pop(self) -> object:
        """Remove and return the top value.

        Raises:
            IndexError: If the stack is empty.
        """
        if self.is_empty:
            raise IndexError("Cannot pop from an empty stack.")

        return self._items.pop()

    def peek(self) -> object:
        """Return the top value without removing it.

        Raises:
            IndexError: If the stack is empty.
        """
        if self.is_empty:
            raise IndexError("Cannot peek at an empty stack.")

        return self._items[-1]

    def clear(self) -> None:
        """Remove all items from the stack."""
        self._items.clear()

    def to_list(self) -> list[object]:
        """Return the stack contents from bottom to top."""
        return self._items.copy()