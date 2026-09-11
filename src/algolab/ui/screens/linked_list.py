import pygame

from algolab.simulation.simulator import Simulator
from algolab.topics.linked_list.model import LinkedListModel
from algolab.topics.linked_list.simulation import (
    LinkedListSimulation,
    LinkedListSimulator,
)
from algolab.ui.components.button import Button
from algolab.ui.components.numeric_input import NumericInput
from algolab.ui.screens.screen import Screen


class LinkedListScreen(Screen):
    """Screen for visualizing linked-list operations."""

    def __init__(self, surface: pygame.Surface) -> None:
        super().__init__(surface)

        self.model = LinkedListModel()
        self.simulator = Simulator()
        self.linked_list_simulator = LinkedListSimulator(
            self.model
        )

        self.current_simulation: LinkedListSimulation | None = None
        self.operation_committed = False

        self.control_font = pygame.font.Font(None, 30)
        self.section_font = pygame.font.Font(None, 24)
        self.node_font = pygame.font.Font(None, 30)
        self.small_font = pygame.font.Font(None, 22)

        self.operation_buttons = self._create_operation_buttons()
        self.navigation_buttons = self._create_navigation_buttons()

        self.value_input = NumericInput(
            pygame.Rect(
                135,
                375,
                75,
                30,
            ),
            10,
        )

        self.index_input = NumericInput(
            pygame.Rect(
                135,
                415,
                75,
                30,
            ),
            0,
        )

        self.step_timer = 0.0
        self.step_interval = 0.8

    def _create_operation_buttons(self) -> list[Button]:
        """Create buttons for linked-list operations."""

        labels = [
            "Insert Beginning",
            "Insert End",
            "Insert At",
            "Delete At",
            "Search",
        ]

        buttons = []

        x = 25
        y = 145
        width = 220
        height = 38
        spacing = 45

        for index, label in enumerate(labels):
            buttons.append(
                Button(
                    pygame.Rect(
                        x,
                        y + index * spacing,
                        width,
                        height,
                    ),
                    label,
                )
            )

        return buttons

    def _create_navigation_buttons(self) -> list[Button]:
        """Create buttons for simulation navigation."""

        labels = [
            "|<",
            "<",
            ">",
            ">|",
            "Pause",
        ]

        buttons = []

        x = 25
        y = 485
        width = 40
        height = 35
        spacing = 45

        for index, label in enumerate(labels):
            buttons.append(
                Button(
                    pygame.Rect(
                        x + index * spacing,
                        y,
                        width,
                        height,
                    ),
                    label,
                )
            )

        return buttons

    def _draw_text(
        self,
        text: str,
        position: tuple[int, int],
        font: pygame.font.Font,
    ) -> None:
        """Draw text in the TA control panel."""

        rendered_text = font.render(
            text,
            True,
            (240, 240, 240),
        )

        self.surface.blit(
            rendered_text,
            position,
        )

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle user interaction."""

        self.value_input.handle_event(event)
        self.index_input.handle_event(event)

        for index, button in enumerate(self.operation_buttons):
            if button.handle_event(event):
                self._select_operation(index)

        for index, button in enumerate(self.navigation_buttons):
            if button.handle_event(event):
                self._handle_navigation(index)

    def _select_operation(self, index: int) -> None:
        """Create and start the selected linked-list simulation."""

        if self.current_simulation is not None:
            return

        value = self.value_input.value
        list_index = self.index_input.value

        try:
            if index == 0:
                simulation = self.linked_list_simulator.insert_at_beginning(
                    value
                )

            elif index == 1:
                simulation = self.linked_list_simulator.insert_at_end(
                    value
                )

            elif index == 2:
                simulation = self.linked_list_simulator.insert_at(
                    list_index,
                    value,
                )

            elif index == 3:
                simulation = self.linked_list_simulator.delete_at(
                    list_index
                )

            elif index == 4:
                simulation = self.linked_list_simulator.search(
                    value
                )

            else:
                return

        except IndexError:
            return

        self.current_simulation = simulation
        self.operation_committed = False

        self.simulator.load_states(
            list(simulation.states)
        )

        self.step_timer = 0.0

    def _handle_navigation(self, index: int) -> None:
        """Handle simulation navigation controls."""

        if self.current_simulation is None:
            return

        if index == 0:
            self.simulator.history.previous_to_start()

        elif index == 1:
            self.simulator.previous()

        elif index == 2:
            self.simulator.next()

        elif index == 3:
            while self.simulator.can_go_forward:
                self.simulator.next()

        elif index == 4:
            if self.simulator.running:
                self.simulator.pause()

            else:
                self.simulator.resume()

        self._commit_if_finished()

    def _commit_if_finished(self) -> None:
        """Commit the operation when its final state is reached."""

        if self.operation_committed:
            return

        if not self.simulator.is_at_end:
            return

        if self.current_simulation is None:
            return

        self.current_simulation.commit(self.model)
        self.operation_committed = True

    def update(self, dt: float) -> None:
        """Advance the simulation automatically while running."""

        if self.current_simulation is None:
            return

        if not self.simulator.running:
            return

        if self.simulator.is_at_end:
            self.simulator.pause()
            self._commit_if_finished()
            return

        self.step_timer += dt

        if self.step_timer >= self.step_interval:
            self.step_timer = 0.0
            self.simulator.next()

            self._commit_if_finished()

    def render(self) -> None:
        """Render the linked-list screen."""

        self.surface.fill((30, 30, 30))

        self._render_control_panel()
        self._render_linked_list()

    def _render_control_panel(self) -> None:
        """Render the TA control panel."""

        pygame.draw.rect(
            self.surface,
            (40, 40, 40),
            pygame.Rect(
                10,
                70,
                250,
                500,
            ),
            border_radius=8,
        )

        self._draw_text(
            "TA Controls",
            (25, 80),
            self.control_font,
        )

        self._draw_text(
            "Operations",
            (25, 115),
            self.section_font,
        )

        for button in self.operation_buttons:
            button.render(self.surface)

        self._draw_text(
            "Value:",
            (25, 380),
            self.section_font,
        )

        self.value_input.render(self.surface)

        self._draw_text(
            "Index:",
            (25, 420),
            self.section_font,
        )

        self.index_input.render(self.surface)

        self._draw_text(
            "Simulation",
            (25, 465),
            self.section_font,
        )

        for button in self.navigation_buttons:
            button.render(self.surface)

        if self.current_simulation is not None:
            state = self.simulator.state

            if state is not None:
                self._draw_text(
                    f"Step: {state.step + 1}/"
                    f"{len(self.current_simulation.states)}",
                    (25, 535),
                    self.small_font,
                )

    def _render_linked_list(self) -> None:
        """Render the linked list visualization."""

        x = 320
        y = 300

        self._draw_text(
            "HEAD",
            (x, 180),
            self.control_font,
        )

        pygame.draw.line(
            self.surface,
            (180, 180, 180),
            (x + 25, 215),
            (x + 25, y),
            3,
        )

        state = self.simulator.state

        if state is None:
            values = tuple(self.model.to_list())
            current_index = None
            created_index = None
            deleted_index = None

        else:
            simulation_state = state.data

            values = simulation_state.values
            current_index = simulation_state.current_index
            created_index = simulation_state.created_index
            deleted_index = simulation_state.deleted_index

        if not values:
            self._draw_text(
                "NULL",
                (x, y),
                self.node_font,
            )
            return

        node_width = 100
        node_height = 60
        spacing = 70

        for index, value in enumerate(values):
            node_x = x + index * (node_width + spacing)

            if index == current_index:
                background = (70, 100, 160)

            elif index == created_index:
                background = (70, 140, 90)

            elif index == deleted_index:
                background = (150, 70, 70)

            else:
                background = (55, 55, 55)

            rect = pygame.Rect(
                node_x,
                y,
                node_width,
                node_height,
            )

            pygame.draw.rect(
                self.surface,
                background,
                rect,
                border_radius=8,
            )

            pygame.draw.rect(
                self.surface,
                (180, 180, 180),
                rect,
                2,
                border_radius=8,
            )

            text = self.node_font.render(
                str(value),
                True,
                (240, 240, 240),
            )

            text_rect = text.get_rect(
                center=rect.center,
            )

            self.surface.blit(
                text,
                text_rect,
            )

            if index < len(values) - 1:
                start = (
                    rect.right,
                    rect.centery,
                )

                end = (
                    node_x + node_width + spacing,
                    rect.centery,
                )

                pygame.draw.line(
                    self.surface,
                    (180, 180, 180),
                    start,
                    end,
                    3,
                )

                arrow_x = end[0] - 10

                pygame.draw.polygon(
                    self.surface,
                    (180, 180, 180),
                    [
                        (arrow_x, end[1] - 6),
                        (end[0], end[1]),
                        (arrow_x, end[1] + 6),
                    ],
                )

        null_x = (
            x
            + len(values) * (node_width + spacing)
            - spacing
        )

        self._draw_text(
            "NULL",
            (null_x, y + 15),
            self.node_font,
        )