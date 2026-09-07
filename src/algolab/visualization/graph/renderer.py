import pygame

from algolab.visualization.graph.coordinate_system import (
    GraphCoordinateSystem,
)


class GraphRenderer:
    """Renders a coordinate system onto a Pygame surface."""

    def __init__(
        self,
        surface: pygame.Surface,
        coordinate_system: GraphCoordinateSystem,
    ) -> None:
        self.surface = surface
        self.coordinate_system = coordinate_system

    def render(self) -> None:
        self._draw_background()
        self._draw_grid()
        self._draw_axes()

    def _draw_background(self) -> None:
        pygame.draw.rect(
            self.surface,
            (245, 245, 245),
            pygame.Rect(
                self.coordinate_system.x,
                self.coordinate_system.y,
                self.coordinate_system.width,
                self.coordinate_system.height,
            ),
        )

    def _draw_grid(self) -> None:
        graph = self.coordinate_system

        grid_lines = 10

        x_step = (graph.x_max - graph.x_min) / grid_lines
        y_step = (graph.y_max - graph.y_min) / grid_lines

        for index in range(grid_lines + 1):
            x_value = graph.x_min + index * x_step

            start = graph.to_screen(x_value, graph.y_min)
            end = graph.to_screen(x_value, graph.y_max)

            pygame.draw.line(
                self.surface,
                (220, 220, 220),
                start,
                end,
            )

        for index in range(grid_lines + 1):
            y_value = graph.y_min + index * y_step

            start = graph.to_screen(graph.x_min, y_value)
            end = graph.to_screen(graph.x_max, y_value)

            pygame.draw.line(
                self.surface,
                (220, 220, 220),
                start,
                end,
            )

    def _draw_axes(self) -> None:
        graph = self.coordinate_system

        x_axis_start = graph.to_screen(graph.x_min, 0)
        x_axis_end = graph.to_screen(graph.x_max, 0)

        y_axis_start = graph.to_screen(0, graph.y_min)
        y_axis_end = graph.to_screen(0, graph.y_max)

        pygame.draw.line(
            self.surface,
            (30, 30, 30),
            x_axis_start,
            x_axis_end,
            2,
        )

        pygame.draw.line(
            self.surface,
            (30, 30, 30),
            y_axis_start,
            y_axis_end,
            2,
        )

    def draw_curve(
        self,
        points: list[tuple[float, float]],
        width: int = 2,
    ) -> None:
        """Draw a curve through mathematical points."""

        screen_points = [
            self.coordinate_system.to_screen(x, y)
            for x, y in points
        ]

        if len(screen_points) < 2:
            return

        pygame.draw.lines(
            self.surface,
            (50, 50, 50),
            False,
            screen_points,
            width,
        )