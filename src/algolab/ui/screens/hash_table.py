from __future__ import annotations

import random

import pygame

from algolab.simulation.simulator import Simulator
from algolab.topics.hash_table.model import (
    CollisionStrategy,
    HashFunction,
    HashTable,
    HashTableMode,
)
from algolab.topics.hash_table.simulation import HashTableSimulator
from algolab.ui.components.button import Button
from algolab.ui.components.info_panel import InfoPanel
from algolab.ui.components.numeric_input import NumericInput
from algolab.ui.components.storage_controls import StorageControls
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

    STRATEGY_LABELS = {
        CollisionStrategy.CHAINING: "Chaining",
        CollisionStrategy.LINEAR_PROBING: "Linear Probing",
        CollisionStrategy.QUADRATIC_PROBING: "Quadratic Probing",
        CollisionStrategy.DOUBLE_HASHING: "Double Hashing",
    }

    def __init__(self, surface: pygame.Surface, on_back=None) -> None:
        super().__init__(surface, on_back)

        self.model = HashTable(
            capacity=11,
            collision_strategy=CollisionStrategy.CHAINING,
            mode=HashTableMode.SET,
            hash_function=HashFunction.SUM_OF_CODES,
        )
        self.simulator = Simulator()
        self.hash_simulator = HashTableSimulator(self.model)

        self.current_simulation = None
        self.operation_committed = False
        self.status_message: str | None = None
        self.error_message: str | None = None

        self.control_font = Font.H1()
        self.section_font = Font.H2()
        self.small_font = Font.SMALL()
        self.explanation_font = Font.BODY()
        self.label_font = Font.LABEL()

        # A Randomize button occupies its own full-width row directly
        # below the "Collision Strategy" label. Unlike every other
        # topic screen, there was no spare horizontal space next to an
        # existing label here (the strategy grid starts immediately
        # below it), so this row was inserted instead, and every rect
        # and text position from here down is shifted by ROW_SHIFT
        # (38px, matching the existing spacing between the two
        # strategy button rows) to make room.
        ROW_SHIFT = 38

        self.randomize_button = Button(
            pygame.Rect(15, 148, 220, 34),
            "Randomize",
            variant="primary",
        )

        self.info_button = Button(
            pygame.Rect(surface.get_width() - 115, 15, 100, 38),
            "Info",
        )
        self.info_panel = InfoPanel(
            "Hash Table - Time Complexity",
            [
                ("Insert", "O(1) avg", "O(n) worst (many collisions)"),
                ("Search", "O(1) avg", "O(n) worst (many collisions)"),
                ("Delete", "O(1) avg", "O(n) worst (many collisions)"),
            ],
        )

        # Save / Load buttons (left of Info) and their dialog.
        self.storage = StorageControls(
            surface,
            "hash_table",
            "Hash Table",
            capture=self._capture_structure,
            restore=self._restore_structure,
        )

        self.strategy_buttons = {
            CollisionStrategy.CHAINING: Button(pygame.Rect(15, 148 + ROW_SHIFT, 110, 34), "Chaining"),
            CollisionStrategy.LINEAR_PROBING: Button(pygame.Rect(130, 148 + ROW_SHIFT, 105, 34), "Linear Probing"),
            CollisionStrategy.QUADRATIC_PROBING: Button(pygame.Rect(15, 186 + ROW_SHIFT, 110, 34), "Quadratic"),
            CollisionStrategy.DOUBLE_HASHING: Button(pygame.Rect(130, 186 + ROW_SHIFT, 105, 34), "Double Hash"),
        }

        self.hash_function_buttons = {
            HashFunction.SUM_OF_CODES: Button(pygame.Rect(15, 250 + ROW_SHIFT, 110, 34), "Sum of Codes"),
            HashFunction.POLYNOMIAL: Button(pygame.Rect(130, 250 + ROW_SHIFT, 105, 34), "Polynomial"),
        }

        self.mode_buttons = {
            HashTableMode.SET: Button(pygame.Rect(15, 314 + ROW_SHIFT, 110, 34), "Set"),
            HashTableMode.MAP: Button(pygame.Rect(130, 314 + ROW_SHIFT, 105, 34), "Map"),
        }

        self.capacity_input = NumericInput(pygame.Rect(160, 348 + ROW_SHIFT, 75, 30), 11)
        self.key_input = NumericInput(pygame.Rect(160, 382 + ROW_SHIFT, 75, 30), 1)
        self.value_input = NumericInput(pygame.Rect(160, 416 + ROW_SHIFT, 75, 30), 1)

        self.operation_buttons = self._create_operation_buttons(ROW_SHIFT)
        self.navigation_buttons = self._create_navigation_buttons(ROW_SHIFT)

        for index, button in enumerate(self.speed_buttons):
            button.rect = pygame.Rect(15 + index * 62, 614 + ROW_SHIFT, 58, 28)

        self._row_shift = ROW_SHIFT

        self.step_timer = 0.0
        self.step_interval = 1.6

    # ------------------------------------------------------------------
    # UI creation
    # ------------------------------------------------------------------

    def _create_operation_buttons(self, row_shift: int) -> list[Button]:
        specs = [
            ("Insert", "primary", 15, 490 + row_shift),
            ("Search", "default", 130, 490 + row_shift),
            ("Delete", "danger", 15, 528 + row_shift),
            ("Clear", "danger", 130, 528 + row_shift),
        ]

        buttons = []

        for label, variant, x, y in specs:
            width = 110 if x == 15 else 105
            buttons.append(Button(pygame.Rect(x, y, width, 34), label, variant=variant))

        return buttons

    def _create_navigation_buttons(self, row_shift: int) -> list[Button]:
        labels = ["|<", "<", ">", ">|", "P"]

        buttons = []
        x = 15
        y = 652 + row_shift
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
        if self.info_panel.handle_event(event):
            return

        if self.storage.handle_event(event):
            return

        if self.handle_back_event(event):
            return

        if self.handle_speed_event(event):
            return

        self.key_input.handle_event(event)

        if self.model.mode is HashTableMode.MAP:
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

        if self.randomize_button.handle_event(event):
            self._randomize()

        if self.info_button.handle_event(event):
            self.info_panel.open()

        for strategy, button in self.strategy_buttons.items():
            if button.handle_event(event):
                self._set_strategy(strategy)

        for hash_function, button in self.hash_function_buttons.items():
            if button.handle_event(event):
                self._set_hash_function(hash_function)

        for mode, button in self.mode_buttons.items():
            if button.handle_event(event):
                self._set_mode(mode)

        new_capacity = self.capacity_input.handle_event(event)

        if new_capacity is not None:
            self._set_capacity(new_capacity)

        for index, button in enumerate(self.operation_buttons):
            if button.handle_event(event):
                self._select_operation(index)

        for index, button in enumerate(self.navigation_buttons):
            if button.handle_event(event):
                self._handle_navigation(index)

    def _cancel_current_simulation(self) -> None:
        """
        Discard any in-progress simulation.

        Settings changes (strategy, hash function, mode, capacity) all
        clear the table anyway, so an in-flight animation of an
        operation on the *old* table no longer means anything. Rather
        than silently refusing the settings change while a simulation
        is active (which looked, from the outside, exactly like the
        control was broken), just cancel it and apply the change.
        """

        if self.current_simulation is not None:
            self.simulator.reset()
            self.current_simulation = None
            self.operation_committed = False

    def _set_strategy(self, strategy: CollisionStrategy) -> None:
        self._cancel_current_simulation()

        self.model.set_collision_strategy(strategy)

        self.status_message = None
        self.error_message = None

    def _set_hash_function(self, hash_function: HashFunction) -> None:
        self._cancel_current_simulation()

        self.model.set_hash_function(hash_function)

        self.status_message = None
        self.error_message = None

    def _set_mode(self, mode: HashTableMode) -> None:
        self._cancel_current_simulation()

        self.model.set_mode(mode)

        self.status_message = None
        self.error_message = None

    def _set_capacity(self, capacity: int) -> None:
        self._cancel_current_simulation()

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

    def _randomize(self) -> None:
        """
        Replace the table contents with random key/value pairs,
        instantly and without animation (same behavior as the sorting
        screen's Randomize).

        Keys are drawn without replacement (random.sample) so a
        repeated key -- which insert() treats as an update rather than
        a new entry -- doesn't silently shrink the table below the
        intended count. Open addressing can still fill up before every
        key is placed, so each insert is guarded with IndexError, the
        same exception _select_operation already handles for a manual
        Insert into a full table.
        """

        self._cancel_current_simulation()

        self.model.clear()

        capacity = self.model.capacity
        count = random.randint(max(3, capacity // 2), max(3, capacity))
        keys = random.sample(range(1, 100), min(count, 99))

        for key in keys:
            value = (
                random.randint(1, 99)
                if self.model.mode is HashTableMode.MAP
                else None
            )

            try:
                self.model.insert(key, value)
            except IndexError:
                break

        self.status_message = None
        self.error_message = None

    # ------------------------------------------------------------------
    # Save / Load
    # ------------------------------------------------------------------

    def _capture_structure(self) -> tuple[str | None, dict]:
        """Current table as (mode, data) for the Save dialog.

        The collision strategy is used as the mode so it shows up in
        suggested file names and in the Load list. The whole layout
        (settings, every slot, tombstones) is in the data.
        """

        return self.model.collision_strategy.value, self.model.to_dict()

    def _restore_structure(self, mode: str | None, data: dict) -> None:
        """Replace the table with loaded data (from the Load dialog).

        HashTable.from_dict() validates everything first (including
        that every key sits where the hash function and strategy would
        look for it) and raises ValueError on bad data, so nothing
        below runs for a bad file. Strategy, hash function, set/map
        mode and capacity all come from the file. The existing model
        object is updated in place because HashTableSimulator holds a
        reference to it.
        """

        loaded = HashTable.from_dict(data)

        self._cancel_current_simulation()

        self.model.replace_with(loaded)
        self.capacity_input.set_value(loaded.capacity)

        self.status_message = None
        self.error_message = None
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

        final_state = self.simulator.state

        if final_state is not None:
            self.status_message = final_state.data.description

        # Defensive: commit() should never actually raise given how the
        # simulator constructs its operation objects, but a screen
        # crashing an entire teaching demo over one bad commit is a
        # much worse outcome than swallowing an error and telling the
        # student what happened, so this is guarded regardless.
        try:
            self.current_simulation.commit(self.model)
        except (IndexError, ValueError) as error:
            self.error_message = str(error)

        self.operation_committed = True
        self.current_simulation = None

        self.simulator.reset()

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    def update(self, dt: float) -> None:
        self.update_back_button(dt)
        self.update_speed_buttons(dt)

        self.randomize_button.update(dt)

        self.info_button.update(dt)

        self.storage.update(dt)

        for button in self.strategy_buttons.values():
            button.update(dt)

        for button in self.hash_function_buttons.values():
            button.update(dt)

        for button in self.mode_buttons.values():
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
        self._render_legend()
        self._render_table()

        self.info_button.render(self.surface)
        self.storage.render(self.surface)
        self.info_panel.render(self.surface)

    def _draw_text(self, text, position, font, color=Color.TEXT_PRIMARY):
        rendered = font.render(text, True, color)
        self.surface.blit(rendered, position)

    def _draw_wrapped_text(self, text, rect, font, color=Color.TEXT_SECONDARY):
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
        # Panel height grew by _row_shift to fit the inserted
        # Randomize row without pushing the bottom controls (load bar,
        # step info) outside the panel.
        panel_rect = pygame.Rect(10, 70, 250, 670 + self._row_shift)
        draw_panel(self.surface, panel_rect, elevated=True)

        self._draw_text("TA Controls", (25, 80), self.control_font)

        self._draw_text(
            "Collision Strategy", (25, 112), self.section_font, color=Color.TEXT_SECONDARY
        )

        self.randomize_button.render(self.surface)

        for strategy, button in self.strategy_buttons.items():
            draw_toggle_button(
                self.surface, button, strategy is self.model.collision_strategy
            )

        for hash_function, button in self.hash_function_buttons.items():
            draw_toggle_button(
                self.surface, button, hash_function is self.model.hash_function
            )

        for mode, button in self.mode_buttons.items():
            draw_toggle_button(self.surface, button, mode is self.model.mode)

        shift = self._row_shift

        self._draw_text("Capacity:", (15, 353 + shift), self.small_font, color=Color.TEXT_SECONDARY)
        self.capacity_input.render(self.surface)

        self._draw_text("Key:", (15, 387 + shift), self.small_font, color=Color.TEXT_SECONDARY)
        self.key_input.render(self.surface)

        self._draw_text("Value:", (15, 421 + shift), self.small_font, color=Color.TEXT_SECONDARY)

        if self.model.mode is HashTableMode.MAP:
            self.value_input.render(self.surface)
        else:
            self._draw_text("N/A (Set mode)", (160, 421 + shift), self.small_font, color=Color.TEXT_MUTED)

        for button in self.operation_buttons:
            button.render(self.surface)

        self._draw_text(
            "Simulation", (25, 588 + shift), self.section_font, color=Color.TEXT_SECONDARY
        )

        self.render_speed_buttons()

        for index, button in enumerate(self.navigation_buttons):
            if index == 4:
                draw_toggle_button(
                    self.surface,
                    button,
                    self.current_simulation is not None and not self.simulator.running,
                )
            else:
                button.render(self.surface)

        self._render_load_bar()

        if self.current_simulation is not None:
            state = self.simulator.state

            if state is not None:
                self._draw_text(
                    (
                        f"Step: {state.step + 1}/{len(self.current_simulation.states)}"
                        f"   Collisions: {state.data.collisions}"
                    ),
                    (15, 698 + shift),
                    self.small_font,
                    color=Color.TEXT_MUTED,
                )
        else:
            info = (
                f"Size: {self.model.size}/{self.model.capacity}  "
                f"Load: {self.model.load_factor:.0%}"
            )
            self._draw_text(info, (15, 698 + shift), self.small_font, color=Color.TEXT_MUTED)

    def _render_load_bar(self) -> None:
        track_rect = pygame.Rect(15, 683 + self._row_shift, 220, 10)

        pygame.draw.rect(self.surface, Color.SURFACE_RAISED, track_rect, border_radius=5)
        pygame.draw.rect(self.surface, Color.BORDER, track_rect, 1, border_radius=5)

        load = min(1.0, self.model.load_factor)

        if load <= 0:
            return

        if load < 0.5:
            fill_color = Color.STATE_SUCCESS
        elif load < 0.85:
            fill_color = Color.STATE_COMPARING
        else:
            fill_color = Color.STATE_DANGER

        fill_width = max(6, int(track_rect.width * load))
        fill_rect = pygame.Rect(track_rect.x, track_rect.y, fill_width, track_rect.height)

        pygame.draw.rect(self.surface, fill_color, fill_rect, border_radius=5)

    def _render_explanation_panel(self) -> None:
        panel_rect = pygame.Rect(280, 70, self.surface.get_width() - 300, 130)
        draw_panel(self.surface, panel_rect, elevated=False)

        self._draw_text(
            "What is happening?", (295, 82), self.section_font, color=Color.TEXT_SECONDARY
        )

        state = self._get_state()
        description_rect = pygame.Rect(295, 112, panel_rect.width - 30, 75)

        if state is not None:
            self._draw_wrapped_text(state.description, description_rect, self.explanation_font)
            return

        if self.error_message is not None:
            self._draw_wrapped_text(
                self.error_message, description_rect, self.explanation_font, Color.STATE_DANGER
            )
            return

        if self.status_message is not None:
            description = self.status_message
        else:
            description = "Enter a key (and value, in Map mode) and choose an operation."

        # The hash formula is shown here permanently, since this panel
        # is idle most of the time, rather than taking up dedicated
        # space in the control panel. It updates live as the key,
        # capacity, or formula choice changes.
        formula_line = self.model.describe_formula()
        example_line = f"For key {self.key_input.value!r}: {self.model.describe_hash_for(self.key_input.value)}"

        self._draw_wrapped_text(description, description_rect, self.explanation_font)

        formula_rect = pygame.Rect(295, 112 + 22, panel_rect.width - 30, 50)
        self._draw_wrapped_text(formula_line, formula_rect, self.small_font, Color.TEXT_MUTED)

        example_rect = pygame.Rect(295, 112 + 38, panel_rect.width - 30, 50)
        self._draw_wrapped_text(example_line, example_rect, self.small_font, Color.TEXT_MUTED)

    def _get_state(self):
        if self.simulator.state is None:
            return None
        return self.simulator.state.data

    # ------------------------------------------------------------------
    # Table visualization
    # ------------------------------------------------------------------

    LEGEND = [
        (Color.STATE_ACTIVE, "Current"),
        (Color.STATE_COMPARING, "Probed"),
        (Color.STATE_DEFAULT, "Occupied"),
        (Color.STATE_DANGER, "Deleted"),
    ]

    def _canvas_rect(self) -> pygame.Rect:
        return pygame.Rect(
            280, 238, self.surface.get_width() - 300, self.surface.get_height() - 258
        )

    def _render_legend(self) -> None:
        x = 280
        y = 212

        for color, label in self.LEGEND:
            swatch = pygame.Rect(x, y + 3, 12, 12)
            pygame.draw.rect(self.surface, color, swatch, border_radius=3)

            text = self.label_font.render(label, True, Color.TEXT_SECONDARY)
            self.surface.blit(text, (x + 18, y))

            x += 18 + text.get_width() + 22

    def _slot_color(self, index, occupied, tombstoned, state):
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
            self._render_open_addressing(buckets, tombstones, state)

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

            index_rect = pygame.Rect(
                canvas.left, y + (row_height - index_box_size) // 2, index_box_size, index_box_size
            )

            index_color = (
                Color.STATE_ACTIVE
                if state is not None and state.highlighted_index == index
                else Color.SURFACE_RAISED
            )

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

                background = (
                    Color.STATE_ACTIVE
                    if state is not None and state.highlighted_index == index
                    else Color.STATE_DEFAULT
                )

                draw_item_card(self.surface, rect, background, self.small_font, label)

                if position < len(bucket) - 1:
                    draw_arrow(
                        self.surface,
                        (rect.right, rect.centery),
                        (rect.right + entry_spacing - 6, rect.centery),
                        Color.BORDER,
                        width=2,
                    )

                x += entry_width + entry_spacing

    def _render_open_addressing(self, buckets, tombstones, state) -> None:
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
                    self.surface, rect, color, self.small_font, label,
                    caption_font=self.label_font, caption=str(index),
                )
            else:
                pygame.draw.rect(self.surface, color, rect, border_radius=8)
                pygame.draw.rect(self.surface, Color.BORDER, rect, 2, border_radius=8)

                text = self.label_font.render(
                    "deleted" if tombstoned else "empty", True, Color.TEXT_MUTED
                )
                self.surface.blit(text, text.get_rect(center=rect.center))

                index_text = self.label_font.render(str(index), True, Color.TEXT_MUTED)
                self.surface.blit(
                    index_text, index_text.get_rect(centerx=rect.centerx, top=rect.bottom + 3)
                )

            x += slot_width + spacing