from abc import ABC, abstractmethod
import math


class ScalingStrategy(ABC):
    """Defines how mathematical values are transformed for visualization."""

    @abstractmethod
    def scale(self, value: float) -> float:
        """Transform a mathematical value for visualization."""
        pass


class LinearScaling(ScalingStrategy):
    """Preserves the original mathematical value."""

    def scale(self, value: float) -> float:
        return value


class LogarithmicScaling(ScalingStrategy):
    """Applies a base-10 logarithmic transformation."""

    def scale(self, value: float) -> float:
        if value <= 0:
            raise ValueError("Logarithmic scaling requires a positive value.")

        return math.log10(value)


class NormalizedScaling(ScalingStrategy):
    """Normalizes values relative to a known maximum."""

    def __init__(self, maximum: float) -> None:
        if maximum <= 0:
            raise ValueError("Maximum must be greater than zero.")

        self._maximum = maximum

    def scale(self, value: float) -> float:
        return value / self._maximum