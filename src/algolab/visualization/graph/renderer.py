import pygame

from algolab.visualization.graph.coordinate_system import (
    GraphCoordinateSystem,
)

from algolab.visualization.graph.scaling import LinearScaling

class GraphRenderer:
    """Renders a coordinate system onto a Pygame surface."""

    def __init__(
        self,
        surface: pygame.Surface,
        coordinate_system: GraphCoordinateSystem,
    ) -> None:
        self.surface = surface
        self.coordinate_system = coordinate_system

        if not pygame.font.get_init():
            pygame.font.init()

        self.font = pygame.font.Font(None, 20)

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

        x_ticks = LinearScaling().get_ticks(
            graph.x_min,
            graph.x_max,
        )

        y_ticks = graph.y_scaling.get_ticks(
            graph.y_min,
            graph.y_max,
        )

        for x_value in x_ticks:
            start = graph.to_screen(x_value, graph.y_min)
            end = graph.to_screen(x_value, graph.y_max)

            pygame.draw.line(
                self.surface,
                (220, 220, 220),
                start,
                end,
            )

        for y_value in y_ticks:
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

        if graph.y_min <= 0 <= graph.y_max:
            x_axis_start = graph.to_screen(graph.x_min, 0)
            x_axis_end = graph.to_screen(graph.x_max, 0)

            pygame.draw.line(
                self.surface,
                (30, 30, 30),
                x_axis_start,
                x_axis_end,
                2,
            )

        if graph.x_min <= 0 <= graph.x_max:
            y_axis_start = graph.to_screen(0, graph.y_min)
            y_axis_end = graph.to_screen(0, graph.y_max)

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