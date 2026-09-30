from __future__ import annotations

import math


# Values a saved stack may contain: anything plain JSON can represent.
_JSON_SCALARS = (int, float, str, bool, type(None))


class Stack:
    """A simple LIFO stack implementation."""

    # Upper bound on items accepted when loading a file. The screen has
    # no limit on manual pushes, but a hand-edited file with millions of
    # items would make every frame draw millions of cards.
    MAX_LOADED_ITEMS = 1000

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

    def to_dict(self) -> dict:
        """Return a JSON-serializable snapshot (items bottom to top)."""
        return {"items": self.to_list()}

    @classmethod
    def from_dict(cls, data: object) -> Stack:
        """Build a stack from a dict produced by to_dict().

        Everything is validated before a Stack is returned, so callers
        can apply the result to a live screen knowing it cannot fail
        halfway through.

        Raises:
            ValueError: If the data is malformed.
        """
        if not isinstance(data, dict) or "items" not in data:
            raise ValueError("Stack data must contain an 'items' list.")

        items = data["items"]

        if not isinstance(items, list):
            raise ValueError("Stack 'items' must be a list.")

        if len(items) > cls.MAX_LOADED_ITEMS:
            raise ValueError(
                f"A stack can hold at most {cls.MAX_LOADED_ITEMS} items "
                f"when loaded from a file (this one has {len(items)})."
            )

        for position, item in enumerate(items):
            if not isinstance(item, _JSON_SCALARS):
                raise ValueError(
                    f"Item {position} is not a number, text, or null."
                )

            if isinstance(item, float) and not math.isfinite(item):
                raise ValueError(f"Item {position} is not a finite number.")

        stack = cls()
        stack._items = list(items)

        return stack