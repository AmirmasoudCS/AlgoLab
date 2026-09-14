import pygame

from algolab.topics.asymptotic.model import AsymptoticModel
from algolab.topics.asymptotic.visualizer import AsymptoticVisualizer
from algolab.ui.components.checkbox import Checkbox
from algolab.ui.components.numeric_input import NumericInput
from algolab.ui.components.radio_button import RadioButton
from algolab.ui.components.surface import draw_panel
from algolab.ui.screens.screen import Screen
from algolab.ui.theme import Color, Font
from algolab.visualization.graph.layout import GraphLayout
from algolab.visualization.graph.scaling import (
    LinearScaling,
    LogarithmicScaling,
    ScalingStrategy,
)


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

        self.control_font = Font.H1()
        self.section_font = Font.H2()

        self.scale_buttons = self._create_scale_buttons()
        self.maximum_input = NumericInput(
            pygame.Rect(
                135,
                240,
                75,
                30,
            ),
            self.model.maximum_input,
        )
        self.checkboxes = self._create_checkboxes()

    def _create_scale_buttons(self) -> list[RadioButton]:
        """Create radio buttons for Y-axis scaling."""

        return [
            RadioButton(
                pygame.Rect(
                    25,
                    155,
                    20,
                    20,
                ),
                "Linear",
                selected=isinstance(
                    self.y_scaling,
                    LinearScaling,
                ),
            ),
            RadioButton(
                pygame.Rect(
                    25,
                    190,
                    20,
                    20,
                ),
                "Logarithmic",
                selected=isinstance(
                    self.y_scaling,
                    LogarithmicScaling,
                ),
            ),
        ]

    def _create_checkboxes(self) -> list[Checkbox]:
        """Create checkboxes for each complexity function."""

        checkboxes = []

        x = 25
        y = 300
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

    def _draw_text(
        self,
        text: str,
        position: tuple[int, int],
        font: pygame.font.Font,
        color: tuple[int, int, int] = Color.TEXT_PRIMARY,
    ) -> None:
        """Draw text in the TA control panel."""

        rendered_text = font.render(
            text,
            True,
            color,
        )

        self.surface.blit(
            rendered_text,
            position,
        )

    def handle_event(self, event: pygame.event.Event) -> None:
        for index, radio_button in enumerate(self.scale_buttons):
            previous_state = radio_button.selected

            radio_button.handle_event(event)

            if radio_button.selected and not previous_state:
                for other_button in self.scale_buttons:
                    other_button.selected = False

                radio_button.selected = True

                if index == 0:
                    self.set_y_scaling(LinearScaling())

                elif index == 1:
                    self.set_y_scaling(LogarithmicScaling())

        new_maximum = self.maximum_input.handle_event(event)

        if new_maximum is not None:
            try:
                self.model.set_input_range(
                    self.model.minimum_input,
                    new_maximum,
                )

            except ValueError:
                self.maximum_input.set_value(
                    self.model.maximum_input,
                )

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
        self.surface.fill(Color.BG)

        panel_rect = pygame.Rect(10, 70, 250, 500)
        draw_panel(self.surface, panel_rect, elevated=True)

        self._draw_text(
            "TA Controls",
            (25, 80),
            self.control_font,
        )

        self._draw_text(
            "Scale",
            (25, 115),
            self.section_font,
            color=Color.TEXT_SECONDARY,
        )

        for radio_button in self.scale_buttons:
            radio_button.render(self.surface)

        self._draw_text(
            "Input Size (N)",
            (25, 220),
            self.section_font,
            color=Color.TEXT_SECONDARY,
        )

        self._draw_text(
            "Maximum:",
            (25, 245),
            self.section_font,
            color=Color.TEXT_SECONDARY,
        )

        self.maximum_input.render(self.surface)

        self._draw_text(
            "Complexity Functions",
            (25, 280),
            self.section_font,
            color=Color.TEXT_SECONDARY,
        )

        for checkbox in self.checkboxes:
            checkbox.render(self.surface)

        self.visualizer.render()

    def set_y_scaling(self, scaling: ScalingStrategy) -> None:
        self.y_scaling = scaling
        self.visualizer.set_y_scaling(scaling)