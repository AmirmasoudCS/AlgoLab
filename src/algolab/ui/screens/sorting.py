from __future__ import annotations

import pygame

from algolab.simulation.simulator import Simulator
from algolab.topics.sorting.model import SortArray
from algolab.topics.sorting.operations import ClearOperation, RandomizeOperation
from algolab.topics.sorting.simulation import (
    BubbleSortSimulator,
    HeapSortSimulator,
    InsertionSortSimulator,
    MergeSortSimulator,
    QuickSortSimulator,
    SelectionSortSimulator,
)
from algolab.ui.components.button import Button
from algolab.ui.components.info_panel import InfoPanel
from algolab.ui.components.numeric_input import NumericInput
from algolab.ui.components.surface import draw_panel, draw_toggle_button
from algolab.ui.screens.screen import Screen
from algolab.ui.theme import Color, Font


class SortingScreen(Screen):
    """Screen for visualizing sorting algorithms as a bar chart."""

    ALGORITHMS = {
        "Bubble": BubbleSortSimulator,
        "Selection": SelectionSortSimulator,
        "Insertion": InsertionSortSimulator,
        "Merge": MergeSortSimulator,
        "Quick": QuickSortSimulator,
        "Heap": HeapSortSimulator,
    }

    LEGEND = [
        (Color.STATE_COMPARING, "Comparing"),
        (Color.STATE_ACTIVE, "Swapping"),
        (Color.STATE_REPLACE, "Pivot"),
        (Color.STATE_SUCCESS, "Sorted"),
    ]

    def __init__(self, surface: pygame.Surface, on_back=None) -> None:
        super().__init__(surface, on_back)

        self.model = SortArray()
        self.model.randomize(size=10, minimum=5, maximum=95)

        self.simulator = Simulator()

        self.current_simulation = None
        self.operation_committed = False
        self.status_message: str | None = None
        self.error_message: str | None = None

        self.control_font = Font.H1()
        self.section_font = Font.H2()
        self.small_font = Font.SMALL()
        self.explanation_font = Font.BODY()
        self.label_font = Font.LABEL()
        self.value_font = Font.LABEL()

        self.size_input = NumericInput(pygame.Rect(160, 147, 75, 30), 10)
        self.value_input = NumericInput(pygame.Rect(160, 219, 75, 30), 50)

        self.randomize_button = Button(pygame.Rect(15, 181, 220, 34), "Randomize", variant="primary")
        self.add_button = Button(pygame.Rect(15, 253, 220, 34), "Add Value", variant="primary")
        self.clear_button = Button(pygame.Rect(15, 291, 220, 34), "Clear", variant="danger")

        self.info_button = Button(
            pygame.Rect(surface.get_width() - 115, 15, 100, 38),
            "Info",
        )
        self.info_panel = InfoPanel(
            "Sorting — Time Complexity",
            [
                ("Bubble Sort", "O(n) best", "O(n^2) avg/worst"),
                ("Selection Sort", "O(n^2)", "Same in every case"),
                ("Insertion Sort", "O(n) best", "O(n^2) avg/worst"),
                ("Merge Sort", "O(n log n)", "Same in every case"),
                ("Quick Sort", "O(n log n) avg", "O(n^2) worst (bad pivots)"),
                ("Heap Sort", "O(n log n)", "Same in every case"),
            ],
        )

        self.algorithm_buttons = self._create_algorithm_buttons()
        self.navigation_buttons = self._create_navigation_buttons()

        for index, button in enumerate(self.speed_buttons):
            button.rect = pygame.Rect(15 + index * 62, 562, 58, 28)

        self.step_timer = 0.0
        self.step_interval = 0.5

    # ------------------------------------------------------------------
    # UI creation
    # ------------------------------------------------------------------

    def _create_algorithm_buttons(self) -> dict[str, Button]:
        labels = list(self.ALGORITHMS.keys())
        buttons = {}

        for index, label in enumerate(labels):
            row = index // 2
            column = index % 2

            x = 15 if column == 0 else 130
            width = 110 if column == 0 else 105
            y = 400 + row * 38

            buttons[label] = Button(pygame.Rect(x, y, width, 34), label)

        return buttons

    def _create_navigation_buttons(self) -> list[Button]:
        labels = ["|<", "<", ">", ">|", "P"]

        buttons = []
        x = 15
        y = 600
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

        if self.handle_back_event(event):
            return

        if self.handle_speed_event(event):
            return

        self.size_input.handle_event(event)
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

        if self.randomize_button.handle_event(event):
            self._randomize()

        if self.add_button.handle_event(event):
            self._add_value()

        if self.clear_button.handle_event(event):
            self._clear_array()

        if self.info_button.handle_event(event):
            self.info_panel.open()

        for label, button in self.algorithm_buttons.items():
            if button.handle_event(event):
                self._run_algorithm(label)

        for index, button in enumerate(self.navigation_buttons):
            if button.handle_event(event):
                self._handle_navigation(index)

    def _cancel_current_simulation(self) -> None:
        """
        Discard any in-progress simulation.

        Editing the array (randomizing, adding a value, clearing it)
        makes an in-flight animation meaningless, since it was
        animating a sort of the *old* array. Rather than silently
        refusing the edit while a simulation is active, cancel it and
        apply the edit immediately.
        """

        if self.current_simulation is not None:
            self.simulator.reset()
            self.current_simulation = None
            self.operation_committed = False

    def _randomize(self) -> None:
        self._cancel_current_simulation()

        size = max(1, min(60, self.size_input.value))

        try:
            RandomizeOperation(size, 5, 95).commit(self.model)
        except ValueError as error:
            self.error_message = str(error)
            return

        self.status_message = None
        self.error_message = None

    def _add_value(self) -> None:
        self._cancel_current_simulation()

        if self.model.size >= 60:
            self.error_message = "That's plenty of bars for one screen. Clear first to add more."
            return

        self.model.append(self.value_input.value)

        self.status_message = None
        self.error_message = None

    def _clear_array(self) -> None:
        self._cancel_current_simulation()

        ClearOperation().commit(self.model)

        self.status_message = None
        self.error_message = None

    def _run_algorithm(self, label: str) -> None:
        if self.current_simulation is not None:
            return

        if self.model.is_empty:
            self.error_message = "Add or randomize some values first."
            return

        simulator_class = self.ALGORITHMS[label]
        simulation = simulator_class().run(self.model.values)

        self.current_simulation = simulation
        self.operation_committed = False
        self.status_message = None
        self.error_message = None

        self.simulator.load_states(list(simulation.states))

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
        self.add_button.update(dt)
        self.clear_button.update(dt)

        self.info_button.update(dt)

        algorithms_enabled = self.current_simulation is None and not self.model.is_empty

        for button in self.algorithm_buttons.values():
            button.enabled = algorithms_enabled
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
        self._render_bars()

        self.info_button.render(self.surface)
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
        panel_rect = pygame.Rect(10, 70, 250, 630)
        draw_panel(self.surface, panel_rect, elevated=True)

        self._draw_text("TA Controls", (25, 80), self.control_font)

        self._draw_text(
            "Build Array", (25, 112), self.section_font, color=Color.TEXT_SECONDARY
        )

        self._draw_text("Size:", (15, 152), self.small_font, color=Color.TEXT_SECONDARY)
        self.size_input.render(self.surface)

        self.randomize_button.render(self.surface)

        self._draw_text("Value:", (15, 224), self.small_font, color=Color.TEXT_SECONDARY)
        self.value_input.render(self.surface)

        self.add_button.render(self.surface)
        self.clear_button.render(self.surface)

        self._draw_text(
            "Algorithm", (25, 360), self.section_font, color=Color.TEXT_SECONDARY
        )

        for button in self.algorithm_buttons.values():
            button.render(self.surface)

        self._draw_text(
            "Simulation", (25, 536), self.section_font, color=Color.TEXT_SECONDARY
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

        if self.current_simulation is not None:
            state = self.simulator.state

            if state is not None:
                self._draw_text(
                    f"Step: {state.step + 1}/{len(self.current_simulation.states)}",
                    (15, 651),
                    self.small_font,
                    color=Color.TEXT_MUTED,
                )
        else:
            status = "Sorted" if self.model.is_sorted else "Not sorted"
            info = f"Size: {self.model.size}   {status}"
            self._draw_text(info, (15, 651), self.small_font, color=Color.TEXT_MUTED)

    def _render_explanation_panel(self) -> None:
        panel_rect = pygame.Rect(280, 70, self.surface.get_width() - 300, 130)
        draw_panel(self.surface, panel_rect, elevated=False)

        self._draw_text(
            "What is happening?", (295, 82), self.section_font, color=Color.TEXT_SECONDARY
        )

        description_rect = pygame.Rect(295, 112, panel_rect.width - 30, 75)

        state = self._get_state()

        if state is not None:
            self._draw_wrapped_text(state.description, description_rect, self.explanation_font)
        elif self.error_message is not None:
            self._draw_wrapped_text(
                self.error_message, description_rect, self.explanation_font, Color.STATE_DANGER
            )
        elif self.status_message is not None:
            self._draw_wrapped_text(self.status_message, description_rect, self.explanation_font)
        else:
            self._draw_wrapped_text(
                "Randomize or add values, then choose an algorithm to sort them.",
                description_rect,
                self.explanation_font,
            )

    def _get_state(self):
        if self.simulator.state is None:
            return None
        return self.simulator.state.data

    def _render_legend(self) -> None:
        x = 280
        y = 212

        for color, label in self.LEGEND:
            swatch = pygame.Rect(x, y + 3, 12, 12)
            pygame.draw.rect(self.surface, color, swatch, border_radius=3)

            text = self.label_font.render(label, True, Color.TEXT_SECONDARY)
            self.surface.blit(text, (x + 18, y))

            x += 18 + text.get_width() + 22

    # ------------------------------------------------------------------
    # Bar chart
    # ------------------------------------------------------------------

    def _canvas_rect(self) -> pygame.Rect:
        return pygame.Rect(
            280, 238, self.surface.get_width() - 300, self.surface.get_height() - 278
        )

    def _bar_color(self, index: int, state) -> tuple[int, int, int]:
        if state is None:
            return Color.STATE_DEFAULT

        if index == state.pivot_index:
            return Color.STATE_REPLACE

        if index in state.swapping:
            return Color.STATE_ACTIVE

        if index in state.comparing:
            return Color.STATE_COMPARING

        if index in state.sorted_indices:
            return Color.STATE_SUCCESS

        return Color.STATE_DEFAULT

    def _render_bars(self) -> None:
        state = self._get_state()
        values = list(state.values) if state is not None else self.model.values

        if not values:
            canvas = self._canvas_rect()
            text = self.explanation_font.render(
                "Array is empty. Randomize or add values to begin.",
                True,
                Color.TEXT_MUTED,
            )
            self.surface.blit(text, text.get_rect(center=canvas.center))
            return

        canvas = self._canvas_rect()

        n = len(values)
        gap = 4
        bar_width = max(4, (canvas.width - gap * (n - 1)) // n)
        max_value = max(values) or 1

        # Active subarray highlight (merge/quick sort), drawn first so
        # bars render on top of it.
        if state is not None and state.active_range is not None:
            low, high = state.active_range
            band_left = canvas.left + low * (bar_width + gap)
            band_width = (high - low) * (bar_width + gap) - gap

            if band_width > 0:
                band_rect = pygame.Rect(band_left, canvas.top, band_width, canvas.height)
                pygame.draw.rect(self.surface, Color.SURFACE_RAISED, band_rect, border_radius=6)

        for index, value in enumerate(values):
            bar_height = int((value / max_value) * (canvas.height - 30))
            bar_height = max(bar_height, 4)

            x = canvas.left + index * (bar_width + gap)
            y = canvas.bottom - bar_height

            rect = pygame.Rect(x, y, bar_width, bar_height)
            color = self._bar_color(index, state)

            pygame.draw.rect(self.surface, color, rect, border_radius=3)

            if bar_width >= 18:
                value_text = self.value_font.render(str(value), True, Color.TEXT_SECONDARY)

                if value_text.get_width() <= bar_width + 10:
                    value_rect = value_text.get_rect(centerx=rect.centerx, bottom=rect.top - 3)
                    self.surface.blit(value_text, value_rect)