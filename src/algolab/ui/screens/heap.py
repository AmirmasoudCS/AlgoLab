from __future__ import annotations

import pygame

from algolab.topics.heap.model import Heap, HeapType
from algolab.topics.heap.simulation import (
    HeapSimulation,
    HeapSimulationState,
    HeapSimulator,
)
from algolab.ui.components.button import Button
from algolab.ui.components.numeric_input import NumericInput
from algolab.ui.screens.screen import Screen


class HeapScreen(Screen):
    """Screen for visualizing binary heap operations."""

    BACKGROUND = (245, 245, 245)
    PANEL = (255, 255, 255)
    BORDER = (210, 210, 210)
    TEXT = (35, 35, 35)
    MUTED_TEXT = (100, 100, 100)

    NODE = (225, 235, 245)
    NODE_BORDER = (80, 110, 140)

    COMPARE = (255, 220, 120)
    SWAP = (255, 150, 120)
    CREATED = (150, 220, 170)
    EXTRACTED = (240, 150, 150)

    BUTTON = (220, 225, 230)
    BUTTON_HOVER = (200, 210, 220)

    def __init__(
        self,
        surface: pygame.Surface,
    ) -> None:
        super().__init__(surface)

        self.model = Heap[int](HeapType.MIN)
        self.simulator = HeapSimulator(self.model)

        self.current_simulation: HeapSimulation | None = None
        self.current_step = 0

        self.operation_committed = False
        self.status_message: str | None = None

        self.font = pygame.font.Font(None, 28)
        self.small_font = pygame.font.Font(None, 22)
        self.title_font = pygame.font.Font(None, 40)

        self.input_box = NumericInput(
            pygame.Rect(30, 95, 130, 42),
        )

        self.insert_button = Button(
            pygame.Rect(175, 95, 100, 42),
            "Insert",
        )

        self.peek_button = Button(
            pygame.Rect(285, 95, 100, 42),
            "Peek",
        )

        self.extract_button = Button(
            pygame.Rect(395, 95, 100, 42),
            "Extract",
        )

        self.build_button = Button(
            pygame.Rect(505, 95, 125, 42),
            "Build Heap",
        )

        self.clear_button = Button(
            pygame.Rect(640, 95, 90, 42),
            "Clear",
        )

        self.min_button = Button(
            pygame.Rect(30, 150, 110, 38),
            "Min Heap",
        )

        self.max_button = Button(
            pygame.Rect(150, 150, 110, 38),
            "Max Heap",
        )

        self.previous_button = Button(
            pygame.Rect(760, 610, 100, 42),
            "Previous",
        )

        self.next_button = Button(
            pygame.Rect(870, 610, 100, 42),
            "Next",
        )

        self.commit_button = Button(
            pygame.Rect(650, 610, 100, 42),
            "Commit",
        )

    def handle_event(
        self,
        event: pygame.event.Event,
    ) -> None:
        """Handle an incoming Pygame event."""

        self.input_box.handle_event(event)

        if event.type != pygame.MOUSEBUTTONDOWN:
            return

        position = event.pos

        if self.insert_button.rect.collidepoint(position):
            self._start_insert()

        elif self.peek_button.rect.collidepoint(position):
            self._start_peek()

        elif self.extract_button.rect.collidepoint(position):
            self._start_extract()

        elif self.build_button.rect.collidepoint(position):
            self._start_build_heap()

        elif self.clear_button.rect.collidepoint(position):
            self._start_clear()

        elif self.min_button.rect.collidepoint(position):
            self._set_heap_type(HeapType.MIN)

        elif self.max_button.rect.collidepoint(position):
            self._set_heap_type(HeapType.MAX)

        elif self.previous_button.rect.collidepoint(position):
            self._previous_step()

        elif self.next_button.rect.collidepoint(position):
            self._next_step()

        elif self.commit_button.rect.collidepoint(position):
            self._commit_simulation()

    def update(self, dt: float) -> None:
        """Update the heap screen."""

    def render(self) -> None:
        """Render the heap screen."""

        self.surface.fill(self.BACKGROUND)

        self._render_title()
        self._render_controls()
        self._render_heap_panel()
        self._render_array_panel()
        self._render_description()
        self._render_simulation_controls()

    def _render_title(self) -> None:
        title = self.title_font.render(
            "Heap",
            True,
            self.TEXT,
        )

        self.surface.blit(
            title,
            (30, 25),
        )

        heap_type_text = (
            "Min Heap"
            if self.model.heap_type is HeapType.MIN
            else "Max Heap"
        )

        subtitle = self.small_font.render(
            heap_type_text,
            True,
            self.MUTED_TEXT,
        )

        self.surface.blit(
            subtitle,
            (105, 34),
        )

    def _render_controls(self) -> None:
        self._draw_button(self.insert_button)
        self._draw_button(self.peek_button)
        self._draw_button(self.extract_button)
        self._draw_button(self.build_button)
        self._draw_button(self.clear_button)

        self._draw_button(self.min_button)
        self._draw_button(self.max_button)

        input_label = self.small_font.render(
            "Value",
            True,
            self.TEXT,
        )

        self.surface.blit(
            input_label,
            (30, 72),
        )

    def _render_heap_panel(self) -> None:
        panel_rect = pygame.Rect(
            30,
            205,
            940,
            320,
        )

        pygame.draw.rect(
            self.surface,
            self.PANEL,
            panel_rect,
        )

        pygame.draw.rect(
            self.surface,
            self.BORDER,
            panel_rect,
            2,
        )

        label = self.font.render(
            "Heap Tree",
            True,
            self.TEXT,
        )

        self.surface.blit(
            label,
            (50, 220),
        )

        state = self._current_state()

        if state is None:
            values = self.model.values
            compared_indices = None
            swapped_indices = None
            current_index = None
            created_value = None
            extracted_value = None
        else:
            values = list(state.values)
            compared_indices = state.compared_indices
            swapped_indices = state.swapped_indices
            current_index = state.current_index
            created_value = state.created_value
            extracted_value = state.extracted_value

        if not values:
            empty_text = self.font.render(
                "Heap is empty",
                True,
                self.MUTED_TEXT,
            )

            rect = empty_text.get_rect(
                center=panel_rect.center,
            )

            self.surface.blit(
                empty_text,
                rect,
            )

            return

        positions = self._calculate_node_positions(
            values,
            panel_rect,
        )

        self._render_tree_edges(
            values,
            positions,
        )

        self._render_tree_nodes(
            values=values,
            positions=positions,
            compared_indices=compared_indices,
            swapped_indices=swapped_indices,
            current_index=current_index,
            created_value=created_value,
            extracted_value=extracted_value,
        )

    def _render_array_panel(self) -> None:
        panel_rect = pygame.Rect(
            30,
            540,
            940,
            55,
        )

        pygame.draw.rect(
            self.surface,
            self.PANEL,
            panel_rect,
        )

        pygame.draw.rect(
            self.surface,
            self.BORDER,
            panel_rect,
            2,
        )

        label = self.small_font.render(
            "Array:",
            True,
            self.TEXT,
        )

        self.surface.blit(
            label,
            (45, 557),
        )

        state = self._current_state()

        if state is None:
            values = self.model.values
        else:
            values = list(state.values)

        x = 125

        for index, value in enumerate(values):
            cell_rect = pygame.Rect(
                x,
                550,
                48,
                35,
            )

            pygame.draw.rect(
                self.surface,
                self.NODE,
                cell_rect,
            )

            pygame.draw.rect(
                self.surface,
                self.NODE_BORDER,
                cell_rect,
                1,
            )

            value_surface = self.small_font.render(
                str(value),
                True,
                self.TEXT,
            )

            value_rect = value_surface.get_rect(
                center=cell_rect.center,
            )

            self.surface.blit(
                value_surface,
                value_rect,
            )

            index_surface = pygame.font.Font(
                None,
                16,
            ).render(
                str(index),
                True,
                self.MUTED_TEXT,
            )

            index_rect = index_surface.get_rect(
                center=(cell_rect.centerx, 594),
            )

            self.surface.blit(
                index_surface,
                index_rect,
            )

            x += 58

            if x > 940:
                break

    def _render_description(self) -> None:
        state = self._current_state()

        if state is not None:
            description = state.description
        elif self.status_message is not None:
            description = self.status_message
        else:
            description = (
                "Select an operation to start a simulation."
            )

        text = self.small_font.render(
            description,
            True,
            self.TEXT,
        )

        self.surface.blit(
            text,
            (30, 600),
        )

    def _render_simulation_controls(self) -> None:
        self._draw_button(self.previous_button)
        self._draw_button(self.next_button)
        self._draw_button(self.commit_button)

        if self.current_simulation is None:
            return

        step_text = self.small_font.render(
            (
                f"Step {self.current_step + 1} / "
                f"{len(self.current_simulation.states)}"
            ),
            True,
            self.TEXT,
        )

        self.surface.blit(
            step_text,
            (500, 622),
        )

    def _draw_button(self, button: Button) -> None:
        mouse_position = pygame.mouse.get_pos()

        color = (
            self.BUTTON_HOVER
            if button.rect.collidepoint(mouse_position)
            else self.BUTTON
        )

        pygame.draw.rect(
            self.surface,
            color,
            button.rect,
        )

        pygame.draw.rect(
            self.surface,
            self.BORDER,
            button.rect,
            1,
        )

        text = self.small_font.render(
            button.text,
            True,
            self.TEXT,
        )

        text_rect = text.get_rect(
            center=button.rect.center,
        )

        self.surface.blit(
            text,
            text_rect,
        )

    def _calculate_node_positions(
        self,
        values: list[object],
        panel_rect: pygame.Rect,
    ) -> dict[int, tuple[int, int]]:
        """Calculate positions for nodes in the heap tree."""

        positions: dict[int, tuple[int, int]] = {}

        node_radius = 24
        top_y = panel_rect.top + 65

        max_level = 0

        for index in range(len(values)):
            level = (index + 1).bit_length() - 1
            max_level = max(max_level, level)

        level_height = 70

        for index in range(len(values)):
            level = (index + 1).bit_length() - 1

            first_index = (2**level) - 1
            position_in_level = index - first_index
            nodes_in_level = 2**level

            available_width = panel_rect.width - 80

            if nodes_in_level == 1:
                x = panel_rect.centerx
            else:
                spacing = available_width / nodes_in_level

                x = int(
                    panel_rect.left
                    + 40
                    + spacing * (position_in_level + 0.5)
                )

            y = top_y + level * level_height

            positions[index] = (x, y)

        return positions

    def _render_tree_edges(
        self,
        values: list[object],
        positions: dict[int, tuple[int, int]],
    ) -> None:
        """Render edges between heap nodes."""

        for index in range(1, len(values)):
            parent_index = (index - 1) // 2

            parent_position = positions[parent_index]
            child_position = positions[index]

            pygame.draw.line(
                self.surface,
                self.BORDER,
                parent_position,
                child_position,
                2,
            )

    def _render_tree_nodes(
        self,
        values: list[object],
        positions: dict[int, tuple[int, int]],
        compared_indices: tuple[int, int] | None,
        swapped_indices: tuple[int, int] | None,
        current_index: int | None,
        created_value: object | None,
        extracted_value: object | None,
    ) -> None:
        """Render heap nodes and their visual state."""

        for index, value in enumerate(values):
            position = positions[index]

            node_color = self.NODE

            if compared_indices is not None and (
                index in compared_indices
            ):
                node_color = self.COMPARE

            if swapped_indices is not None and (
                index in swapped_indices
            ):
                node_color = self.SWAP

            if (
                created_value is not None
                and value == created_value
                and current_index == index
            ):
                node_color = self.CREATED

            if (
                extracted_value is not None
                and value == extracted_value
                and current_index == index
            ):
                node_color = self.EXTRACTED

            if current_index == index:
                pygame.draw.circle(
                    self.surface,
                    node_color,
                    position,
                    27,
                )

                pygame.draw.circle(
                    self.surface,
                    self.NODE_BORDER,
                    position,
                    27,
                    3,
                )
            else:
                pygame.draw.circle(
                    self.surface,
                    node_color,
                    position,
                    24,
                )

                pygame.draw.circle(
                    self.surface,
                    self.NODE_BORDER,
                    position,
                    24,
                    2,
                )

            value_surface = self.font.render(
                str(value),
                True,
                self.TEXT,
            )

            value_rect = value_surface.get_rect(
                center=position,
            )

            self.surface.blit(
                value_surface,
                value_rect,
            )

            index_surface = pygame.font.Font(
                None,
                16,
            ).render(
                f"[{index}]",
                True,
                self.MUTED_TEXT,
            )

            index_rect = index_surface.get_rect(
                center=(
                    position[0],
                    position[1] + 37,
                ),
            )

            self.surface.blit(
                index_surface,
                index_rect,
            )

    def _current_state(
        self,
    ) -> HeapSimulationState | None:
        """Return the current heap simulation state."""

        if self.current_simulation is None:
            return None

        if not self.current_simulation.states:
            return None

        state = self.current_simulation.states[
            self.current_step
        ]

        return state.data

    def _start_insert(self) -> None:
        value = self._get_input_value()

        if value is None:
            return

        self.status_message = None

        self.current_simulation = (
            self.simulator.insert(value)
        )

        self.current_step = 0
        self.operation_committed = False

    def _start_peek(self) -> None:
        self.status_message = None

        self.current_simulation = (
            self.simulator.peek()
        )

        self.current_step = 0
        self.operation_committed = False

    def _start_extract(self) -> None:
        self.status_message = None

        self.current_simulation = (
            self.simulator.extract()
        )

        self.current_step = 0
        self.operation_committed = False

    def _start_build_heap(self) -> None:
        values = self.model.values

        self.status_message = None

        self.current_simulation = (
            self.simulator.build_heap(values)
        )

        self.current_step = 0
        self.operation_committed = False

    def _start_clear(self) -> None:
        self.status_message = None

        self.current_simulation = (
            self.simulator.clear()
        )

        self.current_step = 0
        self.operation_committed = False

    def _get_input_value(self) -> int | None:
        """Return the integer currently entered by the user."""

        try:
            return int(self.input_box.value)
        except (TypeError, ValueError):
            return None

    def _set_heap_type(
        self,
        heap_type: HeapType,
    ) -> None:
        """Change the heap type and reset the heap."""

        if self.model.heap_type is heap_type:
            return

        self.model = Heap[int](heap_type)
        self.simulator = HeapSimulator(self.model)

        self.current_simulation = None
        self.current_step = 0
        self.operation_committed = False
        self.status_message = None

    def _previous_step(self) -> None:
        """Move to the previous simulation state."""

        if self.current_simulation is None:
            return

        if self.current_step > 0:
            self.current_step -= 1

    def _next_step(self) -> None:
        """Move to the next simulation state."""

        if self.current_simulation is None:
            return

        last_step = len(
            self.current_simulation.states
        ) - 1

        if self.current_step < last_step:
            self.current_step += 1

    def _commit_simulation(self) -> None:
        """Commit the current simulation to the heap model."""

        if self.current_simulation is None:
            return

        last_step = len(
            self.current_simulation.states
        ) - 1

        if self.current_step != last_step:
            return

        final_state = self.current_simulation.states[
            -1
        ]

        self.status_message = (
            final_state.data.description
        )

        self.current_simulation.commit(
            self.model
        )

        self.operation_committed = True
        self.current_simulation = None
        self.current_step = 0

        self.simulator = HeapSimulator(
            self.model
        )