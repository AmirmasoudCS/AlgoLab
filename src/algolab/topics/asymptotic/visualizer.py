import pygame

from algolab.topics.asymptotic.model import AsymptoticModel
from algolab.visualization.graph.bounds import BoundsCalculator
from algolab.visualization.graph.coordinate_system import GraphCoordinateSystem
from algolab.visualization.graph.curve import CurveGenerator
from algolab.visualization.graph.layout import GraphLayout
from algolab.visualization.graph.renderer import GraphRenderer
from algolab.visualization.graph.scaling import LogarithmicScaling


class AsymptoticVisualizer:
    """Visualizes asymptotic complexity functions."""

    CURVE_COLORS = {
        "O(1)": (80, 80, 80),
        "O(log n)": (52, 152, 219),
        "O(n)": (46, 204, 113),
        "O(n log n)": (26, 188, 156),
        "O(n²)": (241, 196, 15),
        "O(n³)": (230, 126, 34),
        "O(2ⁿ)": (231, 76, 60),
        "O(nⁿ)": (155, 89, 182),
    }

    def __init__(
        self,
        surface: pygame.Surface,
        model: AsymptoticModel,
        layout: GraphLayout,
    ) -> None:
        self.surface = surface
        self.model = model
        self.layout = layout

        self._curve_generator = CurveGenerator()
        self._bounds_calculator = BoundsCalculator()
        self.title_font = pygame.font.Font(None, 32)
        self.label_font = pygame.font.Font(None, 22)    

    def _draw_title(self) -> None:
        title = self.title_font.render(
            "Asymptotic Complexity",
            True,
            (240, 240, 240),
        )

        title_rect = title.get_rect(
            center=(self.surface.get_width() // 2, 35)
        )

        self.surface.blit(title, title_rect)

        scale = self.label_font.render(
            "Y-axis: Logarithmic Scale",
            True,
            (200, 200, 200),
        )

        scale_rect = scale.get_rect(
            center=(self.surface.get_width() // 2, 65)
        )

        self.surface.blit(scale, scale_rect)

    def _draw_legend(self) -> None:
        legend_title = self.label_font.render(
            "Complexity Functions",
            True,
            (240, 240, 240),
        )

        title_rect = legend_title.get_rect(
            midtop=(self.surface.get_width() // 2, 585)
        )

        self.surface.blit(legend_title, title_rect)

        entries = list(self.model.visible_complexities)

        columns = 4
        column_width = 250
        row_height = 28

        start_x = 160
        start_y = 610

        for index, complexity in enumerate(entries):
            row = index // columns
            column = index % columns

            x = start_x + column * column_width
            y = start_y + row * row_height

            color = self.CURVE_COLORS[complexity.notation]

            pygame.draw.circle(
                self.surface,
                color,
                (x, y + 7),
                5,
            )

            label = self.label_font.render(
                complexity.notation,
                True,
                (230, 230, 230),
            )

            self.surface.blit(
                label,
                (x + 12, y - 3),
            )

    def _draw_axis_labels(self) -> None:
        x_label = self.label_font.render(
            "Input Size (n)",
            True,
            (230, 230, 230),
        )

        x_rect = x_label.get_rect(
            center=(
                self.layout.x + self.layout.width // 2,
                self.layout.y + self.layout.height + 35,
            )
        )

        self.surface.blit(x_label, x_rect)

        y_label = self.label_font.render(
            "Operations",
            True,
            (230, 230, 230),
        )

        y_label = pygame.transform.rotate(y_label, 90)

        y_rect = y_label.get_rect(
            center=(
                self.layout.x - 55,
                self.layout.y + self.layout.height // 2,
            )
        )

        self.surface.blit(y_label, y_rect)

    def render(self) -> None:
        """Render the asymptotic complexity graph."""

        curve_data = []

        for complexity in self.model.visible_complexities:
            curve = [
                point
                for point in self._curve_generator.generate(
                    complexity.function,
                    self.model.minimum_input,
                    self.model.maximum_input,
                )
                if point[1] > 0
            ]

            if curve:
                curve_data.append((complexity, curve))

        if not curve_data:
            return

        curves = [curve for _, curve in curve_data]

        y_min, y_max = self._bounds_calculator.calculate_y_bounds(curves)

        if y_min <= 0:
            y_min = 1

        graph = GraphCoordinateSystem(
            x=self.layout.x,
            y=self.layout.y,
            width=self.layout.width,
            height=self.layout.height,
            x_min=self.model.minimum_input,
            x_max=self.model.maximum_input,
            y_min=y_min,
            y_max=y_max,
            y_scaling=LogarithmicScaling(),
        )

        renderer = GraphRenderer(
            self.surface,
            graph,
        )

        renderer.render()

        for complexity, curve in curve_data:
            renderer.draw_curve(
                curve,
                color=self.CURVE_COLORS[complexity.notation],
            )

        self._draw_title()
        self._draw_axis_labels()
        self._draw_legend()