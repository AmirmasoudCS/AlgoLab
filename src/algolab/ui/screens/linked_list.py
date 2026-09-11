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
from algolab.ui.screens.screen import Screen


class LinkedListScreen(Screen):
    def __init__(self, surface: pygame.Surface) -> None:
        super().__init__(surface)

        self.model = LinkedListModel()
        self.simulator = Simulator()
        self.linked_list_simulator = LinkedListSimulator(self.model)

        self.current_simulation: LinkedListSimulation | None = None
        self.operation_committed = False

        self.control_font = pygame.font.Font(None, 30)
        self.section_font = pygame.font.Font(None, 24)
        self.node_font = pygame.font.Font(None, 30)
        self.small_font = pygame.font.Font(None, 22)
        self.explanation_font = pygame.font.Font(None, 25)
        self.pointer_font = pygame.font.Font(None, 20)
        self.index_font = pygame.font.Font(None, 18)

        self.operation_buttons = self._create_operation_buttons()
        self.navigation_buttons = self._create_navigation_buttons()

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

        buttons = []
        x = 25
        y = 145
        width = 220
        height = 38
        spacing = 45

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
        y = 485
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
    ) -> None:
        rendered_text = font.render(text, True, (240, 240, 240))
        self.surface.blit(rendered_text, position)

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

            rendered_text = font.render(line, True, color)
            self.surface.blit(rendered_text, (rect.x, y))
            y += line_height

    def handle_event(self, event: pygame.event.Event) -> None:
        self.value_input.handle_event(event)
        self.index_input.handle_event(event)

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
                simulation = self.linked_list_simulator.insert_at_beginning(
                    value
                )
            elif index == 1:
                simulation = self.linked_list_simulator.insert_at_end(
                    value
                )
            elif index == 2:
                simulation = self.linked_list_simulator.insert_at(
                    list_index,
                    value,
                )
            elif index == 3:
                simulation = self.linked_list_simulator.delete_at(
                    list_index
                )
            elif index == 4:
                simulation = self.linked_list_simulator.search(value)
            else:
                return

        except IndexError:
            return

        self.current_simulation = simulation
        self.operation_committed = False

        self.simulator.load_states(
            list(simulation.states)
        )

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

            self._rebuild_algorithm_pointers()
            self._commit_if_finished()

    def render(self) -> None:
        self.surface.fill((30, 30, 30))

        self._render_control_panel()
        self._render_explanation_panel()
        self._render_linked_list()

    def _render_control_panel(self) -> None:
        pygame.draw.rect(
            self.surface,
            (40, 40, 40),
            pygame.Rect(10, 70, 250, 500),
            border_radius=8,
        )

        self._draw_text(
            "TA Controls",
            (25, 80),
            self.control_font,
        )

        self._draw_text(
            "Operations",
            (25, 115),
            self.section_font,
        )

        for button in self.operation_buttons:
            button.render(self.surface)

        self._draw_text(
            "Value:",
            (25, 380),
            self.section_font,
        )

        self.value_input.render(self.surface)

        self._draw_text(
            "Index:",
            (25, 420),
            self.section_font,
        )

        self.index_input.render(self.surface)

        self._draw_text(
            "Simulation",
            (25, 465),
            self.section_font,
        )

        for button in self.navigation_buttons:
            button.render(self.surface)

        if self.current_simulation is not None:
            state = self.simulator.state

            if state is not None:
                self._draw_text(
                    (
                        f"Step: {state.step + 1}/"
                        f"{len(self.current_simulation.states)}"
                    ),
                    (25, 535),
                    self.small_font,
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
        y = 390

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

        self._render_algorithm_pointers(
            x,
            y,
            values,
        )

        self._render_head_pointer(
            x,
            y,
            head_index,
            values,
        )

        if not values:
            self._draw_text(
                "NULL",
                (x, y),
                self.node_font,
            )
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

        active_pointers = [
            name
            for name, index in self.algorithm_pointers.items()
            if index is not None
        ]

        if not active_pointers:
            return

        node_width = 120
        node_height = 70
        spacing = 90

        pointer_colors = {
            "previous": (235, 165, 75),
            "current": (95, 165, 235),
            "new": (100, 200, 140),
        }

        pointer_labels = {
            "previous": "PREVIOUS",
            "current": "CURRENT",
            "new": "NEW",
        }

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

            color = pointer_colors[name]
            label = pointer_labels[name]

            target_x = (
                x
                + target_index * (node_width + spacing)
                + node_width // 2
            )

            start_x = target_x
            start_y = lane_y[name]

            end_x = target_x
            end_y = y - 5

            # Pointer label.
            label_surface = self.pointer_font.render(
                f"{label} -> node {target_index}",
                True,
                color,
            )

            label_rect = label_surface.get_rect(
                centerx=start_x,
                bottom=start_y - 5,
            )

            # Keep the label inside the right side of the screen.
            if label_rect.left < 280:
                label_rect.left = 280

            if label_rect.right > self.surface.get_width() - 10:
                label_rect.right = self.surface.get_width() - 10

            self.surface.blit(
                label_surface,
                label_rect,
            )

            pygame.draw.line(
                self.surface,
                color,
                (start_x, start_y),
                (end_x, end_y),
                3,
            )

            self._draw_arrow_head(
                (end_x, end_y),
                color,
                "down",
            )

            # Small marker at the target node.
            target_marker = pygame.Rect(
                target_x - 5,
                y - 5,
                10,
                10,
            )

            pygame.draw.circle(
                self.surface,
                color,
                target_marker.center,
                5,
            )

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
        )

        head_start = (x + 25, y - 145)

        if head_index is None or not values:
            head_end = (x + 25, y - 10)

            pygame.draw.line(
                self.surface,
                (100, 200, 140),
                head_start,
                head_end,
                3,
            )

            self._draw_arrow_head(
                head_end,
                (100, 200, 140),
                "down",
            )

            self._draw_text(
                "NULL",
                (x + 40, y - 25),
                self.pointer_font,
            )

            return

        node_width = 120
        node_height = 70
        spacing = 90

        target_x = (
            x
            + head_index * (node_width + spacing)
        )

        head_end = (
            target_x + node_width // 2,
            y - 5,
        )

        pygame.draw.line(
            self.surface,
            (100, 200, 140),
            head_start,
            head_end,
            3,
        )

        self._draw_arrow_head(
            head_end,
            (100, 200, 140),
            "down",
        )

        self._draw_text(
            f"node {head_index}",
            (x + 55, y - 130),
            self.pointer_font,
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

            rect = pygame.Rect(
                node_x,
                y,
                node_width,
                node_height,
            )

            background = (65, 85, 115)

            if index == current_index:
                background = (70, 110, 180)

            if index == created_index:
                background = (65, 150, 105)

            if index == deleted_index:
                background = (165, 75, 75)

            if index == pointer_source:
                background = (180, 135, 55)

            pygame.draw.rect(
                self.surface,
                background,
                rect,
                border_radius=8,
            )

            border_color = (210, 210, 210)

            if index == pointer_source:
                border_color = (255, 215, 90)

            # Give nodes targeted by temporary algorithm pointers a subtle
            # outer outline without replacing their normal node colors.
            algorithm_pointer_names = [
                name
                for name, target in self.algorithm_pointers.items()
                if target == index
            ]

            if algorithm_pointer_names:
                border_color = (235, 235, 235)

            pygame.draw.rect(
                self.surface,
                border_color,
                rect,
                2,
                border_radius=8,
            )

            self._draw_node_contents(
                rect,
                index,
                value,
            )

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
            (180, 180, 180),
            (data_rect.right, rect.top),
            (data_rect.right, rect.bottom),
            1,
        )

        index_text = self.index_font.render(
            f"node {index}",
            True,
            (200, 200, 200),
        )

        index_rect = index_text.get_rect(
            centerx=data_rect.centerx,
            bottom=data_rect.bottom - 5,
        )

        self.surface.blit(
            index_text,
            index_rect,
        )

        value_text = self.node_font.render(
            str(value),
            True,
            (245, 245, 245),
        )

        value_rect = value_text.get_rect(
            centerx=data_rect.centerx,
            top=data_rect.top + 8,
        )

        self.surface.blit(
            value_text,
            value_rect,
        )

        next_text = self.pointer_font.render(
            "NEXT",
            True,
            (215, 215, 215),
        )

        next_rect_text = next_text.get_rect(
            centerx=next_rect.centerx,
            top=next_rect.top + 10,
        )

        self.surface.blit(
            next_text,
            next_rect_text,
        )

    def _render_next_pointer(
        self,
        rect: pygame.Rect,
        index: int,
        value_count: int,
        spacing: int,
        pointer_source: int | None,
        pointer_target: int | None,
    ) -> None:
        pointer_start = (
            rect.right,
            rect.centery,
        )

        is_active_pointer = index == pointer_source

        if index < value_count - 1:
            next_x = (
                rect.x
                + rect.width
                + spacing
            )

            target_x = next_x + 10

            pointer_end = (
                target_x,
                rect.centery,
            )

            if is_active_pointer:
                pointer_color = (255, 215, 90)
                width = 5
            else:
                pointer_color = (150, 180, 210)
                width = 3

            pygame.draw.line(
                self.surface,
                pointer_color,
                pointer_start,
                pointer_end,
                width,
            )

            self._draw_arrow_head(
                pointer_end,
                pointer_color,
                "right",
            )

            target_label = (
                pointer_target
                if is_active_pointer
                else index + 1
            )

            self._draw_text(
                f"node {target_label}",
                (
                    rect.right + 12,
                    rect.y - 22,
                ),
                self.pointer_font,
            )

        else:
            pointer_end = (
                rect.right + spacing - 10,
                rect.centery,
            )

            if is_active_pointer:
                pointer_color = (255, 215, 90)
                width = 5
            else:
                pointer_color = (150, 180, 210)
                width = 3

            pygame.draw.line(
                self.surface,
                pointer_color,
                pointer_start,
                pointer_end,
                width,
            )

            self._draw_arrow_head(
                pointer_end,
                pointer_color,
                "right",
            )

            self._draw_text(
                "NULL",
                (
                    rect.right + 12,
                    rect.y - 22,
                ),
                self.pointer_font,
            )

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

        pygame.draw.polygon(
            self.surface,
            color,
            points,
        )