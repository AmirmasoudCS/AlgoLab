from __future__ import annotations

import pygame

from algolab.simulation.events import SimulationEvent
from algolab.topics.heap.model import Heap, HeapType
from algolab.topics.heap.simulation import (
    CompareHeapElementsEvent,
    CreateHeapElementEvent,
    ExtractHeapElementEvent,
    HeapSimulation,
    HeapSimulator,
    MoveLastElementEvent,
    SwapHeapElementsEvent,
)
from algolab.ui.components.button import Button
from algolab.ui.components.numeric_input import NumericInput
from algolab.ui.screens.screen import Screen


class HeapScreen(Screen):
    """Screen for interacting with and visualizing a binary heap."""

    def __init__(self, surface: pygame.Surface) -> None:
        super().__init__(surface)

        self.heap = Heap[int](HeapType.MIN)

        self.simulation: HeapSimulation | None = None
        self.simulation_index = 0

        self.title_font = pygame.font.Font(None, 42)
        self.text_font = pygame.font.Font(None, 26)
        self.small_font = pygame.font.Font(None, 22)

        self._create_components()

    def _create_components(self) -> None:
        """Create the controls used by the screen."""

        self.min_heap_button = Button(
            pygame.Rect(30, 80, 120, 42),
            "Min Heap",
        )

        self.max_heap_button = Button(
            pygame.Rect(160, 80, 120, 42),
            "Max Heap",
        )

        self.value_input = NumericInput(
            pygame.Rect(30, 140, 120, 40),
            10,
        )

        self.insert_button = Button(
            pygame.Rect(160, 140, 100, 40),
            "Insert",
        )

        self.peek_button = Button(
            pygame.Rect(270, 140, 100, 40),
            "Peek",
        )

        self.extract_button = Button(
            pygame.Rect(380, 140, 100, 40),
            "Extract",
        )

        self.build_button = Button(
            pygame.Rect(490, 140, 120, 40),
            "Build Heap",
        )

        self.clear_button = Button(
            pygame.Rect(620, 140, 100, 40),
            "Clear",
        )

        self.previous_button = Button(
            pygame.Rect(30, 650, 100, 40),
            "Previous",
        )

        self.next_button = Button(
            pygame.Rect(140, 650, 100, 40),
            "Next",
        )

        self.commit_button = Button(
            pygame.Rect(250, 650, 100, 40),
            "Commit",
        )

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle input events."""

        value = self.value_input.handle_event(event)

        if value is not None:
            return

        if self.min_heap_button.handle_event(event):
            self._set_heap_type(HeapType.MIN)
            return

        if self.max_heap_button.handle_event(event):
            self._set_heap_type(HeapType.MAX)
            return

        if self.insert_button.handle_event(event):
            self._start_insert()
            return

        if self.peek_button.handle_event(event):
            self._start_peek()
            return

        if self.extract_button.handle_event(event):
            self._start_extract()
            return

        if self.build_button.handle_event(event):
            self._start_build_heap()
            return

        if self.clear_button.handle_event(event):
            self._start_clear()
            return

        if self.previous_button.handle_event(event):
            self._previous_step()
            return

        if self.next_button.handle_event(event):
            self._next_step()
            return

        if self.commit_button.handle_event(event):
            self._commit_simulation()

    def update(self, dt: float) -> None:
        """Update the screen."""

    def render(self) -> None:
        """Render the heap screen."""

        self.surface.fill((20, 20, 20))

        self._render_title()
        self._render_controls()
        self._render_heap_tree()
        self._render_array()
        self._render_simulation_info()

    # ------------------------------------------------------------------
    # Operations
    # ------------------------------------------------------------------

    def _set_heap_type(self, heap_type: HeapType) -> None:
        """Change the heap type and clear the current heap."""

        if self.heap.heap_type is heap_type:
            return

        self.heap = Heap[int](heap_type)
        self._reset_simulation()

    def _start_insert(self) -> None:
        """Start an insert simulation."""

        self.simulation = HeapSimulator(self.heap).insert(
            self.value_input.value
        )

        self.simulation_index = 0

    def _start_peek(self) -> None:
        """Start a peek simulation."""

        self.simulation = HeapSimulator(self.heap).peek()
        self.simulation_index = 0

    def _start_extract(self) -> None:
        """Start an extract simulation."""

        self.simulation = HeapSimulator(self.heap).extract()
        self.simulation_index = 0

    def _start_build_heap(self) -> None:
        """Start a build-heap simulation."""

        values = self.heap.values

        if not values:
            return

        self.simulation = HeapSimulator(self.heap).build_heap(values)
        self.simulation_index = 0

    def _start_clear(self) -> None:
        """Start a clear simulation."""

        self.simulation = HeapSimulator(self.heap).clear()
        self.simulation_index = 0

    def _reset_simulation(self) -> None:
        """Clear the current simulation."""

        self.simulation = None
        self.simulation_index = 0

    def _commit_simulation(self) -> None:
        """Commit the current simulation to the actual heap."""

        if self.simulation is None:
            return

        self.simulation.commit(self.heap)

        self._reset_simulation()

    # ------------------------------------------------------------------
    # Simulation navigation
    # ------------------------------------------------------------------

    def _previous_step(self) -> None:
        """Move to the previous simulation state."""

        if self.simulation is None:
            return

        if self.simulation_index > 0:
            self.simulation_index -= 1

    def _next_step(self) -> None:
        """Move to the next simulation state."""

        if self.simulation is None:
            return

        last_index = len(self.simulation.states) - 1

        if self.simulation_index < last_index:
            self.simulation_index += 1

    @property
    def _current_state(self):
        """Return the current simulation state."""

        if self.simulation is None:
            return None

        return self.simulation.states[self.simulation_index]

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------

    def _render_title(self) -> None:
        """Render the screen title."""

        heap_name = (
            "Min Heap"
            if self.heap.heap_type is HeapType.MIN
            else "Max Heap"
        )

        title = self.title_font.render(
            heap_name,
            True,
            (240, 240, 240),
        )

        self.surface.blit(
            title,
            (30, 25),
        )

    def _render_controls(self) -> None:
        """Render all interaction controls."""

        self.min_heap_button.render(self.surface)
        self.max_heap_button.render(self.surface)

        self.value_input.render(self.surface)

        self.insert_button.render(self.surface)
        self.peek_button.render(self.surface)
        self.extract_button.render(self.surface)
        self.build_button.render(self.surface)
        self.clear_button.render(self.surface)

        self.previous_button.render(self.surface)
        self.next_button.render(self.surface)
        self.commit_button.render(self.surface)

    def _render_heap_tree(self) -> None:
        """Render the heap as a binary tree."""

        values = self._display_values()

        if not values:
            text = self.text_font.render(
                "Heap is empty",
                True,
                (160, 160, 160),
            )

            rect = text.get_rect(
                center=(500, 330),
            )

            self.surface.blit(text, rect)

            return

        positions = self._calculate_node_positions(len(values))

        self._render_tree_edges(
            values,
            positions,
        )

        for index, value in enumerate(values):
            self._render_tree_node(
                index,
                value,
                positions[index],
            )

    def _render_tree_edges(
        self,
        values: tuple[object, ...] | list[object],
        positions: dict[int, tuple[int, int]],
    ) -> None:
        """Render edges between heap nodes."""

        for index in range(len(values)):
            left_index = 2 * index + 1
            right_index = 2 * index + 2

            if left_index < len(values):
                pygame.draw.line(
                    self.surface,
                    (100, 100, 100),
                    positions[index],
                    positions[left_index],
                    2,
                )

            if right_index < len(values):
                pygame.draw.line(
                    self.surface,
                    (100, 100, 100),
                    positions[index],
                    positions[right_index],
                    2,
                )

    def _render_tree_node(
        self,
        index: int,
        value: object,
        position: tuple[int, int],
    ) -> None:
        """Render one heap node."""

        color = self._node_color(index)

        pygame.draw.circle(
            self.surface,
            color,
            position,
            28,
        )

        pygame.draw.circle(
            self.surface,
            (180, 180, 180),
            position,
            28,
            2,
        )

        text = self.text_font.render(
            str(value),
            True,
            (240, 240, 240),
        )

        text_rect = text.get_rect(
            center=position,
        )

        self.surface.blit(
            text,
            text_rect,
        )

        index_text = self.small_font.render(
            str(index),
            True,
            (150, 150, 150),
        )

        index_rect = index_text.get_rect(
            center=(
                position[0],
                position[1] + 40,
            ),
        )

        self.surface.blit(
            index_text,
            index_rect,
        )

    def _node_color(self, index: int) -> tuple[int, int, int]:
        """Return the visualization color for a heap node."""

        state = self._current_state

        if state is None:
            return (50, 50, 50)

        if state.swapped_indices is not None:
            if index in state.swapped_indices:
                return (180, 100, 60)

        if state.compared_indices is not None:
            if index in state.compared_indices:
                return (70, 120, 180)

        if state.current_index == index:
            return (80, 160, 100)

        return (50, 50, 50)

    def _calculate_node_positions(
        self,
        size: int,
    ) -> dict[int, tuple[int, int]]:
        """Calculate screen positions for heap nodes."""

        positions: dict[int, tuple[int, int]] = {}

        start_x = 500
        start_y = 245

        level_height = 85

        for index in range(size):
            level = index.bit_length() - 1

            first_index = (2**level) - 1
            position_in_level = index - first_index
            nodes_in_level = 2**level

            available_width = 760

            if nodes_in_level == 1:
                x = start_x
            else:
                spacing = available_width / (nodes_in_level - 1)

                x = (
                    120
                    + position_in_level * spacing
                )

            y = start_y + level * level_height

            positions[index] = (
                int(x),
                int(y),
            )

        return positions

    def _render_array(self) -> None:
        """Render the heap's underlying array representation."""

        values = self._display_values()

        label = self.text_font.render(
            "Array:",
            True,
            (220, 220, 220),
        )

        self.surface.blit(
            label,
            (30, 500),
        )

        x = 120
        y = 485

        for index, value in enumerate(values):
            rect = pygame.Rect(
                x,
                y,
                60,
                42,
            )

            border_color = self._array_cell_color(index)

            pygame.draw.rect(
                self.surface,
                (35, 35, 35),
                rect,
            )

            pygame.draw.rect(
                self.surface,
                border_color,
                rect,
                2,
            )

            value_text = self.small_font.render(
                str(value),
                True,
                (240, 240, 240),
            )

            value_rect = value_text.get_rect(
                center=rect.center,
            )

            self.surface.blit(
                value_text,
                value_rect,
            )

            index_text = self.small_font.render(
                str(index),
                True,
                (130, 130, 130),
            )

            index_rect = index_text.get_rect(
                center=(
                    rect.centerx,
                    rect.bottom + 15,
                ),
            )

            self.surface.blit(
                index_text,
                index_rect,
            )

            x += 70

    def _array_cell_color(
        self,
        index: int,
    ) -> tuple[int, int, int]:
        """Return the border color for an array cell."""

        state = self._current_state

        if state is None:
            return (100, 100, 100)

        if state.swapped_indices is not None:
            if index in state.swapped_indices:
                return (180, 100, 60)

        if state.compared_indices is not None:
            if index in state.compared_indices:
                return (70, 120, 180)

        if state.current_index == index:
            return (80, 160, 100)

        return (100, 100, 100)

    def _render_simulation_info(self) -> None:
        """Render the current simulation description."""

        state = self._current_state

        if state is None:
            description = "No active simulation."
        else:
            description = state.description

        text = self.small_font.render(
            description,
            True,
            (220, 220, 220),
        )

        self.surface.blit(
            text,
            (380, 665),
        )

    def _display_values(self) -> tuple[object, ...] | list[object]:
        """Return values from the simulation or actual heap."""

        state = self._current_state

        if state is not None:
            return state.values

        return self.heap.values