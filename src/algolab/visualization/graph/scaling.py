from abc import ABC, abstractmethod
import math


class ScalingStrategy(ABC):
    """Defines how mathematical values are transformed for visualization."""

    @abstractmethod
    def scale(self, value: float) -> float:
        """Transform a mathematical value for visualization."""
        pass

    @abstractmethod
    def get_ticks(
        self,
        minimum: float,
        maximum: float,
        count: int = 10,
    ) -> list[float]:
        """Return suitable tick values for the scale."""
        pass


class LinearScaling(ScalingStrategy):
    """Preserves the original mathematical value."""

    def scale(self, value: float) -> float:
        return value

    def get_ticks(
        self,
        minimum: float,
        maximum: float,
        count: int = 10,
    ) -> list[float]:
        if maximum <= minimum:
            raise ValueError("Maximum must be greater than minimum.")

        if maximum - minimum <= count:
            return list(range(int(minimum), int(maximum) + 1))

        step = (maximum - minimum) / count

        return [
            minimum + index * step
            for index in range(count + 1)
        ]


class LogarithmicScaling(ScalingStrategy):
    """Applies a base-10 logarithmic transformation."""

    def scale(self, value: float) -> float:
        if value <= 0:
            raise ValueError("Logarithmic scaling requires a positive value.")

        return math.log10(value)

    def get_ticks(
        self,
        minimum: float,
        maximum: float,
        count: int = 10,
    ) -> list[float]:
        if minimum <= 0 or maximum <= 0:
            raise ValueError(
                "Logarithmic ticks require positive values."
            )

        if maximum <= minimum:
            raise ValueError("Maximum must be greater than minimum.")

        minimum_power = math.floor(math.log10(minimum))
        maximum_power = math.ceil(math.log10(maximum))

        return [
            10**power
            for power in range(
                minimum_power,
                maximum_power + 1,
            )
        ]


class NormalizedScaling(ScalingStrategy):
    """Normalizes values relative to a known maximum."""

    def __init__(self, maximum: float) -> None:
        if maximum <= 0:
            raise ValueError("Maximum must be greater than zero.")

        self._maximum = maximum

    def scale(self, value: float) -> float:
        return value / self._maximum

    def get_ticks(
        self,
        minimum: float,
        maximum: float,
        count: int = 10,
    ) -> list[float]:
        if maximum <= minimum:
            raise ValueError("Maximum must be greater than minimum.")

        step = (maximum - minimum) / count

        return [
            minimum + index * step
            for index in range(count + 1)
        ]