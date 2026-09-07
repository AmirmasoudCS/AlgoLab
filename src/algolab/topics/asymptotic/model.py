from algolab.topics.asymptotic.complexity import (
    COMPLEXITIES,
    ComplexityFunction,
)


class AsymptoticModel:
    """Represents the state of the asymptotic notation lesson."""

    def __init__(self) -> None:
        self._complexities = COMPLEXITIES
        self._visible_complexities = list(COMPLEXITIES)
        self._selected_complexity = COMPLEXITIES[0]

        self._minimum_input = 1
        self._maximum_input = 10

    @property
    def complexities(self) -> tuple[ComplexityFunction, ...]:
        return self._complexities

    @property
    def visible_complexities(self) -> list[ComplexityFunction]:
        return self._visible_complexities

    @property
    def selected_complexity(self) -> ComplexityFunction:
        return self._selected_complexity

    @property
    def minimum_input(self) -> int:
        return self._minimum_input

    @property
    def maximum_input(self) -> int:
        return self._maximum_input

    def select_complexity(self, complexity: ComplexityFunction) -> None:
        if complexity not in self._complexities:
            raise ValueError("Unknown complexity function.")

        self._selected_complexity = complexity

    def set_visible(
        self,
        complexity: ComplexityFunction,
        visible: bool,
    ) -> None:
        if complexity not in self._complexities:
            raise ValueError("Unknown complexity function.")

        if visible and complexity not in self._visible_complexities:
            self._visible_complexities.append(complexity)

        elif not visible and complexity in self._visible_complexities:
            self._visible_complexities.remove(complexity)

    def set_input_range(
        self,
        minimum: int,
        maximum: int,
    ) -> None:
        if minimum < 1:
            raise ValueError("Minimum input must be at least 1.")

        if maximum <= minimum:
            raise ValueError("Maximum input must be greater than minimum input.")

        self._minimum_input = minimum
        self._maximum_input = maximum