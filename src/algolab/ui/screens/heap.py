from __future__ import annotations

import pygame

from algolab.simulation.simulator import Simulator
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
    """Heap visualization screen."""

    def __init__(self, surface: pygame.Surface) -> None:
        super().__init__(surface)

        self.model = Heap[int](HeapType.MIN)
        self.simulator = Simulator()
        self.heap_simulator = HeapSimulator(self.model)

        self.current_simulation: HeapSimulation | None = None
        self.operation_committed = False

        self.status_message: str | None = None

        self.control_font = pygame.font.Font(None, 30)
        self.section_font = pygame.font.Font(None, 24)
        self.node_font = pygame.font.Font(None, 28)
        self.small_font = pygame.font.Font(None, 22)
        self.explanation_font = pygame.font.Font(None, 25)
        self.edge_font = pygame.font.Font(None, 18)

        self.operation_buttons = (
            self._create_operation_buttons()
        )

        self.navigation_buttons = (
            self._create_navigation_buttons()
        )

        self.value_input = NumericInput(
            pygame.Rect(135, 405, 75, 30),
            50,
        )

        self.step_timer = 0.0
        self.step_interval = 1.8

    # ------------------------------------------------------------------
    # UI creation
    # ------------------------------------------------------------------

    def _create_operation_buttons(self) -> list[Button]:
        labels = [
            "Insert",
            "Peek",
            "Extract",
            "Build Heap",
            "Clear",
        ]

        buttons = []

        x = 25
        y = 195
        width = 220
        height = 34
        spacing = 38

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
        y = 530
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

    def _create_heap_type_buttons(self) -> list[Button]:
        return [
            Button(
                pygame.Rect(15, 115, 110, 34),
                "Min Heap",
            ),
            Button(
                pygame.Rect(130, 115, 105, 34),
                "Max Heap",
            ),
        ]

    # ------------------------------------------------------------------
    # Event handling
    # ------------------------------------------------------------------

    def handle_event(self, event: pygame.event.Event) -> None:
        self.value_input.handle_event(event)

        for index, button in enumerate(
            self.operation_buttons
        ):
            if button.handle_event(event):
                self._select_operation(index)

        for index, button in enumerate(
            self.navigation_buttons
        ):
            if button.handle_event(event):
                self._handle_navigation(index)

        if hasattr(self, "min_heap_button"):
            if self.min_heap_button.handle_event(event):
                self._set_heap_type(HeapType.MIN)

            if self.max_heap_button.handle_event(event):
                self._set_heap_type(HeapType.MAX)

    def _set_heap_type(self, heap_type: HeapType) -> None:
        """Change heap type and reset the current heap."""

        if self.model.heap_type is heap_type:
            return

        if self.current_simulation is not None:
            return

        self.model = Heap[int](heap_type)
        self.heap_simulator = HeapSimulator(self.model)

        self.status_message = None

    def _select_operation(self, index: int) -> None:
        if self.current_simulation is not None:
            return

        try:
            if index == 0:
                simulation = self.heap_simulator.insert(
                    self.value_input.value
                )

            elif index == 1:
                simulation = self.heap_simulator.peek()

            elif index == 2:
                simulation = self.heap_simulator.extract()

            elif index == 3:
                simulation = self.heap_simulator.build_heap(
                    self.model.values
                )

            elif index == 4:
                simulation = self.heap_simulator.clear()

            else:
                return

        except IndexError:
            return

        self.current_simulation = simulation
        self.operation_committed = False
        self.status_message = None

        self.simulator.load_states(
            list(simulation.states)
        )

        self.step_timer = 0.0

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------

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

        final_state = self.simulator.state

        if final_state is not None:
            self.status_message = (
                final_state.data.description
            )

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

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------

    def render(self) -> None:
        self.surface.fill((30, 30, 30))

        self._render_control_panel()
        self._render_explanation_panel()
        self._render_heap()

    def _render_control_panel(self) -> None:
        pygame.draw.rect(
            self.surface,
            (40, 40, 40),
            pygame.Rect(10, 70, 250, 620),
            border_radius=8,
        )

        self._draw_text(
            "TA Controls",
            self.control_font,
            (25, 80),
        )

        # Heap type
        self._draw_text(
            "Heap Type",
            self.section_font,
            (25, 115),
        )

        for button in self.heap_type_buttons:
            button.render(self.surface)

        # Operations
        self._draw_text(
            "Operations",
            self.section_font,
            (25, 165),
        )

        for button in self.operation_buttons:
            button.render(self.surface)

        # Value input
        self._draw_text(
            "Value:",
            self.control_font,
            (25, 405),
        )

        self.value_input.render(self.surface)

        # Simulation
        self._draw_text(
            "Simulation",
            self.section_font,
            (25, 490),
        )

        for button in self.navigation_buttons:
            button.render(self.surface)

        self._draw_text(
            f"Step: {self.simulator.current_index + 1} / "
            f"{len(self.simulator.states)}",
            self.small_font,
            (25, 570),
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

        if state is not None:
            description = state.data.description

        elif self.status_message is not None:
            description = self.status_message

        else:
            description = (
                "Select an operation to start a simulation."
            )

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

    # ------------------------------------------------------------------
    # Heap visualization
    # ------------------------------------------------------------------

    def _get_simulation_state(self):
        if self.simulator.state is None:
            return None

        return self.simulator.state.data

    def _get_events(self):
        if self.simulator.state is None:
            return ()

        return self.simulator.state.events

    def _get_display_values(self):
        state = self._get_simulation_state()

        if state is not None:
            return state.values

        return self.model.values

    def _render_heap(self) -> None:
        values = self._get_display_values()

        if not values:
            self._draw_text(
                "Heap is empty.",
                (600, 350),
                self.explanation_font,
            )
            return

        events = self._get_events()

        compared_indices = set()
        swapped_indices = set()
        created_index = None
        extracted_index = None
        current_index = None

        for event in events:
            if isinstance(
                event,
                CompareHeapElementsEvent,
            ):
                compared_indices.add(
                    event.first_index
                )
                compared_indices.add(
                    event.second_index
                )

                current_index = (
                    event.first_index
                )

            elif isinstance(
                event,
                SwapHeapElementsEvent,
            ):
                swapped_indices.add(
                    event.first_index
                )
                swapped_indices.add(
                    event.second_index
                )

            elif isinstance(
                event,
                CreateHeapElementEvent,
            ):
                created_index = event.index
                current_index = event.index

            elif isinstance(
                event,
                ExtractHeapElementEvent,
            ):
                extracted_index = event.index

            elif isinstance(
                event,
                MoveLastElementEvent,
            ):
                current_index = event.to_index

        positions = self._calculate_positions(
            len(values)
        )

        self._render_heap_edges(
            len(values),
            positions,
        )

        for index, value in enumerate(values):
            self._render_heap_node(
                index=index,
                value=value,
                rect=positions[index],
                compared=index in compared_indices,
                swapped=index in swapped_indices,
                created=index == created_index,
                extracted=index == extracted_index,
                current=index == current_index,
            )

        self._render_array(
            values,
            compared_indices,
            swapped_indices,
            created_index,
            extracted_index,
            current_index,
        )

    def _calculate_positions(
        self,
        size: int,
    ) -> dict[int, pygame.Rect]:
        positions = {}

        node_width = 80
        node_height = 55
        horizontal_spacing = 25
        level_height = 85

        left = 330
        right = self.surface.get_width() - 25

        available_width = right - left

        levels = []

        for index in range(size):
            level = index.bit_length() - 1

            while len(levels) <= level:
                levels.append([])

            levels[level].append(index)

        for level, indices in enumerate(levels):
            count = len(indices)

            if count == 1:
                x_positions = [
                    left
                    + available_width // 2
                    - node_width // 2
                ]

            else:
                spacing = min(
                    node_width + horizontal_spacing,
                    available_width / (count - 1),
                )

                total_width = (
                    (count - 1) * spacing
                    + node_width
                )

                start_x = (
                    left
                    + (available_width - total_width)
                    / 2
                )

                x_positions = [
                    start_x + position * spacing
                    for position in range(count)
                ]

            y = 245 + level * level_height

            for index, x in zip(
                indices,
                x_positions,
            ):
                positions[index] = pygame.Rect(
                    int(x),
                    int(y),
                    node_width,
                    node_height,
                )

        return positions

    def _render_heap_edges(
        self,
        size: int,
        positions: dict[int, pygame.Rect],
    ) -> None:
        for index in range(size):
            parent_rect = positions[index]

            left_index = 2 * index + 1
            right_index = 2 * index + 2

            if left_index < size:
                self._draw_heap_edge(
                    parent_rect,
                    positions[left_index],
                )

            if right_index < size:
                self._draw_heap_edge(
                    parent_rect,
                    positions[right_index],
                )

    def _draw_heap_edge(
        self,
        source: pygame.Rect,
        target: pygame.Rect,
    ) -> None:
        start = (
            source.centerx,
            source.bottom,
        )

        end = (
            target.centerx,
            target.top,
        )

        pygame.draw.line(
            self.surface,
            (150, 180, 210),
            start,
            end,
            3,
        )

        self._draw_arrow_head(
            end,
            (150, 180, 210),
        )

    def _draw_arrow_head(
        self,
        position: tuple[int, int],
        color: tuple[int, int, int],
    ) -> None:
        x, y = position
        size = 7

        points = [
            (x, y),
            (x - size, y - size),
            (x + size, y - size),
        ]

        pygame.draw.polygon(
            self.surface,
            color,
            points,
        )

    def _render_heap_node(
        self,
        index: int,
        value,
        rect: pygame.Rect,
        compared: bool,
        swapped: bool,
        created: bool,
        extracted: bool,
        current: bool,
    ) -> None:
        background = (65, 85, 115)
        border_color = (210, 210, 210)

        if compared:
            background = (180, 135, 55)
            border_color = (255, 215, 90)

        if swapped:
            background = (150, 100, 60)

        if current:
            background = (70, 110, 180)

        if created:
            background = (65, 150, 105)

        if extracted:
            background = (165, 75, 75)

        pygame.draw.rect(
            self.surface,
            background,
            rect,
            border_radius=8,
        )

        pygame.draw.rect(
            self.surface,
            border_color,
            rect,
            2,
            border_radius=8,
        )

        value_text = self.node_font.render(
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

        index_text = self.edge_font.render(
            f"index {index}",
            True,
            (190, 190, 190),
        )

        index_rect = index_text.get_rect(
            centerx=rect.centerx,
            top=rect.bottom + 4,
        )

        self.surface.blit(
            index_text,
            index_rect,
        )

    # ------------------------------------------------------------------
    # Array representation
    # ------------------------------------------------------------------

    def _render_array(
        self,
        values,
        compared_indices,
        swapped_indices,
        created_index,
        extracted_index,
        current_index,
    ) -> None:
        label = self.section_font.render(
            "Array representation",
            True,
            (235, 235, 235),
        )

        self.surface.blit(
            label,
            (300, 500),
        )

        x = 300
        y = 530

        cell_width = 60
        cell_height = 42
        spacing = 8

        for index, value in enumerate(values):
            rect = pygame.Rect(
                x,
                y,
                cell_width,
                cell_height,
            )

            border_color = (100, 100, 100)
            background = (40, 40, 40)

            if index in compared_indices:
                background = (110, 85, 40)
                border_color = (255, 215, 90)

            if index in swapped_indices:
                background = (110, 75, 45)

            if index == current_index:
                background = (60, 95, 130)

            if index == created_index:
                background = (55, 120, 85)

            if index == extracted_index:
                background = (125, 60, 60)

            pygame.draw.rect(
                self.surface,
                background,
                rect,
                border_radius=5,
            )

            pygame.draw.rect(
                self.surface,
                border_color,
                rect,
                2,
                border_radius=5,
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

            index_text = self.edge_font.render(
                str(index),
                True,
                (170, 170, 170),
            )

            index_rect = index_text.get_rect(
                centerx=rect.centerx,
                top=rect.bottom + 3,
            )

            self.surface.blit(
                index_text,
                index_rect,
            )

            x += cell_width + spacing

            if x + cell_width > self.surface.get_width():
                break

    # ------------------------------------------------------------------
    # Text helpers
    # ------------------------------------------------------------------

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