import pygame

from algolab.simulation.simulator import Simulator
from algolab.topics.linked_list.model import LinkedListModel
from algolab.topics.linked_list.simulation import (
    LinkedListSimulation,
    LinkedListSimulator,
    VisitNodeEvent,
    CreateNodeEvent,
    UpdateHeadEvent,
    UpdateLinkEvent,
    UpdatePointerEvent,
    DeleteNodeEvent,
    CompleteOperationEvent,
)
from algolab.ui.components.button import Button
from algolab.ui.components.numeric_input import NumericInput
from algolab.ui.components.surface import draw_arrow, draw_panel, draw_toggle_button
from algolab.ui.screens.screen import Screen
from algolab.ui.theme import Color, Font, Radius


class LinkedListScreen(Screen):
    """Screen for visualizing singly linked list operations."""

    LEGEND = [
        (Color.STATE_ACTIVE, "Current"),
        (Color.STATE_COMPARING, "Comparing"),
        (Color.STATE_SUCCESS, "New"),
        (Color.STATE_DANGER, "Deleted"),
    ]

    POINTER_COLORS = {
        "previous": Color.STATE_COMPARING,
        "current": Color.STATE_ACTIVE,
        "new": Color.STATE_SUCCESS,
    }

    POINTER_LABELS = {
        "previous": "PREVIOUS",
        "current": "CURRENT",
        "new": "NEW",
    }

    def __init__(self, surface: pygame.Surface, on_back=None) -> None:
        super().__init__(surface, on_back)

        self.model = LinkedListModel()
        self.simulator = Simulator()
        self.linked_list_simulator = LinkedListSimulator(self.model)

        self.current_simulation: LinkedListSimulation | None = None
        self.operation_committed = False

        self.control_font = Font.H1()
        self.section_font = Font.H2()
        self.node_font = Font.NODE()
        self.small_font = Font.SMALL()
        self.explanation_font = Font.BODY()
        self.pointer_font = Font.LABEL()
        self.index_font = Font.LABEL()

        self.operation_buttons = self._create_operation_buttons()
        self.navigation_buttons = self._create_navigation_buttons()

        for index, button in enumerate(self.speed_buttons):
            button.rect = pygame.Rect(15 + index * 62, 491, 58, 28)

        self.value_input = NumericInput(pygame.Rect(135, 375, 75, 30), 10)
        self.index_input = NumericInput(pygame.Rect(135, 415, 75, 30), 0)

        self.step_timer = 0.0

        # A longer interval gives students time to understand each step.
        self.step_interval = 1.8

        # Temporary algorithmic pointers.
        #
        # These are different from HEAD and NEXT:
        #
        # previous -> temporary traversal pointer
        # current  -> temporary traversal pointer
        # new      -> temporary pointer to a newly created node
        #
        # None means the pointer is not currently active.
        self.algorithm_pointers: dict[str, int | None] = {
            "previous": None,
            "current": None,
            "new": None,
        }

        self._pointer_state_step: int | None = None

    def _create_operation_buttons(self) -> list[Button]:
        labels = [
            "Insert Beginning",
            "Insert End",
            "Insert At",
            "Delete At",
            "Search",
        ]

        variants = ["primary", "primary", "primary", "danger", "default"]

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
        y = 529
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
        if self.handle_back_event(event):
            return

        if self.handle_speed_event(event):
            return

        self.value_input.handle_event(event)
        self.index_input.handle_event(event)

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
        list_index = self.index_input.value

        try:
            if index == 0:
                simulation = self.linked_list_simulator.insert_at_beginning(value)
            elif index == 1:
                simulation = self.linked_list_simulator.insert_at_end(value)
            elif index == 2:
                simulation = self.linked_list_simulator.insert_at(list_index, value)
            elif index == 3:
                simulation = self.linked_list_simulator.delete_at(list_index)
            elif index == 4:
                simulation = self.linked_list_simulator.search(value)
            else:
                return
        except IndexError:
            return

        self.current_simulation = simulation
        self.operation_committed = False

        self.simulator.load_states(list(simulation.states))

        self.step_timer = 0.0

        self._reset_algorithm_pointers()

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

        self._rebuild_algorithm_pointers()
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
        self._reset_algorithm_pointers()

    def update(self, dt: float) -> None:
        self.update_back_button(dt)
        self.update_speed_buttons(dt)

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

            self._rebuild_algorithm_pointers()
            self._commit_if_finished()

    def render(self) -> None:
        self.surface.fill(Color.BG)

        self.render_back_button()
        self._render_control_panel()
        self._render_explanation_panel()
        self._render_legend()
        self._render_linked_list()

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
        panel_rect = pygame.Rect(10, 70, 250, 600)
        draw_panel(self.surface, panel_rect, elevated=True)

        self._draw_text("TA Controls", (25, 80), self.control_font)

        self._draw_text(
            "Operations",
            (25, 115),
            self.section_font,
            color=Color.TEXT_SECONDARY,
        )

        for button in self.operation_buttons:
            button.render(self.surface)

        self._draw_text(
            "Value:",
            (25, 380),
            self.section_font,
            color=Color.TEXT_SECONDARY,
        )

        self.value_input.render(self.surface)

        self._draw_text(
            "Index:",
            (25, 420),
            self.section_font,
            color=Color.TEXT_SECONDARY,
        )

        self.index_input.render(self.surface)

        self._draw_text(
            "Simulation",
            (25, 465),
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
                    (25, 579),
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

    def _get_event_info(self):
        state = self.simulator.state

        if state is None:
            return None

        events = state.events

        if not events:
            return None

        return events

    def _reset_algorithm_pointers(self) -> None:
        self.algorithm_pointers = {
            "previous": None,
            "current": None,
            "new": None,
        }

        self._pointer_state_step = None

    def _rebuild_algorithm_pointers(self) -> None:
        """
        Reconstruct algorithm-pointer positions from the simulation history.

        Pointer events describe movement rather than the complete pointer
        state, so we replay all events up to the current simulation state.
        This also makes backward navigation work correctly.
        """

        state = self.simulator.state

        if state is None:
            self._reset_algorithm_pointers()
            return

        current_step = state.step

        if self._pointer_state_step == current_step:
            return

        pointers = {
            "previous": None,
            "current": None,
            "new": None,
        }

        history_states = self.simulator.history._states

        for history_state in history_states:
            if history_state.step > current_step:
                break

            for event in history_state.events:
                if isinstance(event, UpdatePointerEvent):
                    if event.name in pointers:
                        pointers[event.name] = event.index

        self.algorithm_pointers = pointers
        self._pointer_state_step = current_step

    def _render_linked_list(self) -> None:
        # The visualization is intentionally positioned below the
        # explanation panel so HEAD and the algorithmic pointers do not
        # overlap with it.
        x = 320
        y = 420

        state = self._get_simulation_state()
        events = self._get_event_info()

        if state is None:
            values = tuple(self.model.to_list())
            current_index = None
            created_index = None
            deleted_index = None
            pointer_source = None
            pointer_target = None
            head_index = 0 if values else None

            self._reset_algorithm_pointers()
        else:
            values = state.values
            current_index = state.current_index
            created_index = state.created_index
            deleted_index = state.deleted_index

            pointer_source = None
            pointer_target = None
            head_index = 0 if values else None

            if events:
                for event in events:
                    if isinstance(event, UpdateLinkEvent):
                        pointer_source = event.index
                        pointer_target = event.next_index
                    elif isinstance(event, UpdateHeadEvent):
                        head_index = event.index
                    elif isinstance(event, VisitNodeEvent):
                        current_index = event.index
                    elif isinstance(event, CreateNodeEvent):
                        created_index = event.index
                    elif isinstance(event, DeleteNodeEvent):
                        deleted_index = event.index

            self._rebuild_algorithm_pointers()

        self._render_algorithm_pointers(x, y, values)
        self._render_head_pointer(x, y, head_index, values)

        if not values:
            self._draw_empty_message()
            return

        self._render_nodes(
            x,
            y,
            values,
            current_index,
            created_index,
            deleted_index,
            pointer_source,
            pointer_target,
        )

    def _draw_empty_message(self) -> None:
        area = pygame.Rect(280, 430, self.surface.get_width() - 300, 130)

        text = self.explanation_font.render(
            "List is empty. Insert a value to begin.",
            True,
            Color.TEXT_MUTED,
        )

        self.surface.blit(text, text.get_rect(center=area.center))

    def _render_algorithm_pointers(
        self,
        x: int,
        y: int,
        values: tuple[object, ...],
    ) -> None:
        """
        Draw temporary algorithmic pointers above the linked list.

        The pointers are deliberately separated from HEAD and NEXT because
        they represent variables used by the algorithm rather than actual
        links belonging to the data structure.
        """

        if not values:
            return

        node_width = 120
        spacing = 90

        # Separate horizontal lanes keep multiple pointers readable.
        lane_y = {
            "previous": y - 72,
            "current": y - 105,
            "new": y - 138,
        }

        for name in ("previous", "current", "new"):
            target_index = self.algorithm_pointers.get(name)

            if target_index is None:
                continue

            if target_index < 0 or target_index >= len(values):
                continue

            color = self.POINTER_COLORS[name]
            label = self.POINTER_LABELS[name]

            target_x = x + target_index * (node_width + spacing) + node_width // 2

            start = (target_x, lane_y[name])
            end = (target_x, y - 5)

            label_surface = self.pointer_font.render(
                f"{label} -> node {target_index}",
                True,
                color,
            )

            label_rect = label_surface.get_rect(
                centerx=start[0],
                bottom=start[1] - 5,
            )

            # Keep the label inside the right side of the screen.
            if label_rect.left < 280:
                label_rect.left = 280

            if label_rect.right > self.surface.get_width() - 10:
                label_rect.right = self.surface.get_width() - 10

            self.surface.blit(label_surface, label_rect)

            draw_arrow(self.surface, start, end, color)

            pygame.draw.circle(self.surface, color, (target_x, y - 5), 5)

    def _render_head_pointer(
        self,
        x: int,
        y: int,
        head_index: int | None,
        values: tuple[object, ...],
    ) -> None:
        self._draw_text(
            "HEAD",
            (x, y - 180),
            self.control_font,
            color=Color.ACCENT,
        )

        head_start = (x + 25, y - 145)

        if head_index is None or not values:
            head_end = (x + 25, y - 10)

            draw_arrow(self.surface, head_start, head_end, Color.ACCENT)

            self._draw_text(
                "NULL",
                (x + 40, y - 25),
                self.pointer_font,
                color=Color.TEXT_SECONDARY,
            )

            return

        node_width = 120
        spacing = 90

        target_x = x + head_index * (node_width + spacing)
        head_end = (target_x + node_width // 2, y - 5)

        draw_arrow(self.surface, head_start, head_end, Color.ACCENT)

        self._draw_text(
            f"node {head_index}",
            (x + 55, y - 130),
            self.pointer_font,
            color=Color.TEXT_SECONDARY,
        )

    def _render_nodes(
        self,
        x: int,
        y: int,
        values: tuple[object, ...],
        current_index: int | None,
        created_index: int | None,
        deleted_index: int | None,
        pointer_source: int | None,
        pointer_target: int | None,
    ) -> None:
        node_width = 120
        node_height = 70
        spacing = 90

        for index, value in enumerate(values):
            node_x = x + index * (node_width + spacing)

            rect = pygame.Rect(node_x, y, node_width, node_height)

            background = Color.STATE_DEFAULT

            if index == current_index:
                background = Color.STATE_ACTIVE

            if index == created_index:
                background = Color.STATE_SUCCESS

            if index == deleted_index:
                background = Color.STATE_DANGER

            if index == pointer_source:
                background = Color.STATE_COMPARING

            # Faint shadow for a hint of depth, matching BST/stack/queue.
            shadow_rect = rect.move(0, 3)
            pygame.draw.rect(self.surface, Color.BG, shadow_rect, border_radius=Radius.MD)

            pygame.draw.rect(self.surface, background, rect, border_radius=Radius.MD)

            border_color = tuple(min(255, channel + 45) for channel in background)

            # Give nodes targeted by temporary algorithm pointers a
            # brighter outline without replacing their normal node color.
            algorithm_pointer_names = [
                name
                for name, target in self.algorithm_pointers.items()
                if target == index
            ]

            if algorithm_pointer_names:
                border_color = Color.TEXT_PRIMARY

            pygame.draw.rect(self.surface, border_color, rect, 2, border_radius=Radius.MD)

            self._draw_node_contents(rect, index, value)

            self._render_next_pointer(
                rect,
                index,
                len(values),
                spacing,
                pointer_source,
                pointer_target,
            )

    def _draw_node_contents(
        self,
        rect: pygame.Rect,
        index: int,
        value: object,
    ) -> None:
        data_rect = pygame.Rect(
            rect.x,
            rect.y,
            int(rect.width * 0.55),
            rect.height,
        )

        next_rect = pygame.Rect(
            data_rect.right,
            rect.y,
            rect.width - data_rect.width,
            rect.height,
        )

        pygame.draw.line(
            self.surface,
            Color.BORDER,
            (data_rect.right, rect.top),
            (data_rect.right, rect.bottom),
            1,
        )

        index_text = self.index_font.render(f"node {index}", True, Color.TEXT_MUTED)
        index_rect = index_text.get_rect(
            centerx=data_rect.centerx,
            bottom=data_rect.bottom - 5,
        )
        self.surface.blit(index_text, index_rect)

        value_text = self.node_font.render(str(value), True, Color.TEXT_PRIMARY)
        value_rect = value_text.get_rect(
            centerx=data_rect.centerx,
            top=data_rect.top + 8,
        )
        self.surface.blit(value_text, value_rect)

        next_text = self.pointer_font.render("NEXT", True, Color.TEXT_SECONDARY)
        next_rect_text = next_text.get_rect(
            centerx=next_rect.centerx,
            top=next_rect.top + 10,
        )
        self.surface.blit(next_text, next_rect_text)

    def _render_next_pointer(
        self,
        rect: pygame.Rect,
        index: int,
        value_count: int,
        spacing: int,
        pointer_source: int | None,
        pointer_target: int | None,
    ) -> None:
        pointer_start = (rect.right, rect.centery)

        is_active_pointer = index == pointer_source

        if index < value_count - 1:
            next_x = rect.x + rect.width + spacing
            target_x = next_x + 10

            pointer_end = (target_x, rect.centery)

            pointer_color = Color.STATE_COMPARING if is_active_pointer else Color.BORDER
            width = 5 if is_active_pointer else 3

            draw_arrow(self.surface, pointer_start, pointer_end, pointer_color, width=width)

            target_label = pointer_target if is_active_pointer else index + 1

            self._draw_text(
                f"node {target_label}",
                (rect.right + 12, rect.y - 22),
                self.pointer_font,
                color=Color.TEXT_SECONDARY,
            )
        else:
            pointer_end = (rect.right + spacing - 10, rect.centery)

            pointer_color = Color.STATE_COMPARING if is_active_pointer else Color.BORDER
            width = 5 if is_active_pointer else 3

            draw_arrow(self.surface, pointer_start, pointer_end, pointer_color, width=width)

            self._draw_text(
                "NULL",
                (rect.right + 12, rect.y - 22),
                self.pointer_font,
                color=Color.TEXT_SECONDARY,
            )