from __future__ import annotations

import pygame

from algolab.simulation.simulator import Simulator
from algolab.topics.stack.model import Stack
from algolab.topics.stack.simulation import (
    StackSimulation,
    StackSimulator,
)
from algolab.ui.components.button import Button
from algolab.ui.components.numeric_input import NumericInput
from algolab.ui.screens.screen import Screen


class StackScreen(Screen):
    """Screen for visualizing stack operations."""

    def __init__(self, surface: pygame.Surface) -> None:
        super().__init__(surface)

        self.model = Stack()
        self.simulator = Simulator()
        self.stack_simulator = StackSimulator(self.model)

        self.current_simulation: StackSimulation | None = None
        self.operation_committed = False

        self.control_font = pygame.font.Font(None, 30)
        self.section_font = pygame.font.Font(None, 24)
        self.item_font = pygame.font.Font(None, 30)
        self.small_font = pygame.font.Font(None, 22)
        self.explanation_font = pygame.font.Font(None, 25)
        self.pointer_font = pygame.font.Font(None, 20)
        self.index_font = pygame.font.Font(None, 18)

        self.operation_buttons = self._create_operation_buttons()
        self.navigation_buttons = self._create_navigation_buttons()

        self.value_input = NumericInput(
            pygame.Rect(135, 285, 75, 30),
            10,
        )

        self.step_timer = 0.0

        # A longer interval gives students time to understand each step.
        self.step_interval = 1.8

        # Stack visual layout.
        self.stack_x = 610
        self.stack_width = 150
        self.item_height = 55
        self.item_spacing = 10
        self.stack_first_y = 300

        # TOP pointer layout.
        self.pointer_x = self.stack_x - 130
        self.pointer_start_y = self.stack_first_y - 30

    def _create_operation_buttons(self) -> list[Button]:
        labels = [
            "Push",
            "Pop",
            "Peek",
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
        labels = ["|<", "<", ">", ">|", "P"]

        buttons = []

        x = 25
        y = 375
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
        rendered_text = font.render(
            text,
            True,
            (240, 240, 240),
        )

        self.surface.blit(
            rendered_text,
            position,
        )

    def _draw_wrapped_text(
        self,
        text: str,
        rect: pygame.Rect,
        font: pygame.font.Font,
        color: tuple[int, int, int] = (235, 235, 235),
    ) -> None:
        words = text.split()

        lines = []
        current_line = ""

        for word in words:
            test_line = (
                word
                if not current_line
                else f"{current_line} {word}"
            )

            if font.size(test_line)[0] <= rect.width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)

                current_line = word

        if current_line:
            lines.append(current_line)

        line_height = font.get_height()
        y = rect.y

        for line in lines:
            if y + line_height > rect.bottom:
                break

            rendered_text = font.render(
                line,
                True,
                color,
            )

            self.surface.blit(
                rendered_text,
                (rect.x, y),
            )

            y += line_height

    def handle_event(self, event: pygame.event.Event) -> None:
        self.value_input.handle_event(event)

        for index, button in enumerate(self.operation_buttons):
            if button.handle_event(event):
                self._select_operation(index)

        for index, button in enumerate(self.navigation_buttons):
            if button.handle_event(event):
                self._handle_navigation(index)

    def _select_operation(self, index: int) -> None:
        if self.current_simulation is not None:
            return

        value = self.value_input.value

        try:
            if index == 0:
                simulation = self.stack_simulator.push(value)

            elif index == 1:
                simulation = self.stack_simulator.pop()

            elif index == 2:
                simulation = self.stack_simulator.peek()

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
        if self.operation_committed:
            return

        if not self.simulator.is_at_end:
            return

        if self.current_simulation is None:
            return

        self.current_simulation.commit(self.model)

        self.operation_committed = True
        self.current_simulation = None

        self.simulator.reset()

    def update(self, dt: float) -> None:
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
        self.surface.fill((30, 30, 30))

        self._render_control_panel()
        self._render_explanation_panel()
        self._render_stack()

    def _render_control_panel(self) -> None:
        pygame.draw.rect(
            self.surface,
            (40, 40, 40),
            pygame.Rect(10, 70, 250, 500),
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
            (25, 290),
            self.section_font,
        )

        self.value_input.render(self.surface)

        self._draw_text(
            "Simulation",
            (25, 355),
            self.section_font,
        )

        for button in self.navigation_buttons:
            button.render(self.surface)

        if self.current_simulation is not None:
            state = self.simulator.state

            if state is not None:
                self._draw_text(
                    (
                        f"Step: {state.step + 1}/"
                        f"{len(self.current_simulation.states)}"
                    ),
                    (25, 425),
                    self.small_font,
                )

    def _render_explanation_panel(self) -> None:
        panel_rect = pygame.Rect(
            280,
            70,
            self.surface.get_width() - 300,
            130,
        )

        pygame.draw.rect(
            self.surface,
            (40, 40, 40),
            panel_rect,
            border_radius=8,
        )

        pygame.draw.rect(
            self.surface,
            (90, 90, 90),
            panel_rect,
            2,
            border_radius=8,
        )

        self._draw_text(
            "What is happening?",
            (295, 82),
            self.section_font,
        )

        state = self.simulator.state

        if state is None:
            description = (
                "Select an operation to start a simulation."
            )
        else:
            simulation_state = state.data
            description = simulation_state.description

        description_rect = pygame.Rect(
            295,
            112,
            panel_rect.width - 30,
            75,
        )

        self._draw_wrapped_text(
            description,
            description_rect,
            self.explanation_font,
        )

    def _get_simulation_state(self):
        if self.simulator.state is None:
            return None

        return self.simulator.state.data

    def _render_stack(self) -> None:
        """
        Render the stack vertically.

        The bottom item is rendered first and the top item is rendered
        last. The TOP pointer is determined directly from top_index
        stored in the simulation state.
        """

        values = tuple(self.model.to_list())
        state = self._get_simulation_state()

        top_index: int | None = None
        created_value = None
        removed_value = None
        peeked_value = None

        if state is None:
            top_index = (
                len(values) - 1
                if values
                else None
            )

        else:
            values = state.values
            top_index = state.top_index

            created_value = state.created_value
            removed_value = state.removed_value
            peeked_value = state.peeked_value

        self._render_stack_items(
            values=values,
            top_index=top_index,
            created_value=created_value,
            removed_value=removed_value,
            peeked_value=peeked_value,
        )

        self._render_top_pointer(
            top_index=top_index,
            values=values,
        )

    def _render_top_pointer(
        self,
        top_index: int | None,
        values: tuple[object, ...],
    ) -> None:
        """Render the TOP pointer for the current simulation state."""

        if top_index is None or not values:
            null_start = (
                self.pointer_x + 25,
                self.pointer_start_y,
            )

            null_end = (
                self.pointer_x + 25,
                self.stack_first_y + 10,
            )

            self._draw_text(
                "TOP",
                (
                    self.pointer_x,
                    self.pointer_start_y - 30,
                ),
                self.control_font,
            )

            pygame.draw.line(
                self.surface,
                (100, 200, 140),
                null_start,
                null_end,
                3,
            )

            self._draw_arrow_head(
                null_end,
                (100, 200, 140),
                "down",
            )

            self._draw_text(
                "NULL",
                (
                    self.pointer_x + 40,
                    null_end[1] - 10,
                ),
                self.pointer_font,
            )

            return

        if top_index < 0 or top_index >= len(values):
            return

        top_y = self._get_item_y(
            top_index,
            len(values),
        )

        start = (
            self.pointer_x + 25,
            self.pointer_start_y,
        )

        end = (
            self.stack_x - 10,
            top_y + self.item_height // 2,
        )

        self._draw_text(
            "TOP",
            (
                self.pointer_x,
                self.pointer_start_y - 30,
            ),
            self.control_font,
        )

        pygame.draw.line(
            self.surface,
            (100, 200, 140),
            start,
            end,
            3,
        )

        self._draw_arrow_head(
            end,
            (100, 200, 140),
            "right",
        )

        self._draw_text(
            f"item {top_index}",
            (
                self.pointer_x - 5,
                self.pointer_start_y + 10,
            ),
            self.pointer_font,
        )

    def _render_stack_items(
        self,
        values: tuple[object, ...],
        top_index: int | None,
        created_value: object | None,
        removed_value: object | None,
        peeked_value: object | None,
    ) -> None:
        if values:
            for index, value in enumerate(values):
                y = self._get_item_y(
                    index,
                    len(values),
                )

                background = (65, 85, 115)

                if index == top_index:
                    background = (70, 110, 180)

                if (
                    peeked_value is not None
                    and index == top_index
                    and value == peeked_value
                ):
                    background = (100, 135, 200)

                self._draw_stack_item(
                    x=self.stack_x,
                    y=y,
                    width=self.stack_width,
                    height=self.item_height,
                    index=index,
                    value=value,
                    background=background,
                )

        # A PUSH item is deliberately detached from the stack.
        #
        # The simulation state still contains the old values here, so
        # the new item must NOT be rendered as part of the stack yet.
        if created_value is not None:
            self._render_detached_item(
                x=self.stack_x,
                y=self.stack_first_y - 90,
                width=self.stack_width,
                height=self.item_height,
                label="NEW",
                value=created_value,
                background=(65, 150, 105),
            )

        # A POP item is rendered separately while it is being removed.
        if removed_value is not None:
            removed_y = self.stack_first_y

            if values:
                removed_index = len(values) - 1

                removed_y = self._get_item_y(
                    removed_index,
                    len(values),
                )

            self._render_detached_item(
                x=self.stack_x + self.stack_width + 100,
                y=removed_y,
                width=self.stack_width,
                height=self.item_height,
                label="REMOVED",
                value=removed_value,
                background=(165, 75, 75),
            )

    def _draw_stack_item(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        index: int,
        value: object,
        background: tuple[int, int, int],
    ) -> None:
        rect = pygame.Rect(
            x,
            y,
            width,
            height,
        )

        pygame.draw.rect(
            self.surface,
            background,
            rect,
            border_radius=6,
        )

        pygame.draw.rect(
            self.surface,
            (210, 210, 210),
            rect,
            2,
            border_radius=6,
        )

        value_text = self.item_font.render(
            str(value),
            True,
            (245, 245, 245),
        )

        value_rect = value_text.get_rect(
            center=rect.center,
        )

        self.surface.blit(
            value_text,
            value_rect,
        )

        index_text = self.index_font.render(
            f"index {index}",
            True,
            (200, 200, 200),
        )

        index_rect = index_text.get_rect(
            centerx=rect.centerx,
            top=rect.bottom + 3,
        )

        self.surface.blit(
            index_text,
            index_rect,
        )

    def _render_detached_item(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        label: str,
        value: object,
        background: tuple[int, int, int],
    ) -> None:
        label_surface = self.pointer_font.render(
            label,
            True,
            background,
        )

        label_rect = label_surface.get_rect(
            centerx=x + width // 2,
            bottom=y - 5,
        )

        self.surface.blit(
            label_surface,
            label_rect,
        )

        rect = pygame.Rect(
            x,
            y,
            width,
            height,
        )

        pygame.draw.rect(
            self.surface,
            background,
            rect,
            border_radius=6,
        )

        pygame.draw.rect(
            self.surface,
            (230, 230, 230),
            rect,
            2,
            border_radius=6,
        )

        value_text = self.item_font.render(
            str(value),
            True,
            (245, 245, 245),
        )

        value_rect = value_text.get_rect(
            center=rect.center,
        )

        self.surface.blit(
            value_text,
            value_rect,
        )

    def _get_item_y(
        self,
        index: int,
        value_count: int,
    ) -> int:
        """
        Convert a stack index into a screen Y coordinate.

        Index 0 is the bottom item. The largest index is the top item.
        """

        return (
            self.stack_first_y
            + (value_count - 1 - index)
            * (self.item_height + self.item_spacing)
        )

    def _draw_arrow_head(
        self,
        position: tuple[int, int],
        color: tuple[int, int, int],
        direction: str,
    ) -> None:
        x, y = position
        size = 8

        if direction == "right":
            points = [
                (x, y),
                (x - size, y - size // 2),
                (x - size, y + size // 2),
            ]

        elif direction == "down":
            points = [
                (x, y),
                (x - size // 2, y - size),
                (x + size // 2, y - size),
            ]

        else:
            return

        pygame.draw.polygon(
            self.surface,
            color,
            points,
        )