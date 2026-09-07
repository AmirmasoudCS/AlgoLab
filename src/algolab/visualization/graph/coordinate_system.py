from dataclasses import dataclass

from algolab.visualization.graph.scaling import (
    LinearScaling,
    ScalingStrategy,
)


@dataclass
class GraphCoordinateSystem:
    """Converts mathematical coordinates into screen coordinates."""

    x: int
    y: int
    width: int
    height: int

    x_min: float
    x_max: float
    y_min: float
    y_max: float

    y_scaling: ScalingStrategy = LinearScaling()

    def to_screen(self, x_value: float, y_value: float) -> tuple[int, int]:
        """Convert mathematical coordinates into screen coordinates."""

        scaled_y = self.y_scaling.scale(y_value)
        scaled_y_min = self.y_scaling.scale(self.y_min)
        scaled_y_max = self.y_scaling.scale(self.y_max)

        x_ratio = (x_value - self.x_min) / (self.x_max - self.x_min)
        y_ratio = (scaled_y - scaled_y_min) / (
            scaled_y_max - scaled_y_min
        )

        screen_x = self.x + x_ratio * self.width
        screen_y = self.y + (1 - y_ratio) * self.height

        return round(screen_x), round(screen_y)

    def contains(self, x_value: float, y_value: float) -> bool:
        """Return whether a mathematical point is inside the graph."""

        return (
            self.x_min <= x_value <= self.x_max
            and self.y_min <= y_value <= self.y_max
        )