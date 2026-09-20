from __future__ import annotations

import random


class SortArray:
    """Represents an array a student builds and sorts."""

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