import pygame

from algolab.topics.asymptotic.model import AsymptoticModel
from algolab.topics.asymptotic.visualizer import AsymptoticVisualizer
from algolab.ui.screens.screen import Screen
from algolab.visualization.graph.layout import GraphLayout
from algolab.visualization.graph.scaling import LinearScaling


class AsymptoticScreen(Screen):
    """Screen for visualizing asymptotic complexity."""

    def __init__(self, surface: pygame.Surface) -> None:
        super().__init__(surface)

        self.model = AsymptoticModel()

        self.layout = GraphLayout(
            x=110,
            y=100,
            width=1090,
            height=400,
        )

        self.y_scaling = LinearScaling()

        self.visualizer = AsymptoticVisualizer(
            surface,
            self.model,
            self.layout,
            self.y_scaling,
        )

    def handle_event(self, event: pygame.event.Event) -> None:
        pass

    def update(self, dt: float) -> None:
        pass

    def render(self) -> None:
        self.surface.fill((30, 30, 30))
        self.visualizer.render()