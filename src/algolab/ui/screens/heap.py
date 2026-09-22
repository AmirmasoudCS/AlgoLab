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
from algolab.ui.components.surface import draw_arrow, draw_item_card, draw_panel, draw_toggle_button
from algolab.ui.screens.screen import Screen
from algolab.ui.theme import Color, Font


class HeapScreen(Screen):
    """Heap visualization screen."""

    def __init__(self, surface: pygame.Surface, on_back=None) -> None:
        super().__init__(surface, on_back)

        self.model = Heap[int](HeapType.MIN)
        self.simulator = Simulator()
        self.heap_simulator = HeapSimulator(self.model)

        self.current_simulation: HeapSimulation | None = None
        self.operation_committed = False

        self.status_message: str | None = None

        self.control_font = Font.H1()
        self.section_font = Font.H2()
        self.node_font = Font.NODE()
        self.small_font = Font.SMALL()
        self.explanation_font = Font.BODY()
        self.edge_font = Font.LABEL()

        self.heap_type_buttons = self._create_heap_type_buttons()
        self.operation_buttons = self._create_operation_buttons()
        self.navigation_buttons = self._create_navigation_buttons()

        for index, button in enumerate(self.speed_buttons):
            button.rect = pygame.Rect(15 + index * 62, 556, 58, 28)

        self.value_input = NumericInput(
            pygame.Rect(135, 445, 75, 30),
            50,
        )

        self.step_timer = 0.0
        self.step_interval = 1.8

    # ------------------------------------------------------------------
    # UI creation
    # ------------------------------------------------------------------

    def _create_operation_buttons(self) -> list[Button]:
        labels = ["Insert", "Peek", "Extract", "Build Heap", "Clear"]
        variants = ["primary", "default", "danger", "default", "danger"]

        buttons = []

        x = 25
        y = 235
        width = 220
        height = 34
        spacing = 38

        for index, (label, variant) in enumerate(zip(labels, variants)):
            buttons.append(
                Button(
                    pygame.Rect(
                        x,
                        y + index * spacing,
                        width,
                        height,
                    ),
                    label,
                    variant=variant,
                )
            )

        return buttons

    def _create_navigation_buttons(self) -> list[Button]:
        labels = ["|<", "<", ">", ">|", "P"]

        buttons = []

        x = 25
        y = 594
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
            Button(pygame.Rect(15, 145, 110, 34), "Min Heap"),
            Button(pygame.Rect(130, 145, 105, 34), "Max Heap"),
        ]

    # ------------------------------------------------------------------
    # Event handling
    # ------------------------------------------------------------------

    def handle_event(self, event: pygame.event.Event) -> None:
        if self.handle_back_event(event):
            return

        if self.handle_speed_event(event):
            return

        self.value_input.handle_event(event)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                self._handle_navigation(4)
                return
            if event.key == pygame.K_LEFT:
                self._handle_navigation(1)
                return
            if event.key == pygame.K_RIGHT:
                self._handle_navigation(2)
                return
            if event.key == pygame.K_RETURN:
                self._select_operation(0)
                return

        for index, button in enumerate(self.operation_buttons):
            if button.handle_event(event):
                self._select_operation(index)

        for index, button in enumerate(self.navigation_buttons):
            if button.handle_event(event):
                self._handle_navigation(index)

        if self.heap_type_buttons[0].handle_event(event):
            self._set_heap_type(HeapType.MIN)

        if self.heap_type_buttons[1].handle_event(event):
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
                simulation = self.heap_simulator.insert(self.value_input.value)
            elif index == 1:
                simulation = self.heap_simulator.peek()
            elif index == 2:
                simulation = self.heap_simulator.extract()
            elif index == 3:
                simulation = self.heap_simulator.build_heap(self.model.values)
            elif index == 4:
                simulation = self.heap_simulator.clear()
            else:
                return
        except IndexError:
            return

        self.current_simulation = simulation
        self.operation_committed = False
        self.status_message = None

        self.simulator.load_states(list(simulation.states))

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
            self.status_message = final_state.data.description

        self.current_simulation.commit(self.model)

        self.operation_committed = True
        self.current_simulation = None

        self.simulator.reset()

    def update(self, dt: float) -> None:
        self.update_back_button(dt)
        self.update_speed_buttons(dt)

        for button in self.operation_buttons:
            button.update(dt)

        for button in self.navigation_buttons:
            button.update(dt)

        for button in self.heap_type_buttons:
            button.update(dt)

        if self.current_simulation is None:
            return

        if not self.simulator.running:
            return

        if self.simulator.is_at_end:
            self.simulator.pause()
            self._commit_if_finished()
            return

        self.step_timer += dt

        if self.step_timer >= self.scaled_interval(self.step_interval):
            self.step_timer = 0.0

            self.simulator.next()

            self._commit_if_finished()

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------

    def render(self) -> None:
        self.surface.fill(Color.BG)

        self.render_back_button()
        self._render_control_panel()
        self._render_explanation_panel()
        self._render_heap()

    def _render_control_panel(self) -> None:
        panel_rect = pygame.Rect(10, 70, 250, 620)
        draw_panel(self.surface, panel_rect, elevated=True)

        self._draw_text("TA Controls", self.control_font, (25, 80))

        self._draw_text(
            "Heap Type",
            self.section_font,
            (25, 105),
            color=Color.TEXT_SECONDARY,
        )

        self._render_heap_type_button(
            self.heap_type_buttons[0],
            self.model.heap_type is HeapType.MIN,
        )

        self._render_heap_type_button(
            self.heap_type_buttons[1],
            self.model.heap_type is HeapType.MAX,
        )

        self._draw_text(
            "Operations",
            self.section_font,
            (25, 195),
            color=Color.TEXT_SECONDARY,
        )

        for button in self.operation_buttons:
            button.render(self.surface)

        self._draw_text("Value:", self.control_font, (25, 445))

        self.value_input.render(self.surface)

        self._draw_text(
            "Simulation",
            self.section_font,
            (25, 530),
            color=Color.TEXT_SECONDARY,
        )

        self.render_speed_buttons()

        for index, button in enumerate(self.navigation_buttons):
            if index == 4:
                draw_toggle_button(
                    self.surface,
                    button,
                    self.current_simulation is not None
                    and not self.simulator.running,
                )
            else:
                button.render(self.surface)

        if self.current_simulation is None:
            step_text = "Step: -"
        else:
            current_index = self.simulator.history._current_index
            total_steps = len(self.current_simulation.states)

            step_text = f"Step: {current_index + 1} / {total_steps}"

        self._draw_text(
            step_text,
            self.small_font,
            (25, 634),
            color=Color.TEXT_MUTED,
        )

    def _render_heap_type_button(
        self,
        button: Button,
        selected: bool,
    ) -> None:
        """Render a heap type button with selected-state highlighting."""

        if selected:
            background = Color.ACCENT_SOFT
            border_color = Color.ACCENT
        else:
            mouse_position = pygame.mouse.get_pos()

            if button.rect.collidepoint(mouse_position):
                background = Color.SURFACE_RAISED
            else:
                background = Color.SURFACE

            border_color = Color.BORDER

        pygame.draw.rect(self.surface, background, button.rect, border_radius=8)
        pygame.draw.rect(self.surface, border_color, button.rect, 2, border_radius=8)

        text_color = Color.TEXT_PRIMARY if selected else Color.TEXT_SECONDARY
        text = button.font.render(button.label, True, text_color)
        text_rect = text.get_rect(center=button.rect.center)

        self.surface.blit(text, text_rect)

    def _render_explanation_panel(self) -> None:
        panel_rect = pygame.Rect(
            280,
            70,
            self.surface.get_width() - 300,
            130,
        )

        draw_panel(self.surface, panel_rect, elevated=False)

        self._draw_text(
            "What is happening?",
            self.section_font,
            (295, 82),
            color=Color.TEXT_SECONDARY,
        )

        state = self.simulator.state

        if state is not None:
            description = state.data.description
        elif self.status_message is not None:
            description = self.status_message
        else:
            description = "Select an operation to start a simulation."

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
            self._draw_empty_heap_message()
            return

        events = self._get_events()

        compared_indices = set()
        swapped_indices = set()
        created_index = None
        extracted_index = None
        current_index = None

        for event in events:
            if isinstance(event, CompareHeapElementsEvent):
                compared_indices.add(event.first_index)
                compared_indices.add(event.second_index)
                current_index = event.first_index
            elif isinstance(event, SwapHeapElementsEvent):
                swapped_indices.add(event.first_index)
                swapped_indices.add(event.second_index)
            elif isinstance(event, CreateHeapElementEvent):
                created_index = event.index
                current_index = event.index
            elif isinstance(event, ExtractHeapElementEvent):
                extracted_index = event.index
            elif isinstance(event, MoveLastElementEvent):
                current_index = event.to_index

        # The create state intentionally contains the old values,
        # because the simulation separates creation from insertion
        # into the heap array. Add the created value only for display.
        display_values = list(values)

        state = self._get_simulation_state()

        if (
            state is not None
            and created_index is not None
            and created_index == len(display_values)
            and state.created_value is not None
        ):
            display_values.append(state.created_value)

        positions = self._calculate_positions(len(display_values))

        self._render_heap_edges(len(display_values), positions)

        for index, value in enumerate(display_values):
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
            display_values,
            compared_indices,
            swapped_indices,
            created_index,
            extracted_index,
            current_index,
        )

    def _draw_empty_heap_message(self) -> None:
        area = pygame.Rect(280, 220, self.surface.get_width() - 300, 120)

        text = self.explanation_font.render(
            "Heap is empty. Insert a value to begin.",
            True,
            Color.TEXT_MUTED,
        )

        self.surface.blit(text, text.get_rect(center=area.center))

    def _calculate_positions(self, size: int) -> dict[int, pygame.Rect]:
        """
        Compute a screen rect for every heap index.

        Each index is given a horizontal "slot" based on where it would
        sit in a completely full binary tree of the same depth, not
        based on how many siblings currently exist at that depth. This
        is what keeps a lone node correctly centered under its actual
        parent (e.g. a single left child stays under the left half of
        its parent) instead of drifting to the middle of the whole
        canvas whenever it happens to be the only node at its depth.
        """

        positions = {}

        if size == 0:
            return positions

        node_width = 80
        node_height = 55
        level_height = 85

        left = 330
        right = self.surface.get_width() - 25

        available_width = right - left

        for index in range(size):
            depth = (index + 1).bit_length() - 1
            slots_at_depth = 1 << depth
            position_in_level = index - (slots_at_depth - 1)

            slot_width = available_width / slots_at_depth
            center_x = left + (position_in_level + 0.5) * slot_width

            y = 245 + depth * level_height

            positions[index] = pygame.Rect(
                int(center_x - node_width / 2),
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
                self._draw_heap_edge(parent_rect, positions[left_index])

            if right_index < size:
                self._draw_heap_edge(parent_rect, positions[right_index])

    def _draw_heap_edge(self, source: pygame.Rect, target: pygame.Rect) -> None:
        start = (source.centerx, source.bottom)
        end = (target.centerx, target.top)

        draw_arrow(self.surface, start, end, Color.BORDER, width=2)

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
        background = Color.STATE_DEFAULT

        # Later checks intentionally override earlier ones, since a
        # single node can match multiple conditions in one step and the
        # most specific/important one should win.
        if compared:
            background = Color.STATE_COMPARING

        if swapped:
            background = Color.STATE_REPLACE

        if current:
            background = Color.STATE_ACTIVE

        if created:
            background = Color.STATE_SUCCESS

        if extracted:
            background = Color.STATE_DANGER

        draw_item_card(
            self.surface,
            rect,
            background,
            self.node_font,
            value,
            caption_font=self.edge_font,
            caption=f"index {index}",
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
            Color.TEXT_SECONDARY,
        )

        self.surface.blit(label, (300, 500))

        x = 300
        y = 530

        cell_width = 60
        cell_height = 42
        spacing = 8

        for index, value in enumerate(values):
            background = Color.SURFACE_RAISED

            if index in compared_indices:
                background = Color.STATE_COMPARING

            if index in swapped_indices:
                background = Color.STATE_REPLACE

            if index == current_index:
                background = Color.STATE_ACTIVE

            if index == created_index:
                background = Color.STATE_SUCCESS

            if index == extracted_index:
                background = Color.STATE_DANGER

            rect = pygame.Rect(x, y, cell_width, cell_height)

            draw_item_card(
                self.surface,
                rect,
                background,
                self.small_font,
                value,
                caption_font=self.edge_font,
                caption=str(index),
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
        font: pygame.font.Font,
        position: tuple[int, int],
        color: tuple[int, int, int] = Color.TEXT_PRIMARY,
    ) -> None:
        rendered_text = font.render(text, True, color)
        self.surface.blit(rendered_text, position)

    def _draw_wrapped_text(
        self,
        text: str,
        rect: pygame.Rect,
        font: pygame.font.Font,
        color: tuple[int, int, int] = Color.TEXT_SECONDARY,
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

            rendered_text = font.render(line, True, color)
            self.surface.blit(rendered_text, (rect.x, y))

            y += line_height