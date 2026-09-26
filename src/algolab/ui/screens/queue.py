from __future__ import annotations

import random

import pygame

from algolab.simulation.simulator import Simulator
from algolab.topics.queue.model import Queue
from algolab.topics.queue.simulation import (
    QueueSimulation,
    QueueSimulator,
)
from algolab.ui.components.button import Button
from algolab.ui.components.info_panel import InfoPanel
from algolab.ui.components.numeric_input import NumericInput
from algolab.ui.components.surface import draw_item_card, draw_panel, draw_toggle_button
from algolab.ui.screens.screen import Screen
from algolab.ui.theme import Color, Font


class QueueScreen(Screen):
    """Screen for visualizing queue operations."""

    LEGEND = [
        (Color.STATE_ACTIVE, "Front"),
        (Color.STATE_VISITED, "Rear"),
        (Color.STATE_COMPARING, "Peeked"),
        (Color.STATE_SUCCESS, "New"),
        (Color.STATE_DANGER, "Removed"),
    ]

    def __init__(self, surface: pygame.Surface, on_back=None) -> None:
        super().__init__(surface, on_back)

        self.model = Queue()
        self.simulator = Simulator()
        self.queue_simulator = QueueSimulator(self.model)

        self.current_simulation: QueueSimulation | None = None
        self.operation_committed = False

        self.control_font = Font.H1()
        self.section_font = Font.H2()
        self.item_font = Font.NODE()
        self.small_font = Font.SMALL()
        self.explanation_font = Font.BODY()
        self.pointer_font = Font.LABEL()
        self.index_font = Font.LABEL()

        self.operation_buttons = self._create_operation_buttons()
        self.navigation_buttons = self._create_navigation_buttons()

        self.randomize_button = Button(
            pygame.Rect(140, 112, 95, 24),
            "Randomize",
        )

        self.info_button = Button(
            pygame.Rect(surface.get_width() - 115, 15, 100, 38),
            "Info",
        )
        self.info_panel = InfoPanel(
            "Queue - Time Complexity",
            [
                ("Enqueue", "O(1)", "Amortized"),
                # Honest about the actual implementation: Queue.dequeue()
                # calls list.pop(0), which is O(n) in real Python since
                # every remaining element shifts down one slot. A
                # deque- or linked-list-backed queue achieves O(1) here.
                ("Dequeue", "O(n)", "list.pop(0); a deque gets O(1)"),
                ("Peek", "O(1)", ""),
            ],
        )

        for index, button in enumerate(self.speed_buttons):
            button.rect = pygame.Rect(15 + index * 62, 381, 58, 28)

        self.value_input = NumericInput(
            pygame.Rect(135, 285, 75, 30),
            10,
        )

        self.step_timer = 0.0

        # A longer interval gives students time to understand each step.
        self.step_interval = 1.8

        # Queue visual layout.
        self.queue_x = 430
        # Pushed down from the original 310 so the REAR label (drawn
        # well above this point, in the large control_font) doesn't
        # land on top of the legend row rendered at a fixed y=210.
        self.queue_y = 380
        self.item_width = 120
        self.item_height = 55
        self.item_spacing = 30

        # FRONT pointer layout.
        self.front_pointer_y = self.queue_y - 75

        # REAR pointer layout.
        self.rear_pointer_y = self.queue_y - 75

    def _create_operation_buttons(self) -> list[Button]:
        labels = ["Enqueue", "Dequeue", "Peek"]
        variants = ["primary", "danger", "default"]

        buttons = []

        x = 25
        y = 145
        width = 220
        height = 38
        spacing = 45

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
        y = 419
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

    def handle_event(self, event: pygame.event.Event) -> None:
        if self.info_panel.handle_event(event):
            return

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

        if self.randomize_button.handle_event(event):
            self._randomize()

        if self.info_button.handle_event(event):
            self.info_panel.open()

        for index, button in enumerate(self.navigation_buttons):
            if button.handle_event(event):
                self._handle_navigation(index)

    def _select_operation(self, index: int) -> None:
        if self.current_simulation is not None:
            return

        value = self.value_input.value

        try:
            if index == 0:
                simulation = self.queue_simulator.enqueue(value)
            elif index == 1:
                simulation = self.queue_simulator.dequeue()
            elif index == 2:
                simulation = self.queue_simulator.peek()
            else:
                return
        except IndexError:
            return

        self.current_simulation = simulation
        self.operation_committed = False

        self.simulator.load_states(list(simulation.states))

        self.step_timer = 0.0

    def _randomize(self) -> None:
        """
        Replace the queue contents with random values, instantly and
        without animation (same behavior as the sorting screen's
        Randomize).
        """

        self.cancel_current_simulation()

        self.model.clear()

        # Capped at 5 so the rear item stays on screen in the default
        # 1280px window: items start at x=430 and take 150px each, so a
        # 6th item would end at x=1300.
        for _ in range(random.randint(3, 5)):
            self.model.enqueue(random.randint(1, 99))

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
        self.update_back_button(dt)
        self.update_speed_buttons(dt)

        for button in self.operation_buttons:
            button.update(dt)

        self.randomize_button.update(dt)

        self.info_button.update(dt)

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

    def render(self) -> None:
        self.surface.fill(Color.BG)

        self.render_back_button()
        self._render_control_panel()
        self._render_explanation_panel()
        self._render_legend()
        self._render_queue()

        self.info_button.render(self.surface)
        self.info_panel.render(self.surface)

    def _render_legend(self) -> None:
        x = 280
        y = 210

        for color, label in self.LEGEND:
            swatch = pygame.Rect(x, y + 3, 12, 12)
            pygame.draw.rect(self.surface, color, swatch, border_radius=3)

            text = self.small_font.render(label, True, Color.TEXT_SECONDARY)
            self.surface.blit(text, (x + 18, y))

            x += 18 + text.get_width() + 22

    def _render_control_panel(self) -> None:
        panel_rect = pygame.Rect(10, 70, 250, 500)
        draw_panel(self.surface, panel_rect, elevated=True)

        self._draw_text("TA Controls", (25, 80), self.control_font)

        self._draw_text(
            "Operations",
            (25, 115),
            self.section_font,
            color=Color.TEXT_SECONDARY,
        )

        self.randomize_button.render(self.surface)

        for button in self.operation_buttons:
            button.render(self.surface)

        self._draw_text(
            "Value:",
            (25, 290),
            self.section_font,
            color=Color.TEXT_SECONDARY,
        )

        self.value_input.render(self.surface)

        self._draw_text(
            "Simulation",
            (25, 355),
            self.section_font,
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

        if self.current_simulation is not None:
            state = self.simulator.state

            if state is not None:
                self._draw_text(
                    (
                        f"Step: {state.step + 1}/"
                        f"{len(self.current_simulation.states)}"
                    ),
                    (25, 469),
                    self.small_font,
                    color=Color.TEXT_MUTED,
                )

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
            (295, 82),
            self.section_font,
            color=Color.TEXT_SECONDARY,
        )

        state = self.simulator.state

        if state is None:
            description = "Select an operation to start a simulation."
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

    def _render_queue(self) -> None:
        """
        Render the queue horizontally.

        Index 0 is the FRONT of the queue and the largest index
        is the REAR.
        """

        values = tuple(self.model.to_list())
        state = self._get_simulation_state()

        front_index: int | None = None
        rear_index: int | None = None
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
            self._draw_empty_message()

        self._render_queue_items(
            values=values,
            front_index=front_index,
            rear_index=rear_index,
            created_value=created_value,
            removed_value=removed_value,
            peeked_value=peeked_value,
        )

        self._render_front_pointer(front_index=front_index, values=values)
        self._render_rear_pointer(rear_index=rear_index, values=values)

    def _draw_empty_message(self) -> None:
        area = pygame.Rect(280, 220, self.surface.get_width() - 300, 120)

        text = self.explanation_font.render(
            "Queue is empty. Enqueue a value to begin.",
            True,
            Color.TEXT_MUTED,
        )

        self.surface.blit(text, text.get_rect(center=area.center))

    def _render_front_pointer(
        self,
        front_index: int | None,
        values: tuple[object, ...],
    ) -> None:
        """Render the FRONT pointer for the current queue state."""

        self._draw_text(
            "FRONT",
            (self.queue_x, self.front_pointer_y),
            self.control_font,
            color=Color.ACCENT,
        )

        if front_index is None or not values:
            start = (self.queue_x + 35, self.front_pointer_y + 30)
            end = (self.queue_x + 35, self.queue_y - 5)

            pygame.draw.line(self.surface, Color.ACCENT, start, end, 3)
            self._draw_arrow_head(end, Color.ACCENT, "down")

            self._draw_text(
                "NULL",
                (self.queue_x + 50, self.queue_y - 25),
                self.pointer_font,
                color=Color.TEXT_SECONDARY,
            )

            return

        if front_index < 0 or front_index >= len(values):
            return

        item_x = self._get_item_x(front_index)

        start = (item_x + self.item_width // 2, self.front_pointer_y + 45)
        end = (item_x + self.item_width // 2, self.queue_y - 5)

        pygame.draw.line(self.surface, Color.ACCENT, start, end, 3)
        self._draw_arrow_head(end, Color.ACCENT, "down")

        self._draw_text(
            f"index {front_index}",
            (item_x + self.item_width // 2 - 25, self.front_pointer_y + 48),
            self.pointer_font,
            color=Color.TEXT_SECONDARY,
        )

    def _render_rear_pointer(
        self,
        rear_index: int | None,
        values: tuple[object, ...],
    ) -> None:
        """Render the REAR pointer for the current queue state."""

        if rear_index is None or not values:
            return

        if rear_index < 0 or rear_index >= len(values):
            return

        item_x = self._get_item_x(rear_index)

        text = self.control_font.render("REAR", True, Color.ACCENT)
        text_rect = text.get_rect(
            centerx=item_x + self.item_width // 2,
            bottom=self.front_pointer_y - 5,
        )
        self.surface.blit(text, text_rect)

        start = (item_x + self.item_width // 2, text_rect.bottom + 5)
        end = (item_x + self.item_width // 2, self.queue_y - 5)

        pygame.draw.line(self.surface, Color.ACCENT, start, end, 3)
        self._draw_arrow_head(end, Color.ACCENT, "down")

    def _render_queue_items(
        self,
        values: tuple[object, ...],
        front_index: int | None,
        rear_index: int | None,
        created_value: object | None,
        removed_value: object | None,
        peeked_value: object | None,
    ) -> None:
        for index, value in enumerate(values):
            x = self._get_item_x(index)

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
                self.surface,
                rect,
                background,
                self.item_font,
                value,
                caption_font=self.index_font,
                caption=f"index {index}",
            )

            if index < len(values) - 1:
                self._draw_queue_arrow(
                    x + self.item_width + 5,
                    self.queue_y + self.item_height // 2,
                )

        # An ENQUEUE item is deliberately detached from the queue.
        #
        # During the creation state the simulation still contains
        # only the old values, so the new item must not be rendered
        # as part of the queue yet.
        if created_value is not None:
            rect = pygame.Rect(
                self.queue_x,
                self.queue_y + 100,
                self.item_width,
                self.item_height,
            )

            draw_item_card(
                self.surface,
                rect,
                Color.STATE_SUCCESS,
                self.item_font,
                created_value,
                label_font=self.pointer_font,
                label="NEW",
            )

        # A DEQUEUE item is rendered separately while it is being
        # removed from the queue.
        if removed_value is not None:
            rect = pygame.Rect(
                self.queue_x,
                self.queue_y + 100,
                self.item_width,
                self.item_height,
            )

            draw_item_card(
                self.surface,
                rect,
                Color.STATE_DANGER,
                self.item_font,
                removed_value,
                label_font=self.pointer_font,
                label="REMOVED",
            )

    def _get_item_x(self, index: int) -> int:
        """Convert a queue index into a screen X coordinate."""

        return self.queue_x + index * (self.item_width + self.item_spacing)

    def _draw_queue_arrow(self, x: int, y: int) -> None:
        """Draw the arrow connecting two queue items."""

        end_x = x + self.item_spacing - 5

        pygame.draw.line(self.surface, Color.BORDER, (x, y), (end_x, y), 3)
        self._draw_arrow_head((end_x, y), Color.BORDER, "right")

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

        pygame.draw.polygon(self.surface, color, points)