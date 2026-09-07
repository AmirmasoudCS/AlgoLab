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

    def render(self) -> None:
        """Render the asymptotic complexity graph."""

        curves = [
            self._curve_generator.generate(
                complexity.function,
                self.model.minimum_input,
                self.model.maximum_input,
            )
            for complexity in self.model.visible_complexities
        ]

        if not curves:
            return

        y_min, y_max = self._bounds_calculator.calculate_y_bounds(curves)

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

        for curve in curves:
            renderer.draw_curve(curve)