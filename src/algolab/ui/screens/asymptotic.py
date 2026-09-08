import pygame

from algolab.topics.asymptotic.model import AsymptoticModel
from algolab.topics.asymptotic.visualizer import AsymptoticVisualizer
from algolab.ui.screens.screen import Screen
from algolab.visualization.graph.layout import GraphLayout


class AsymptoticScreen(Screen):
    """Screen for visualizing asymptotic complexity."""

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

    def __init__(self, surface: pygame.Surface) -> None:
        super().__init__(surface)

        self.model = AsymptoticModel()

        self.layout = GraphLayout(
            x=110,
            y=80,
            width=1090,
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