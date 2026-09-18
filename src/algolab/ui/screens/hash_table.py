from __future__ import annotations

import pygame

from algolab.simulation.simulator import Simulator
from algolab.topics.hash_table.model import CollisionStrategy, HashTable, HashTableMode
from algolab.topics.hash_table.simulation import HashTableSimulator
from algolab.ui.components.button import Button
from algolab.ui.components.numeric_input import NumericInput
from algolab.ui.components.surface import (
    draw_arrow,
    draw_item_card,
    draw_panel,
    draw_toggle_button,
)
from algolab.ui.screens.screen import Screen
from algolab.ui.theme import Color, Font


class HashTableScreen(Screen):
    """Screen for visualizing hash table insert/search/delete."""

    def __init__(self, surface: pygame.Surface, on_back=None) -> None:
        super().__init__(surface, on_back)

        self.model = HashTable(
            capacity=11,
            collision_strategy=CollisionStrategy.CHAINING,
            mode=HashTableMode.SET,
        )
        self.simulator = Simulator()
        self.hash_simulator = HashTableSimulator(self.model)

        self.current_simulation = None
        self.operation_committed = False
        self.status_message: str | None = None
        self.error_message: str | None = None

        self.control_font = Font.H1()
        self.section_font = Font.H2()
        self.entry_font = Font.get(18, bold=True)
        self.small_font = Font.SMALL()
        self.explanation_font = Font.BODY()
        self.label_font = Font.LABEL()

        self.strategy_buttons = [
            Button(pygame.Rect(15, 148, 110, 34), "Chaining"),
            Button(pygame.Rect(130, 148, 105, 34), "Linear Probing"),
        ]

        self.mode_buttons = [
            Button(pygame.Rect(15, 246, 110, 34), "Set"),
            Button(pygame.Rect(130, 246, 105, 34), "Map"),
        ]

        self.capacity_input = NumericInput(pygame.Rect(160, 301, 75, 30), 11)
        self.key_input = NumericInput(pygame.Rect(160, 335, 75, 30), 1)
        self.value_input = NumericInput(pygame.Rect(160, 369, 75, 30), 1)

        self.operation_buttons = self._create_operation_buttons()
        self.navigation_buttons = self._create_navigation_buttons()

        self.step_timer = 0.0
        self.step_interval = 1.6

    # ------------------------------------------------------------------
    # UI creation
    # ------------------------------------------------------------------

    def _create_operation_buttons(self) -> list[Button]:
        labels = ["Insert", "Search", "Delete", "Clear"]
        variants = ["primary", "default", "danger", "danger"]

        buttons = []
        y = 424

        for label, variant in zip(labels, variants):
            buttons.append(
                Button(pygame.Rect(15, y, 220, 34), label, variant=variant)
            )
            y += 36

        return buttons

    def _create_navigation_buttons(self) -> list[Button]:
        labels = ["|<", "<", ">", ">|", "P"]

        buttons = []
        x = 15
        y = 624
        width = 40
        height = 35
        spacing = 45

        for index, label in enumerate(labels):
            buttons.append(
                Button(pygame.Rect(x + index * spacing, y, width, height), label)
            )

        return buttons

    # ------------------------------------------------------------------
    # Event handling
    # ------------------------------------------------------------------

    def handle_event(self, event: pygame.event.Event) -> None:
        if self.handle_back_event(event):
            return

        self.key_input.handle_event(event)

        if self.model.mode is HashTableMode.MAP:
            self.value_input.handle_event(event)

        for index, button in enumerate(self.strategy_buttons):
            if button.handle_event(event):
                self._set_strategy(index == 1)

        for index, button in enumerate(self.mode_buttons):
            if button.handle_event(event):
                self._set_mode(index == 1)

        new_capacity = self.capacity_input.handle_event(event)

        if new_capacity is not None:
            self._set_capacity(new_capacity)

        for index, button in enumerate(self.operation_buttons):
            if button.handle_event(event):
                self._select_operation(index)

        for index, button in enumerate(self.navigation_buttons):
            if button.handle_event(event):
                self._handle_navigation(index)

    def _set_strategy(self, use_probing: bool) -> None:
        if self.current_simulation is not None:
            return

        strategy = (
            CollisionStrategy.LINEAR_PROBING
            if use_probing
            else CollisionStrategy.CHAINING
        )

        self.model.set_collision_strategy(strategy)

        self.status_message = None
        self.error_message = None

    def _set_mode(self, use_map: bool) -> None:
        if self.current_simulation is not None:
            return

        mode = HashTableMode.MAP if use_map else HashTableMode.SET
        self.model.set_mode(mode)

        self.status_message = None
        self.error_message = None

    def _set_capacity(self, capacity: int) -> None:
        if self.current_simulation is not None:
            return

        try:
            self.model.set_capacity(capacity)
        except ValueError as error:
            self.error_message = str(error)
            return

        self.status_message = None
        self.error_message = None

    def _select_operation(self, index: int) -> None:
        if self.current_simulation is not None:
            return

        key = self.key_input.value
        value = self.value_input.value if self.model.mode is HashTableMode.MAP else None

        try:
            if index == 0:
                simulation = self.hash_simulator.insert(key, value)
            elif index == 1:
                simulation = self.hash_simulator.search(key)
            elif index == 2:
                simulation = self.hash_simulator.delete(key)
            elif index == 3:
                self._clear_table()
                return
            else:
                return
        except IndexError as error:
            self.error_message = str(error)
            return

        self.current_simulation = simulation
        self.operation_committed = False
        self.status_message = None
        self.error_message = None

        self.simulator.load_states(list(simulation.states))

        self.step_timer = 0.0

    def _clear_table(self) -> None:
        self.model.clear()
        self.status_message = None
        self.error_message = None

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

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    def update(self, dt: float) -> None:
        self.update_back_button(dt)

        for button in self.strategy_buttons:
            button.update(dt)

        for button in self.mode_buttons:
            button.update(dt)

        for button in self.operation_buttons:
            button.update(dt)

        for button in self.navigation_buttons:
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

        if self.step_timer >= self.step_interval:
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
        self._render_table()

    def _draw_text(
        self,
        text: str,
        position: tuple[int, int],
        font: pygame.font.Font,
        color: tuple[int, int, int] = Color.TEXT_PRIMARY,
    ) -> None:
        rendered = font.render(text, True, color)
        self.surface.blit(rendered, position)

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
            test_line = word if not current_line else f"{current_line} {word}"

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

            rendered = font.render(line, True, color)
            self.surface.blit(rendered, (rect.x, y))

            y += line_height

    def _render_control_panel(self) -> None:
        panel_rect = pygame.Rect(10, 70, 250, 630)
        draw_panel(self.surface, panel_rect, elevated=True)

        self._draw_text("TA Controls", (25, 80), self.control_font)

        self._draw_text(
            "Collision Strategy",
            (25, 112),
            self.section_font,
            color=Color.TEXT_SECONDARY,
        )

        for index, button in enumerate(self.strategy_buttons):
            is_on = (index == 1) == (
                self.model.collision_strategy is CollisionStrategy.LINEAR_PROBING
            )
            draw_toggle_button(self.surface, button, is_on)

        self._draw_text(
            "Mode",
            (25, 210),
            self.section_font,
            color=Color.TEXT_SECONDARY,
        )

        for index, button in enumerate(self.mode_buttons):
            is_on = (index == 1) == (self.model.mode is HashTableMode.MAP)
            draw_toggle_button(self.surface, button, is_on)

        self._draw_text(
            "Capacity:",
            (15, 306),
            self.small_font,
            color=Color.TEXT_SECONDARY,
        )
        self.capacity_input.render(self.surface)

        self._draw_text(
            "Key:",
            (15, 340),
            self.small_font,
            color=Color.TEXT_SECONDARY,
        )
        self.key_input.render(self.surface)

        self._draw_text(
            "Value:",
            (15, 374),
            self.small_font,
            color=Color.TEXT_SECONDARY,
        )

        if self.model.mode is HashTableMode.MAP:
            self.value_input.render(self.surface)
        else:
            self._draw_text(
                "N/A (Set mode)",
                (160, 374),
                self.small_font,
                color=Color.TEXT_MUTED,
            )

        for button in self.operation_buttons:
            button.render(self.surface)

        self._draw_text(
            "Simulation",
            (25, 590),
            self.section_font,
            color=Color.TEXT_SECONDARY,
        )

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

        status_area = pygame.Rect(15, 605, 220, 16)

        if self.current_simulation is not None:
            state = self.simulator.state

            if state is not None:
                self._draw_text(
                    (
                        f"Step: {state.step + 1}/"
                        f"{len(self.current_simulation.states)}"
                    ),
                    (status_area.x, status_area.y),
                    self.small_font,
                    color=Color.TEXT_MUTED,
                )
        else:
            info = (
                f"Size: {self.model.size}/{self.model.capacity}  "
                f"Load: {self.model.load_factor:.2f}"
            )

            self._draw_text(
                info,
                (status_area.x, status_area.y),
                self.small_font,
                color=Color.TEXT_MUTED,
            )

        if self.error_message is not None:
            error_area = pygame.Rect(280, self.surface.get_height() - 40, self.surface.get_width() - 300, 30)
            self._draw_wrapped_text(
                self.error_message, error_area, self.small_font, Color.STATE_DANGER
            )

    def _render_explanation_panel(self) -> None:
        panel_rect = pygame.Rect(280, 70, self.surface.get_width() - 300, 130)
        draw_panel(self.surface, panel_rect, elevated=False)

        self._draw_text(
            "What is happening?",
            (295, 82),
            self.section_font,
            color=Color.TEXT_SECONDARY,
        )

        state = self._get_state()

        if state is not None:
            description = state.description
        elif self.status_message is not None:
            description = self.status_message
        else:
            description = (
                "Enter a key (and value, in Map mode) and choose an "
                "operation to begin."
            )

        description_rect = pygame.Rect(295, 112, panel_rect.width - 30, 75)

        self._draw_wrapped_text(
            description, description_rect, self.explanation_font
        )

    def _get_state(self):
        if self.simulator.state is None:
            return None

        return self.simulator.state.data

    # ------------------------------------------------------------------
    # Table visualization
    # ------------------------------------------------------------------

    def _canvas_rect(self) -> pygame.Rect:
        return pygame.Rect(
            280,
            210,
            self.surface.get_width() - 300,
            self.surface.get_height() - 230,
        )

    def _slot_color(
        self,
        index: int,
        occupied: bool,
        tombstoned: bool,
        state,
    ) -> tuple[int, int, int]:
        if state is not None:
            if index == state.highlighted_index:
                return Color.STATE_ACTIVE

            if index in state.probe_trail:
                return Color.STATE_COMPARING

        if tombstoned:
            return Color.STATE_DANGER

        if occupied:
            return Color.STATE_DEFAULT

        return Color.SURFACE

    def _render_table(self) -> None:
        state = self._get_state()

        if state is not None:
            buckets = state.buckets
            tombstones = state.tombstones
        else:
            buckets = tuple(tuple(bucket) for bucket in self.model.snapshot())
            tombstones = tuple(self.model.tombstones())

        if self.model.collision_strategy is CollisionStrategy.CHAINING:
            self._render_chaining(buckets, state)
        else:
            self._render_probing(buckets, tombstones, state)

    def _render_chaining(self, buckets, state) -> None:
        canvas = self._canvas_rect()

        row_height = min(48, max(30, canvas.height // max(1, len(buckets))))
        index_box_size = 40
        entry_width = 90
        entry_height = min(row_height - 8, 40)
        entry_spacing = 30

        for index, bucket in enumerate(buckets):
            y = canvas.top + index * row_height

            if y + row_height > canvas.bottom:
                break

            index_rect = pygame.Rect(canvas.left, y + (row_height - index_box_size) // 2, index_box_size, index_box_size)

            index_color = Color.STATE_ACTIVE if (
                state is not None and state.highlighted_index == index
            ) else Color.SURFACE_RAISED

            pygame.draw.rect(self.surface, index_color, index_rect, border_radius=8)
            pygame.draw.rect(self.surface, Color.BORDER, index_rect, 2, border_radius=8)

            index_text = self.label_font.render(str(index), True, Color.TEXT_PRIMARY)
            self.surface.blit(index_text, index_text.get_rect(center=index_rect.center))

            if not bucket:
                empty_text = self.small_font.render("empty", True, Color.TEXT_MUTED)
                self.surface.blit(
                    empty_text,
                    (index_rect.right + 16, index_rect.centery - empty_text.get_height() // 2),
                )
                continue

            x = index_rect.right + 16

            for position, entry in enumerate(bucket):
                if x + entry_width > canvas.right:
                    break

                rect = pygame.Rect(x, y + (row_height - entry_height) // 2, entry_width, entry_height)

                label = (
                    f"{entry.key}: {entry.value}"
                    if self.model.mode is HashTableMode.MAP
                    else str(entry.key)
                )

                background = Color.STATE_ACTIVE if (
                    state is not None and state.highlighted_index == index
                ) else Color.STATE_DEFAULT

                draw_item_card(
                    self.surface,
                    rect,
                    background,
                    self.small_font,
                    label,
                )

                if position < len(bucket) - 1:
                    arrow_start = (rect.right, rect.centery)
                    arrow_end = (rect.right + entry_spacing - 6, rect.centery)
                    draw_arrow(self.surface, arrow_start, arrow_end, Color.BORDER, width=2)

                x += entry_width + entry_spacing

    def _render_probing(self, buckets, tombstones, state) -> None:
        canvas = self._canvas_rect()

        slot_width = 70
        slot_height = 55
        spacing = 8

        x = canvas.left
        y = canvas.top

        for index, bucket in enumerate(buckets):
            if x + slot_width > canvas.right:
                x = canvas.left
                y += slot_height + 24

            if y + slot_height > canvas.bottom:
                break

            occupied = bool(bucket)
            tombstoned = tombstones[index] if index < len(tombstones) else False

            color = self._slot_color(index, occupied, tombstoned, state)

            rect = pygame.Rect(x, y, slot_width, slot_height)

            if occupied:
                entry = bucket[0]
                label = (
                    f"{entry.key}:{entry.value}"
                    if self.model.mode is HashTableMode.MAP
                    else str(entry.key)
                )

                draw_item_card(
                    self.surface,
                    rect,
                    color,
                    self.small_font,
                    label,
                    caption_font=self.label_font,
                    caption=str(index),
                )
            else:
                pygame.draw.rect(self.surface, color, rect, border_radius=8)
                pygame.draw.rect(self.surface, Color.BORDER, rect, 2, border_radius=8)

                text = self.label_font.render(
                    "deleted" if tombstoned else "empty",
                    True,
                    Color.TEXT_MUTED,
                )
                self.surface.blit(text, text.get_rect(center=rect.center))

                index_text = self.label_font.render(str(index), True, Color.TEXT_MUTED)
                index_rect = index_text.get_rect(centerx=rect.centerx, top=rect.bottom + 3)
                self.surface.blit(index_text, index_rect)

            x += slot_width + spacing