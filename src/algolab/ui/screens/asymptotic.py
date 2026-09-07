import pygame

from algolab.topics.asymptotic.model import AsymptoticModel
from algolab.topics.asymptotic.visualizer import AsymptoticVisualizer
from algolab.ui.screens.screen import Screen
from algolab.visualization.graph.layout import GraphLayout


class AsymptoticScreen(Screen):
    """Screen for visualizing asymptotic complexity."""

    def __init__(self, surface: pygame.Surface) -> None:
        super().__init__(surface)

        self.model = AsymptoticModel()

        self.layout = GraphLayout(
            x=80,
            y=80,
            width=1120,
            height=580,
        )

        self.visualizer = AsymptoticVisualizer(
            surface,
            self.model,
            self.layout,
        )

    def handle_event(self, event: pygame.event.Event) -> None:
        pass

    def update(self, dt: float) -> None:
        pass

    def render(self) -> None:
        self.surface.fill((30, 30, 30))
        self.visualizer.render()