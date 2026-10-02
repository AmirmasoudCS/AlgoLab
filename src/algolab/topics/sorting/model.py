from __future__ import annotations

import random

from algolab.core.serialization import checked_int_items


class SortArray:
    """Represents an array a student builds and sorts."""

    # Upper bounds accepted when loading a file. 60 matches the most
    # bars the screen lets a student build (see SortingScreen).
    MAX_LOADED_VALUES = 60
    MAX_LOADED_VALUE = 1_000_000_000

    def __init__(self, values: list[int] | None = None) -> None:
        self._values: list[int] = list(values) if values else []

    @property
    def values(self) -> list[int]:
        return list(self._values)

    @property
    def size(self) -> int:
        return len(self._values)

    @property
    def is_empty(self) -> bool:
        return not self._values

    @property
    def is_sorted(self) -> bool:
        return all(
            self._values[i] <= self._values[i + 1]
            for i in range(len(self._values) - 1)
        )

    def append(self, value: int) -> None:
        """Add one value, as when a student types values in one at a time."""
        self._values.append(value)

    def clear(self) -> None:
        self._values.clear()

    def randomize(
        self,
        size: int = 10,
        minimum: int = 1,
        maximum: int = 99,
    ) -> None:
        """Replace the array with a fresh set of random values."""

        if size < 1:
            raise ValueError("Size must be at least 1.")

        if minimum > maximum:
            raise ValueError("Minimum cannot be greater than maximum.")

        self._values = [random.randint(minimum, maximum) for _ in range(size)]

    def set_values(self, values: list[int]) -> None:
        self._values = list(values)

    def to_dict(self) -> dict:
        """Return a JSON-serializable snapshot (values in array order)."""
        return {"values": self.values}

    @classmethod
    def from_dict(cls, data: object) -> SortArray:
        """Build an array from a dict produced by to_dict().

        Raises:
            ValueError: If the data is malformed, has a negative or
                absurdly large value, or has more than MAX_LOADED_VALUES
                values.
        """
        values = checked_int_items(
            data, "Array", cls.MAX_LOADED_VALUES, key="values"
        )

        for position, value in enumerate(values):
            if not 0 <= value <= cls.MAX_LOADED_VALUE:
                raise ValueError(
                    f"Value {position} must be between 0 and "
                    f"{cls.MAX_LOADED_VALUE}."
                )

        return cls(values)