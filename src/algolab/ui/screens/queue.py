from __future__ import annotations

import math
import random

import pygame

from algolab.simulation.simulator import Simulator
from algolab.topics.circular_queue.model import CircularQueue
from algolab.topics.circular_queue.simulation import CircularQueueSimulator
from algolab.topics.priority_queue.model import PriorityBacking, PriorityQueue
from algolab.topics.priority_queue.simulation import PriorityQueueSimulator
from algolab.topics.queue.model import Queue
from algolab.topics.queue.simulation import (
    QueueSimulation,
    QueueSimulator,
)
from algolab.ui.components.button import Button
from algolab.ui.components.checkbox import Checkbox
from algolab.ui.components.info_panel import InfoPanel
from algolab.ui.components.numeric_input import NumericInput
from algolab.ui.components.storage_controls import StorageControls
from algolab.ui.components.surface import draw_arrow, draw_item_card, draw_panel, draw_toggle_button
from algolab.ui.screens.screen import Screen
from algolab.ui.theme import Color, Font


class QueueScreen(Screen):
    """
    Screen for visualizing Linear, Circular, and Priority queues.

    Each mode keeps its own independent model, Simulator, and
    in-progress-simulation tracking, so switching modes is purely a
    change of which controls/canvas are shown -- nothing is reset or
    lost when you switch away and back. Only one mode's animation ever
    plays at a time.
    """

    MODES = ("linear", "circular", "priority")

    # The circular queue's capacity input is limited to this range
    # (see _set_circular_capacity), so a loaded file must respect it too.
    MIN_CIRCULAR_CAPACITY = 3
    MAX_CIRCULAR_CAPACITY = 16

    LEGEND_LINEAR = [
        (Color.STATE_ACTIVE, "Front"),
        (Color.STATE_VISITED, "Rear"),
        (Color.STATE_COMPARING, "Peeked"),
        (Color.STATE_SUCCESS, "New"),
        (Color.STATE_DANGER, "Removed"),
    ]

    LEGEND_CIRCULAR = [
        (Color.STATE_ACTIVE, "Front"),
        (Color.STATE_VISITED, "Rear"),
        (Color.STATE_COMPARING, "Peeked/Active"),
        (Color.STATE_SUCCESS, "New"),
        (Color.STATE_DANGER, "Removed"),
        (Color.STATE_DEFAULT, "Occupied"),
    ]

    LEGEND_PRIORITY = [
        (Color.STATE_COMPARING, "Comparing"),
        (Color.STATE_REPLACE, "Swapping"),
        (Color.STATE_SUCCESS, "New"),
        (Color.STATE_DANGER, "Removed"),
        (Color.STATE_ACTIVE, "Highest priority"),
    ]

    def __init__(self, surface: pygame.Surface, on_back=None) -> None:
        super().__init__(surface, on_back)

        self.mode = "linear"

        self.control_font = Font.H1()
        self.section_font = Font.H2()
        self.item_font = Font.NODE()
        self.small_font = Font.SMALL()
        self.explanation_font = Font.BODY()
        self.pointer_font = Font.LABEL()
        self.index_font = Font.LABEL()
        self.node_font = Font.NODE()
        self.edge_font = Font.LABEL()

        self._init_mode_toggle()
        self._init_linear()
        self._init_circular()
        self._init_priority()

        self.info_button = Button(
            pygame.Rect(surface.get_width() - 115, 15, 100, 38),
            "Info",
        )

        # Save / Load buttons (left of Info) and their dialog. One file
        # holds whichever mode is active when Save is clicked.
        self.storage = StorageControls(
            surface,
            "queue",
            "Queue",
            capture=self._capture_structure,
            restore=self._restore_structure,
        )

        self.step_timer = 0.0
        self.step_interval = 1.8

    # ------------------------------------------------------------------
    # Mode toggle
    # ------------------------------------------------------------------

    def _init_mode_toggle(self) -> None:
        self.mode_buttons = {
            "linear": Button(pygame.Rect(15, 108, 68, 32), "Linear"),
            "circular": Button(pygame.Rect(88, 108, 68, 32), "Circular"),
            "priority": Button(pygame.Rect(161, 108, 69, 32), "Priority"),
        }

    def _set_mode(self, mode: str) -> None:
        if mode == self.mode:
            return

        self.mode = mode

    def _panel_height(self) -> int:
        return {"linear": 460, "circular": 490, "priority": 630}[self.mode]

    def _active_info_panel(self) -> InfoPanel:
        return {
            "linear": self.linear_info_panel,
            "circular": self.circular_info_panel,
            "priority": self.priority_info_panel,
        }[self.mode]

    # ------------------------------------------------------------------
    # LINEAR mode setup
    # ------------------------------------------------------------------

    def _init_linear(self) -> None:
        self.linear_model = Queue()
        self.linear_simulator = Simulator()
        self.linear_queue_simulator = QueueSimulator(self.linear_model)
        self.linear_current_simulation: QueueSimulation | None = None
        self.linear_operation_committed = False

        self.linear_operation_buttons = self._create_button_row(
            ["Enqueue", "Dequeue", "Peek"],
            ["primary", "danger", "default"],
            190,
        )
        self.linear_navigation_buttons = self._create_navigation_buttons(464)

        self.linear_randomize_button = Button(
            pygame.Rect(140, 152, 95, 24), "Randomize"
        )
        self.linear_value_input = NumericInput(pygame.Rect(135, 330, 75, 30), 10)

        self.linear_speed_button_rects = [
            pygame.Rect(15 + index * 62, 426, 58, 28)
            for index in range(len(self.speed_buttons))
        ]

        self.linear_info_panel = InfoPanel(
            "Linear Queue - Time Complexity",
            [
                ("Enqueue", "O(1)", "Amortized"),
                (
                    "Dequeue",
                    "O(n)",
                    "list.pop(0); a deque or circular queue gets O(1)",
                ),
                ("Peek", "O(1)", ""),
            ],
        )

        # Queue visual layout (unchanged from the original single-mode
        # screen).
        self.queue_x = 430
        self.queue_y = 380
        self.item_width = 120
        self.item_height = 55
        self.item_spacing = 30
        self.front_pointer_y = self.queue_y - 75

    # ------------------------------------------------------------------
    # CIRCULAR mode setup
    # ------------------------------------------------------------------

    def _init_circular(self) -> None:
        self.circular_model = CircularQueue(capacity=8)
        self.circular_simulator = Simulator()
        self.circular_queue_simulator = CircularQueueSimulator(self.circular_model)
        self.circular_current_simulation = None
        self.circular_operation_committed = False

        self.circular_capacity_input = NumericInput(
            pygame.Rect(160, 150, 75, 30), 8
        )
        self.circular_randomize_button = Button(
            pygame.Rect(140, 189, 95, 24), "Randomize"
        )
        self.circular_operation_buttons = self._create_button_row(
            ["Enqueue", "Dequeue", "Peek"],
            ["primary", "danger", "default"],
            222,
        )
        self.circular_value_input = NumericInput(pygame.Rect(135, 362, 75, 30), 10)
        self.circular_navigation_buttons = self._create_navigation_buttons(496)

        self.circular_speed_button_rects = [
            pygame.Rect(15 + index * 62, 458, 58, 28)
            for index in range(len(self.speed_buttons))
        ]

        self.circular_info_panel = InfoPanel(
            "Circular Queue - Time Complexity",
            [
                ("Enqueue", "O(1)", "True O(1); no shifting, unlike a linear list"),
                ("Dequeue", "O(1)", "Index math only, wraps via modulo"),
                ("Peek", "O(1)", ""),
            ],
        )

        self.circular_error_message: str | None = None

    # ------------------------------------------------------------------
    # PRIORITY mode setup
    # ------------------------------------------------------------------

    def _init_priority(self) -> None:
        self.priority_model = PriorityQueue()
        self.priority_simulator = Simulator()
        self.priority_queue_simulator = PriorityQueueSimulator(self.priority_model)
        self.priority_current_simulation = None
        self.priority_operation_committed = False

        self.priority_backing_buttons = [
            Button(pygame.Rect(15, 172, 110, 32), "Heap"),
            Button(pygame.Rect(130, 172, 105, 32), "Sorted List"),
        ]
        self.priority_order_buttons = [
            Button(pygame.Rect(15, 236, 110, 32), "Min First"),
            Button(pygame.Rect(130, 236, 105, 32), "Max First"),
        ]

        self.priority_randomize_button = Button(
            pygame.Rect(140, 275, 95, 24), "Randomize"
        )
        self.priority_operation_buttons = self._create_button_row(
            ["Insert", "Extract", "Peek"],
            ["primary", "danger", "default"],
            308,
        )
        self.priority_value_input = NumericInput(pygame.Rect(135, 453, 75, 30), 10)
        self.priority_priority_input = NumericInput(
            pygame.Rect(135, 493, 75, 30), 5
        )

        # On by default, per the request: this is the common textbook
        # case where a number is its own priority. When checked, the
        # priority input is kept synced to the value input and stops
        # accepting its own clicks/typing (see _handle_priority_event).
        self.priority_match_value_checkbox = Checkbox(
            pygame.Rect(25, 528, 20, 20), "Priority = Value", checked=True
        )
        self.priority_priority_input.set_value(self.priority_value_input.value)

        # Shifted down by 35 (SHIFT) from their original positions
        # (597/559) to make room for the checkbox row inserted above,
        # the same cascade-shift approach used for Hash Table's
        # Randomize row.
        self.priority_navigation_buttons = self._create_navigation_buttons(632)

        self.priority_speed_button_rects = [
            pygame.Rect(15 + index * 62, 594, 58, 28)
            for index in range(len(self.speed_buttons))
        ]

        self.priority_info_panel = InfoPanel(
            "Priority Queue - Time Complexity",
            [
                ("Insert (Heap backing)", "O(log n)", "Bubbles up at most h levels"),
                ("Insert (Sorted List backing)", "O(n)", "Scans for the insertion point"),
                ("Extract (Heap backing)", "O(log n)", "Bubbles down at most h levels"),
                ("Extract (Sorted List backing)", "O(1)", "Highest priority is always index 0"),
                ("Peek", "O(1)", "Same for either backing"),
            ],
        )

        self.priority_error_message: str | None = None

    # ------------------------------------------------------------------
    # Shared button-creation helpers
    # ------------------------------------------------------------------

    def _create_button_row(
        self, labels: list[str], variants: list[str], y_start: int
    ) -> list[Button]:
        buttons = []
        x = 25
        width = 220
        height = 38
        spacing = 45

        for index, (label, variant) in enumerate(zip(labels, variants)):
            buttons.append(
                Button(
                    pygame.Rect(x, y_start + index * spacing, width, height),
                    label,
                    variant=variant,
                )
            )

        return buttons

    def _create_navigation_buttons(self, y: int) -> list[Button]:
        labels = ["|<", "<", ">", ">|", "P"]
        buttons = []
        x = 25
        width = 40
        height = 35
        spacing = 45

        for index, label in enumerate(labels):
            buttons.append(
                Button(pygame.Rect(x + index * spacing, y, width, height), label)
            )

        return buttons

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

    # ==================================================================
    # Event handling
    # ==================================================================

    def handle_event(self, event: pygame.event.Event) -> None:
        if self._active_info_panel().handle_event(event):
            return

        if self.storage.handle_event(event):
            return

        if self.handle_back_event(event):
            return

        if self.handle_speed_event(event):
            return

        for mode, button in self.mode_buttons.items():
            if button.handle_event(event):
                self._set_mode(mode)

        if self.info_button.handle_event(event):
            self._active_info_panel().open()

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

        if self.mode == "linear":
            self._handle_linear_event(event)
        elif self.mode == "circular":
            self._handle_circular_event(event)
        else:
            self._handle_priority_event(event)

        navigation_buttons = self._active_navigation_buttons()
        for index, button in enumerate(navigation_buttons):
            if button.handle_event(event):
                self._handle_navigation(index)

    def _handle_linear_event(self, event: pygame.event.Event) -> None:
        self.linear_value_input.handle_event(event)

        if self.linear_randomize_button.handle_event(event):
            self._randomize_linear()

        for index, button in enumerate(self.linear_operation_buttons):
            if button.handle_event(event):
                self._select_operation(index)

    def _handle_circular_event(self, event: pygame.event.Event) -> None:
        self.circular_value_input.handle_event(event)

        new_capacity = self.circular_capacity_input.handle_event(event)
        if new_capacity is not None:
            self._set_circular_capacity(new_capacity)

        if self.circular_randomize_button.handle_event(event):
            self._randomize_circular()

        for index, button in enumerate(self.circular_operation_buttons):
            if button.handle_event(event):
                self._select_operation(index)

    def _handle_priority_event(self, event: pygame.event.Event) -> None:
        self.priority_value_input.handle_event(event)

        self.priority_match_value_checkbox.handle_event(event)

        if self.priority_match_value_checkbox.checked:
            # Locked to mirror Value: never processes its own click or
            # typing while checked, and is force-synced every event so
            # it can never drift from Value even between operations.
            self.priority_priority_input.set_value(self.priority_value_input.value)
        else:
            self.priority_priority_input.handle_event(event)

        for index, button in enumerate(self.priority_backing_buttons):
            if button.handle_event(event):
                self._set_priority_backing(
                    PriorityBacking.HEAP if index == 0 else PriorityBacking.SORTED_LIST
                )

        for index, button in enumerate(self.priority_order_buttons):
            if button.handle_event(event):
                self._set_priority_order(min_first=(index == 0))

        if self.priority_randomize_button.handle_event(event):
            self._randomize_priority()

        for index, button in enumerate(self.priority_operation_buttons):
            if button.handle_event(event):
                self._select_operation(index)

    def _active_navigation_buttons(self) -> list[Button]:
        return {
            "linear": self.linear_navigation_buttons,
            "circular": self.circular_navigation_buttons,
            "priority": self.priority_navigation_buttons,
        }[self.mode]

    # ------------------------------------------------------------------
    # Operation selection (per mode)
    # ------------------------------------------------------------------

    def _select_operation(self, index: int) -> None:
        if self.mode == "linear":
            self._select_linear_operation(index)
        elif self.mode == "circular":
            self._select_circular_operation(index)
        else:
            self._select_priority_operation(index)

    def _select_linear_operation(self, index: int) -> None:
        if self.linear_current_simulation is not None:
            return

        value = self.linear_value_input.value

        try:
            if index == 0:
                simulation = self.linear_queue_simulator.enqueue(value)
            elif index == 1:
                simulation = self.linear_queue_simulator.dequeue()
            elif index == 2:
                simulation = self.linear_queue_simulator.peek()
            else:
                return
        except IndexError:
            return

        self.linear_current_simulation = simulation
        self.linear_operation_committed = False
        self.linear_simulator.load_states(list(simulation.states))
        self.step_timer = 0.0

    def _select_circular_operation(self, index: int) -> None:
        if self.circular_current_simulation is not None:
            return

        value = self.circular_value_input.value

        try:
            if index == 0:
                simulation = self.circular_queue_simulator.enqueue(value)
            elif index == 1:
                simulation = self.circular_queue_simulator.dequeue()
            elif index == 2:
                simulation = self.circular_queue_simulator.peek()
            else:
                return
        except IndexError:
            return

        self.circular_current_simulation = simulation
        self.circular_operation_committed = False
        self.circular_simulator.load_states(list(simulation.states))
        self.circular_error_message = None
        self.step_timer = 0.0

    def _select_priority_operation(self, index: int) -> None:
        if self.priority_current_simulation is not None:
            return

        value = self.priority_value_input.value
        priority = self.priority_priority_input.value

        try:
            if index == 0:
                simulation = self.priority_queue_simulator.insert(value, priority)
            elif index == 1:
                simulation = self.priority_queue_simulator.extract()
            elif index == 2:
                simulation = self.priority_queue_simulator.peek()
            else:
                return
        except IndexError:
            return

        self.priority_current_simulation = simulation
        self.priority_operation_committed = False
        self.priority_simulator.load_states(list(simulation.states))
        self.priority_error_message = None
        self.step_timer = 0.0

    # ------------------------------------------------------------------
    # Settings changes
    # ------------------------------------------------------------------

    def _set_circular_capacity(self, capacity: int) -> None:
        self._cancel_active_simulation()

        capacity = max(
            self.MIN_CIRCULAR_CAPACITY,
            min(self.MAX_CIRCULAR_CAPACITY, capacity),
        )

        try:
            self.circular_model.set_capacity(capacity)
        except ValueError as error:
            self.circular_error_message = str(error)
            return

        self.circular_error_message = None

    def _set_priority_backing(self, backing: PriorityBacking) -> None:
        self._cancel_active_simulation()
        self.priority_model.set_backing(backing)
        self.priority_error_message = None

    def _set_priority_order(self, min_first: bool) -> None:
        self._cancel_active_simulation()
        self.priority_model.set_priority_order(min_first)
        self.priority_error_message = None

    def _cancel_active_simulation(self) -> None:
        """Cancel whichever mode's simulation is currently active."""

        if self.mode == "linear":
            self.linear_simulator.reset()
            self.linear_current_simulation = None
            self.linear_operation_committed = False
        elif self.mode == "circular":
            self.circular_simulator.reset()
            self.circular_current_simulation = None
            self.circular_operation_committed = False
        else:
            self.priority_simulator.reset()
            self.priority_current_simulation = None
            self.priority_operation_committed = False

    # ------------------------------------------------------------------
    # Randomize (per mode)
    # ------------------------------------------------------------------

    def _randomize_linear(self) -> None:
        self._cancel_active_simulation()

        self.linear_model.clear()

        for _ in range(random.randint(3, 5)):
            self.linear_model.enqueue(random.randint(1, 99))

        self.step_timer = 0.0

    def _randomize_circular(self) -> None:
        self._cancel_active_simulation()

        self.circular_model.clear()

        # Leave at least one slot open so is_full's boundary case is
        # still reachable by hand afterward, rather than always
        # starting already full.
        count = random.randint(1, max(1, self.circular_model.capacity - 1))

        for _ in range(count):
            self.circular_model.enqueue(random.randint(1, 99))

        self.circular_error_message = None
        self.step_timer = 0.0

    def _randomize_priority(self) -> None:
        self._cancel_active_simulation()

        self.priority_model.clear()

        match_value = self.priority_match_value_checkbox.checked

        for _ in range(random.randint(4, 7)):
            value = random.randint(1, 99)
            priority = value if match_value else random.randint(1, 20)
            self.priority_model.insert(value, priority)

        self.priority_error_message = None
        self.step_timer = 0.0

    # ------------------------------------------------------------------
    # Save / Load
    # ------------------------------------------------------------------

    def _capture_structure(self) -> tuple[str | None, dict]:
        """The active mode's structure as (mode, data) for the Save dialog."""

        if self.mode == "linear":
            return "linear", self.linear_model.to_dict()

        if self.mode == "circular":
            return "circular", self.circular_model.to_dict()

        return "priority", self.priority_model.to_dict()

    def _restore_structure(self, mode: str | None, data: dict) -> None:
        """Load a saved queue (from the Load dialog), switching to its mode.

        The file's own mode decides which queue it replaces. Each
        model's from_dict() validates everything first and raises
        ValueError on bad data, so nothing below runs for a bad file;
        only that mode's running simulation is cancelled.
        """

        if mode == "linear":
            loaded = Queue.from_dict(data)
        elif mode == "circular":
            loaded = CircularQueue.from_dict(data)

            if not (
                self.MIN_CIRCULAR_CAPACITY
                <= loaded.capacity
                <= self.MAX_CIRCULAR_CAPACITY
            ):
                raise ValueError(
                    "A circular queue here must have a capacity between "
                    f"{self.MIN_CIRCULAR_CAPACITY} and "
                    f"{self.MAX_CIRCULAR_CAPACITY}."
                )
        elif mode == "priority":
            loaded = PriorityQueue.from_dict(data)
        else:
            raise ValueError(f"Unknown queue type: {mode!r}.")

        self._set_mode(mode)
        self._cancel_active_simulation()

        if mode == "linear":
            self.linear_model.clear()

            for value in loaded.to_list():
                self.linear_model.enqueue(value)
        elif mode == "circular":
            self.circular_model.replace_with(loaded)
            self.circular_capacity_input.set_value(loaded.capacity)
            self.circular_error_message = None
        else:
            self.priority_model.replace_with(loaded)
            self.priority_error_message = None

        self.step_timer = 0.0

    # ------------------------------------------------------------------
    # Navigation (per mode)
    # ------------------------------------------------------------------

    def _handle_navigation(self, index: int) -> None:
        simulator, current_simulation = self._active_simulator_and_simulation()

        if current_simulation is None:
            return

        if index == 0:
            simulator.history.previous_to_start()
        elif index == 1:
            simulator.previous()
        elif index == 2:
            simulator.next()
        elif index == 3:
            while simulator.can_go_forward:
                simulator.next()
        elif index == 4:
            if simulator.running:
                simulator.pause()
            else:
                simulator.resume()

        self._commit_if_finished()

    def _active_simulator_and_simulation(self):
        if self.mode == "linear":
            return self.linear_simulator, self.linear_current_simulation
        if self.mode == "circular":
            return self.circular_simulator, self.circular_current_simulation
        return self.priority_simulator, self.priority_current_simulation

    def _commit_if_finished(self) -> None:
        if self.mode == "linear":
            self._commit_linear_if_finished()
        elif self.mode == "circular":
            self._commit_circular_if_finished()
        else:
            self._commit_priority_if_finished()

    def _commit_linear_if_finished(self) -> None:
        if self.linear_operation_committed:
            return
        if not self.linear_simulator.is_at_end:
            return
        if self.linear_current_simulation is None:
            return

        self.linear_current_simulation.commit(self.linear_model)
        self.linear_operation_committed = True
        self.linear_current_simulation = None
        self.linear_simulator.reset()

    def _commit_circular_if_finished(self) -> None:
        if self.circular_operation_committed:
            return
        if not self.circular_simulator.is_at_end:
            return
        if self.circular_current_simulation is None:
            return

        try:
            self.circular_current_simulation.commit(self.circular_model)
        except IndexError as error:
            self.circular_error_message = str(error)

        self.circular_operation_committed = True
        self.circular_current_simulation = None
        self.circular_simulator.reset()

    def _commit_priority_if_finished(self) -> None:
        if self.priority_operation_committed:
            return
        if not self.priority_simulator.is_at_end:
            return
        if self.priority_current_simulation is None:
            return

        try:
            self.priority_current_simulation.commit(self.priority_model)
        except IndexError as error:
            self.priority_error_message = str(error)

        self.priority_operation_committed = True
        self.priority_current_simulation = None
        self.priority_simulator.reset()

    # ==================================================================
    # Update
    # ==================================================================

    def update(self, dt: float) -> None:
        self.update_back_button(dt)

        # Speed button rects are reassigned here, before
        # update_speed_buttons() reads them for hover detection, so
        # switching modes never leaves hover checking against a stale
        # rect from the previous mode even for a single frame.
        rects = {
            "linear": self.linear_speed_button_rects,
            "circular": self.circular_speed_button_rects,
            "priority": self.priority_speed_button_rects,
        }[self.mode]

        for button, rect in zip(self.speed_buttons, rects):
            button.rect = rect

        self.update_speed_buttons(dt)
        self.info_button.update(dt)
        self.storage.update(dt)

        for button in self.mode_buttons.values():
            button.update(dt)

        if self.mode == "linear":
            self.linear_randomize_button.update(dt)
            for button in self.linear_operation_buttons:
                button.update(dt)
            for button in self.linear_navigation_buttons:
                button.update(dt)
        elif self.mode == "circular":
            self.circular_randomize_button.update(dt)
            for button in self.circular_operation_buttons:
                button.update(dt)
            for button in self.circular_navigation_buttons:
                button.update(dt)
        else:
            self.priority_randomize_button.update(dt)
            for button in self.priority_backing_buttons:
                button.update(dt)
            for button in self.priority_order_buttons:
                button.update(dt)
            for button in self.priority_operation_buttons:
                button.update(dt)
            for button in self.priority_navigation_buttons:
                button.update(dt)

        simulator, current_simulation = self._active_simulator_and_simulation()

        if current_simulation is None:
            return

        if not simulator.running:
            return

        if simulator.is_at_end:
            simulator.pause()
            self._commit_if_finished()
            return

        self.step_timer += dt

        if self.step_timer >= self.scaled_interval(self.step_interval):
            self.step_timer = 0.0
            simulator.next()
            self._commit_if_finished()

    # ==================================================================
    # Rendering
    # ==================================================================

    def render(self) -> None:
        self.surface.fill(Color.BG)

        self.render_back_button()
        self._render_control_panel()
        self._render_explanation_panel()
        self._render_legend()

        if self.mode == "linear":
            self._render_linear_queue()
        elif self.mode == "circular":
            self._render_circular_queue()
        else:
            self._render_priority_queue()

        self.info_button.render(self.surface)
        self.storage.render(self.surface)
        self._active_info_panel().render(self.surface)

    def _render_control_panel(self) -> None:
        panel_rect = pygame.Rect(10, 70, 250, self._panel_height())
        draw_panel(self.surface, panel_rect, elevated=True)

        self._draw_text("TA Controls", (25, 80), self.control_font)

        for mode, button in self.mode_buttons.items():
            draw_toggle_button(self.surface, button, mode == self.mode)

        if self.mode == "linear":
            self._render_linear_panel()
        elif self.mode == "circular":
            self._render_circular_panel()
        else:
            self._render_priority_panel()

        self.render_speed_buttons()

        navigation_buttons = self._active_navigation_buttons()
        simulator, current_simulation = self._active_simulator_and_simulation()

        for index, button in enumerate(navigation_buttons):
            if index == 4:
                draw_toggle_button(
                    self.surface,
                    button,
                    current_simulation is not None and not simulator.running,
                )
            else:
                button.render(self.surface)

    # ------------------------------------------------------------------
    # LINEAR panel + canvas
    # ------------------------------------------------------------------

    def _render_linear_panel(self) -> None:
        self._draw_text(
            "Operations", (25, 155), self.section_font, color=Color.TEXT_SECONDARY
        )
        self.linear_randomize_button.render(self.surface)

        for button in self.linear_operation_buttons:
            button.render(self.surface)

        self._draw_text(
            "Value:", (25, 335), self.section_font, color=Color.TEXT_SECONDARY
        )
        self.linear_value_input.render(self.surface)

        self._draw_text(
            "Simulation", (25, 400), self.section_font, color=Color.TEXT_SECONDARY
        )

        if self.linear_current_simulation is not None:
            state = self.linear_simulator.state
            if state is not None:
                self._draw_text(
                    f"Step: {state.step + 1}/{len(self.linear_current_simulation.states)}",
                    (25, 499),
                    self.small_font,
                    color=Color.TEXT_MUTED,
                )

    def _get_linear_state(self):
        if self.linear_simulator.state is None:
            return None
        return self.linear_simulator.state.data

    def _render_linear_queue(self) -> None:
        values = tuple(self.linear_model.to_list())
        state = self._get_linear_state()

        front_index = None
        rear_index = None
        created_value = None
        removed_value = None
        peeked_value = None

        if state is None:
            front_index = 0 if values else None
            rear_index = len(values) - 1 if values else None
        else:
            values = state.values
            front_index = state.front_index
            rear_index = state.rear_index
            created_value = state.created_value
            removed_value = state.removed_value
            peeked_value = state.peeked_value

        if not values and created_value is None and removed_value is None:
            area = pygame.Rect(280, 220, self.surface.get_width() - 300, 120)
            text = self.explanation_font.render(
                "Queue is empty. Enqueue a value to begin.", True, Color.TEXT_MUTED
            )
            self.surface.blit(text, text.get_rect(center=area.center))

        for index, value in enumerate(values):
            x = self.queue_x + index * (self.item_width + self.item_spacing)

            background = Color.STATE_DEFAULT
            if index == front_index:
                background = Color.STATE_ACTIVE
            if index == rear_index and index != front_index:
                background = Color.STATE_VISITED
            if (
                front_index is not None
                and peeked_value is not None
                and index == front_index
                and value == peeked_value
            ):
                background = Color.STATE_COMPARING

            rect = pygame.Rect(x, self.queue_y, self.item_width, self.item_height)
            draw_item_card(
                self.surface, rect, background, self.item_font, value,
                caption_font=self.index_font, caption=f"index {index}",
            )

            if index < len(values) - 1:
                end_x = x + self.item_width + self.item_spacing - 5
                pygame.draw.line(
                    self.surface, Color.BORDER,
                    (x + self.item_width + 5, self.queue_y + self.item_height // 2),
                    (end_x, self.queue_y + self.item_height // 2), 3,
                )

        if created_value is not None:
            rect = pygame.Rect(self.queue_x, self.queue_y + 100, self.item_width, self.item_height)
            draw_item_card(
                self.surface, rect, Color.STATE_SUCCESS, self.item_font, created_value,
                label_font=self.pointer_font, label="NEW",
            )

        if removed_value is not None:
            rect = pygame.Rect(self.queue_x, self.queue_y + 100, self.item_width, self.item_height)
            draw_item_card(
                self.surface, rect, Color.STATE_DANGER, self.item_font, removed_value,
                label_font=self.pointer_font, label="REMOVED",
            )

        self._render_linear_pointers(front_index, rear_index, values)

    def _render_linear_pointers(self, front_index, rear_index, values) -> None:
        self._draw_text("FRONT", (self.queue_x, self.front_pointer_y), self.control_font, color=Color.ACCENT)

        if front_index is None or not values:
            start = (self.queue_x + 35, self.front_pointer_y + 30)
            end = (self.queue_x + 35, self.queue_y - 5)
            pygame.draw.line(self.surface, Color.ACCENT, start, end, 3)
            self._draw_text("NULL", (self.queue_x + 50, self.queue_y - 25), self.pointer_font, color=Color.TEXT_SECONDARY)
            return

        item_x = self.queue_x + front_index * (self.item_width + self.item_spacing)
        start = (item_x + self.item_width // 2, self.front_pointer_y + 45)
        end = (item_x + self.item_width // 2, self.queue_y - 5)
        pygame.draw.line(self.surface, Color.ACCENT, start, end, 3)

        if rear_index is not None and 0 <= rear_index < len(values):
            rear_x = self.queue_x + rear_index * (self.item_width + self.item_spacing)
            text = self.control_font.render("REAR", True, Color.ACCENT)
            text_rect = text.get_rect(centerx=rear_x + self.item_width // 2, bottom=self.front_pointer_y - 5)
            self.surface.blit(text, text_rect)
            rear_start = (rear_x + self.item_width // 2, text_rect.bottom + 5)
            rear_end = (rear_x + self.item_width // 2, self.queue_y - 5)
            pygame.draw.line(self.surface, Color.ACCENT, rear_start, rear_end, 3)

    # ------------------------------------------------------------------
    # CIRCULAR panel + canvas
    # ------------------------------------------------------------------

    def _render_circular_panel(self) -> None:
        self._draw_text(
            "Capacity:", (15, 155), self.small_font, color=Color.TEXT_SECONDARY
        )
        self.circular_capacity_input.render(self.surface)

        self._draw_text(
            "Operations", (25, 192), self.section_font, color=Color.TEXT_SECONDARY
        )
        self.circular_randomize_button.render(self.surface)

        for button in self.circular_operation_buttons:
            button.render(self.surface)

        self._draw_text(
            "Value:", (25, 362), self.section_font, color=Color.TEXT_SECONDARY
        )
        self.circular_value_input.render(self.surface)

        self._draw_text(
            "Simulation", (25, 432), self.section_font, color=Color.TEXT_SECONDARY
        )

        info_y = 531
        if self.circular_current_simulation is not None:
            state = self.circular_simulator.state
            if state is not None:
                self._draw_text(
                    f"Step: {state.step + 1}/{len(self.circular_current_simulation.states)}",
                    (15, info_y), self.small_font, color=Color.TEXT_MUTED,
                )
        else:
            info = f"Size: {self.circular_model.size}/{self.circular_model.capacity}"
            self._draw_text(info, (15, info_y), self.small_font, color=Color.TEXT_MUTED)

    def _get_circular_state(self):
        if self.circular_simulator.state is None:
            return None
        return self.circular_simulator.state.data

    def _circular_canvas_rect(self) -> pygame.Rect:
        # Top at 245, not 210, to clear the legend row (drawn at
        # y=210, ending roughly at 230) with the same margin BST and
        # Heap already use before their own tree diagrams.
        return pygame.Rect(
            280, 245, self.surface.get_width() - 300, self.surface.get_height() - 265
        )

    def _render_circular_queue(self) -> None:
        state = self._get_circular_state()

        if state is not None:
            slots = state.slots
            capacity = state.capacity
            front_index = state.front_index
            rear_index = state.rear_index
            active_index = state.active_index
            created_index = state.created_index
            removed_index = state.removed_index
            peeked_index = state.peeked_index
        else:
            slots = self.circular_model.slots_snapshot()
            capacity = self.circular_model.capacity
            front_index = self.circular_model.front_index
            rear_index = self.circular_model.rear_index
            active_index = created_index = removed_index = peeked_index = None

        canvas = self._circular_canvas_rect()
        center = canvas.center
        radius = min(canvas.width, canvas.height) * 0.36
        slot_size = 68

        positions = []
        for index in range(capacity):
            angle = (2 * math.pi * index) / capacity - (math.pi / 2)
            x = center[0] + radius * math.cos(angle)
            y = center[1] + radius * math.sin(angle)
            positions.append((x, y))

        for index in range(capacity):
            value = slots[index] if index < len(slots) else None
            x, y = positions[index]
            rect = pygame.Rect(0, 0, slot_size, slot_size)
            rect.center = (int(x), int(y))

            background = Color.SURFACE if value is None else Color.STATE_DEFAULT

            if index == removed_index:
                background = Color.STATE_DANGER
            elif index == created_index:
                background = Color.STATE_SUCCESS
            elif index == peeked_index or index == active_index:
                background = Color.STATE_COMPARING
            elif index == front_index and value is not None:
                background = Color.STATE_ACTIVE
            elif index == rear_index and value is not None:
                background = Color.STATE_VISITED

            label = str(value) if value is not None else ""
            draw_item_card(
                self.surface, rect, background, self.small_font, label,
                caption_font=self.edge_font, caption=str(index),
            )

        self._render_circular_pointer_label(
            "FRONT", front_index, positions, center, Color.ACCENT
        )
        self._render_circular_pointer_label(
            "REAR", rear_index, positions, center, Color.STATE_VISITED
        )

        if self.circular_error_message is not None:
            area = pygame.Rect(280, canvas.bottom - 40, canvas.width, 30)
            self._draw_wrapped_text(
                self.circular_error_message, area, self.small_font, Color.STATE_DANGER
            )

    def _render_circular_pointer_label(
        self, label, index, positions, center, color
    ) -> None:
        if index is None:
            return

        slot_x, slot_y = positions[index]

        direction_x = slot_x - center[0]
        direction_y = slot_y - center[1]
        length = math.hypot(direction_x, direction_y) or 1.0

        label_x = slot_x + (direction_x / length) * 46
        label_y = slot_y + (direction_y / length) * 46

        text = self.pointer_font.render(label, True, color)
        text_rect = text.get_rect(center=(int(label_x), int(label_y)))
        self.surface.blit(text, text_rect)

    # ------------------------------------------------------------------
    # PRIORITY panel + canvas
    # ------------------------------------------------------------------

    def _render_priority_panel(self) -> None:
        self._draw_text(
            "Backing", (25, 148), self.section_font, color=Color.TEXT_SECONDARY
        )
        for index, button in enumerate(self.priority_backing_buttons):
            is_heap = self.priority_model.backing is PriorityBacking.HEAP
            is_on = (index == 0) == is_heap
            draw_toggle_button(self.surface, button, is_on)

        self._draw_text(
            "Priority Order", (25, 212), self.section_font, color=Color.TEXT_SECONDARY
        )
        for index, button in enumerate(self.priority_order_buttons):
            is_on = (index == 0) == self.priority_model.min_priority_first
            draw_toggle_button(self.surface, button, is_on)

        self._draw_text(
            "Operations", (25, 278), self.section_font, color=Color.TEXT_SECONDARY
        )
        self.priority_randomize_button.render(self.surface)

        for button in self.priority_operation_buttons:
            button.render(self.surface)

        self._draw_text(
            "Value:", (25, 453), self.section_font, color=Color.TEXT_SECONDARY
        )
        self.priority_value_input.render(self.surface)

        self._draw_text(
            "Priority:", (25, 493), self.section_font, color=Color.TEXT_SECONDARY
        )
        self.priority_priority_input.render(self.surface)

        self.priority_match_value_checkbox.render(self.surface)

        self._draw_text(
            "Simulation", (25, 568), self.section_font, color=Color.TEXT_SECONDARY
        )

        info_y = 667
        if self.priority_current_simulation is not None:
            state = self.priority_simulator.state
            if state is not None:
                self._draw_text(
                    f"Step: {state.step + 1}/{len(self.priority_current_simulation.states)}",
                    (15, info_y), self.small_font, color=Color.TEXT_MUTED,
                )
        else:
            self._draw_text(
                f"Size: {self.priority_model.size}", (15, info_y),
                self.small_font, color=Color.TEXT_MUTED,
            )

        if self.priority_error_message is not None:
            area = pygame.Rect(15, info_y + 16, 220, 32)
            self._draw_wrapped_text(
                self.priority_error_message, area, self.small_font, Color.STATE_DANGER
            )

    def _get_priority_state(self):
        if self.priority_simulator.state is None:
            return None
        return self.priority_simulator.state.data

    def _render_priority_queue(self) -> None:
        state = self._get_priority_state()

        if state is not None:
            entries = state.entries
            backing = state.backing
            current_index = state.current_index
            compared_indices = state.compared_indices or ()
            swapped_indices = state.swapped_indices or ()
            created_index = state.created_index
            removed_index = state.removed_index
            peeked_index = state.peeked_index
        else:
            entries = tuple(self.priority_model.entries)
            backing = self.priority_model.backing
            current_index = None
            compared_indices = ()
            swapped_indices = ()
            created_index = removed_index = peeked_index = None

        if not entries:
            area = pygame.Rect(280, 220, self.surface.get_width() - 300, 120)
            text = self.explanation_font.render(
                "Priority queue is empty. Insert a value to begin.",
                True, Color.TEXT_MUTED,
            )
            self.surface.blit(text, text.get_rect(center=area.center))
            return

        if backing is PriorityBacking.HEAP:
            self._render_priority_as_tree(
                entries, current_index, compared_indices, swapped_indices,
                created_index, removed_index, peeked_index,
            )
        else:
            self._render_priority_as_list(
                entries, current_index, compared_indices, swapped_indices,
                created_index, removed_index, peeked_index,
            )

    def _priority_entry_color(
        self, index, current_index, compared_indices, swapped_indices,
        created_index, removed_index, peeked_index,
    ) -> tuple[int, int, int]:
        if index == removed_index:
            return Color.STATE_DANGER
        if index == created_index:
            return Color.STATE_SUCCESS
        if index in swapped_indices:
            return Color.STATE_REPLACE
        if index in compared_indices:
            return Color.STATE_COMPARING
        if index == peeked_index:
            return Color.STATE_ACTIVE
        # Index 0 is always the highest-priority entry, for either
        # backing, so it stays highlighted even at rest -- a constant
        # visual reminder of the invariant both backings guarantee.
        if index == 0:
            return Color.STATE_ACTIVE
        if index == current_index:
            return Color.STATE_COMPARING
        return Color.STATE_DEFAULT

    def _render_priority_as_tree(
        self, entries, current_index, compared_indices, swapped_indices,
        created_index, removed_index, peeked_index,
    ) -> None:
        node_width, node_height, level_height = 100, 55, 85
        left, right = 330, self.surface.get_width() - 25
        available_width = right - left

        positions = {}
        for index in range(len(entries)):
            depth = (index + 1).bit_length() - 1
            slots_at_depth = 1 << depth
            position_in_level = index - (slots_at_depth - 1)
            slot_width = available_width / slots_at_depth
            center_x = left + (position_in_level + 0.5) * slot_width
            y = 245 + depth * level_height
            positions[index] = pygame.Rect(
                int(center_x - node_width / 2), int(y), node_width, node_height
            )

        for index in range(len(entries)):
            rect = positions[index]
            for child_index in (2 * index + 1, 2 * index + 2):
                if child_index < len(entries):
                    child_rect = positions[child_index]
                    draw_arrow(
                        self.surface,
                        (rect.centerx, rect.bottom),
                        (child_rect.centerx, child_rect.top),
                        Color.BORDER, width=2,
                    )

        for index, entry in enumerate(entries):
            rect = positions[index]
            color = self._priority_entry_color(
                index, current_index, compared_indices, swapped_indices,
                created_index, removed_index, peeked_index,
            )
            draw_item_card(
                self.surface, rect, color, self.node_font, entry.value,
                caption_font=self.edge_font,
                caption=f"p={entry.priority:g}",
            )

    def _render_priority_as_list(
        self, entries, current_index, compared_indices, swapped_indices,
        created_index, removed_index, peeked_index,
    ) -> None:
        x = 320
        y = 420
        width, height, spacing = 120, 70, 30

        for index, entry in enumerate(entries):
            item_x = x + index * (width + spacing)

            if item_x + width > self.surface.get_width() - 15:
                break

            color = self._priority_entry_color(
                index, current_index, compared_indices, swapped_indices,
                created_index, removed_index, peeked_index,
            )
            rect = pygame.Rect(item_x, y, width, height)
            draw_item_card(
                self.surface, rect, color, self.node_font, entry.value,
                caption_font=self.edge_font,
                caption=f"p={entry.priority:g}",
            )

            if index < len(entries) - 1 and item_x + width + spacing <= self.surface.get_width() - 15:
                draw_arrow(
                    self.surface,
                    (item_x + width + 4, y + height // 2),
                    (item_x + width + spacing - 6, y + height // 2),
                    Color.BORDER, width=2,
                )

    # ------------------------------------------------------------------
    # Explanation panel + legend (shared shape, mode-specific content)
    # ------------------------------------------------------------------

    def _render_explanation_panel(self) -> None:
        panel_rect = pygame.Rect(280, 70, self.surface.get_width() - 300, 130)
        draw_panel(self.surface, panel_rect, elevated=False)

        self._draw_text(
            "What is happening?", (295, 82), self.section_font, color=Color.TEXT_SECONDARY
        )

        simulator, current_simulation = self._active_simulator_and_simulation()
        state = simulator.state

        if state is None:
            description = "Select an operation to start a simulation."
        else:
            description = state.data.description

        description_rect = pygame.Rect(295, 112, panel_rect.width - 30, 75)
        self._draw_wrapped_text(description, description_rect, self.explanation_font)

    def _render_legend(self) -> None:
        legend = {
            "linear": self.LEGEND_LINEAR,
            "circular": self.LEGEND_CIRCULAR,
            "priority": self.LEGEND_PRIORITY,
        }[self.mode]

        x = 280
        y = 210

        for color, label in legend:
            swatch = pygame.Rect(x, y + 3, 12, 12)
            pygame.draw.rect(self.surface, color, swatch, border_radius=3)
            text = self.small_font.render(label, True, Color.TEXT_SECONDARY)
            self.surface.blit(text, (x + 18, y))
            x += 18 + text.get_width() + 20