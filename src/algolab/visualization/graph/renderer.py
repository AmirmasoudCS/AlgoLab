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

        for x_value in range(
            int(graph.x_min),
            int(graph.x_max) + 1,
        ):
            start = graph.to_screen(x_value, graph.y_min)
            end = graph.to_screen(x_value, graph.y_max)

            pygame.draw.line(
                self.surface,
                (220, 220, 220),
                start,
                end,
            )

        for y_value in range(
            int(graph.y_min),
            int(graph.y_max) + 1,
        ):
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