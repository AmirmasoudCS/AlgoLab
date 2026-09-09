import pygame

from algolab.topics.asymptotic.model import AsymptoticModel
from algolab.topics.asymptotic.visualizer import AsymptoticVisualizer
from algolab.ui.components.checkbox import Checkbox
from algolab.ui.screens.screen import Screen
from algolab.visualization.graph.layout import GraphLayout
from algolab.visualization.graph.scaling import LinearScaling, ScalingStrategy


class AsymptoticScreen(Screen):
    """Screen for visualizing asymptotic complexity."""

    def __init__(self, surface: pygame.Surface) -> None:
        super().__init__(surface)

        self.model = AsymptoticModel()

        self.layout = GraphLayout(
            x=290,
            y=100,
            width=950,
            height=400,
        )

        self.y_scaling: ScalingStrategy = LinearScaling()

        self.visualizer = AsymptoticVisualizer(
            surface,
            self.model,
            self.layout,
            self.y_scaling,
        )

        self.checkboxes = self._create_checkboxes()

    def _create_checkboxes(self) -> list[Checkbox]:
        """Create checkboxes for each complexity function."""

        checkboxes = []

        x = 25
        y = 140
        spacing = 35

        for index, complexity in enumerate(self.model.complexities):
            checkbox = Checkbox(
                pygame.Rect(
                    x,
                    y + index * spacing,
                    20,
                    20,
                ),
                complexity.notation,
                checked=complexity in self.model.visible_complexities,
            )

            checkboxes.append(checkbox)

        return checkboxes

    def handle_event(self, event: pygame.event.Event) -> None:
        for checkbox, complexity in zip(
            self.checkboxes,
            self.model.complexities,
        ):
            previous_state = checkbox.checked

            checkbox.handle_event(event)

            if checkbox.checked != previous_state:
                self.model.set_visible(
                    complexity,
                    checkbox.checked,
                )

    def update(self, dt: float) -> None:
        pass

    def render(self) -> None:
        self.surface.fill((30, 30, 30))

        pygame.draw.rect(
            self.surface,
            (40, 40, 40),
            pygame.Rect(
                10,
                90,
                250,
                400,
            ),
            border_radius=8,
        )

        font = pygame.font.Font(None, 30)

        text = font.render(
            "TA Controls",
            True,
            (240, 240, 240),
        )

        self.surface.blit(
            text,
            (25, 100),
        )

        self.visualizer.render()

        for checkbox in self.checkboxes:
            checkbox.render(self.surface)

    def set_y_scaling(self, scaling: ScalingStrategy) -> None:
        self.y_scaling = scaling
        self.visualizer.set_y_scaling(scaling)