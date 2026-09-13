import pygame

from algolab.simulation.simulator import Simulator
from algolab.topics.bst.model import BinarySearchTree
from algolab.topics.bst.simulation import (
    BSTSimulation,
    BSTSimulator,
    CompareNodeEvent,
    VisitBSTNodeEvent,
    CreateBSTNodeEvent,
    DeleteBSTNodeEvent,
    ReplaceNodeValueEvent,
)
from algolab.ui.components.button import Button
from algolab.ui.components.numeric_input import NumericInput
from algolab.ui.screens.screen import Screen


class BSTScreen(Screen):
    """Binary search tree visualization screen."""

    def __init__(self, surface: pygame.Surface) -> None:
        super().__init__(surface)

        self.model = BinarySearchTree()
        self.simulator = Simulator()
        self.bst_simulator = BSTSimulator(self.model)

        self.current_simulation: BSTSimulation | None = None
        self.operation_committed = False

        # Message shown after an operation finishes.
        self.status_message: str | None = None

        self.control_font = pygame.font.Font(None, 30)
        self.section_font = pygame.font.Font(None, 24)
        self.node_font = pygame.font.Font(None, 28)
        self.small_font = pygame.font.Font(None, 22)
        self.explanation_font = pygame.font.Font(None, 25)
        self.edge_font = pygame.font.Font(None, 18)

        self.operation_buttons = self._create_operation_buttons()
        self.navigation_buttons = self._create_navigation_buttons()

        self.value_input = NumericInput(
            pygame.Rect(135, 475, 75, 30),
            50,
        )

        self.step_timer = 0.0
        self.step_interval = 1.8

    def _create_operation_buttons(self) -> list[Button]:
        labels = [
            "Insert",
            "Search",
            "Delete",
            "Find Min",
            "Find Max",
            "In-Order",
            "Pre-Order",
            "Post-Order",
        ]

        buttons = []

        x = 25
        y = 145
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
        y = 565
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

    def handle_event(self, event: pygame.event.Event) -> None:
        self.value_input.handle_event(event)

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

        try:
            if index == 0:
                simulation = self.bst_simulator.insert(value)

            elif index == 1:
                simulation = self.bst_simulator.search(value)

            elif index == 2:
                simulation = self.bst_simulator.delete(value)

            elif index == 3:
                simulation = self.bst_simulator.find_min()

            elif index == 4:
                simulation = self.bst_simulator.find_max()

            elif index == 5:
                simulation = self.bst_simulator.in_order()

            elif index == 6:
                simulation = self.bst_simulator.pre_order()

            elif index == 7:
                simulation = self.bst_simulator.post_order()

            else:
                return

        except (IndexError, ValueError):
            return

        self.current_simulation = simulation
        self.operation_committed = False
        self.status_message = None

        self.simulator.load_states(
            list(simulation.states)
        )

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

    def render(self) -> None:
        self.surface.fill((30, 30, 30))

        self._render_control_panel()
        self._render_explanation_panel()
        self._render_tree()

    def _render_control_panel(self) -> None:
        pygame.draw.rect(
            self.surface,
            (40, 40, 40),
            pygame.Rect(10, 70, 250, 620),
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
            (25, 480),
            self.section_font,
        )

        self.value_input.render(self.surface)

        self._draw_text(
            "Simulation",
            (25, 535),
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
                    (25, 610),
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

    def _get_simulation_state(self):
        if self.simulator.state is None:
            return None

        return self.simulator.state.data

    def _get_events(self):
        if self.simulator.state is None:
            return ()

        return self.simulator.state.events

    def _build_node_map(self, state):
        if state is None:
            return {}

        nodes = state.nodes

        if isinstance(nodes, dict):
            return dict(nodes)

        return {
            node.node_id: node
            for node in nodes
        }

    def _render_tree(self) -> None:
        state = self._get_simulation_state()

        if state is None:
            root = self.model.root

            if root is None:
                self._draw_text(
                    "Tree is empty.",
                    (600, 350),
                    self.explanation_font,
                )
                return

            node_map = self._build_model_node_map(root)

            root_id = id(root)

            self._render_tree_structure(
                node_map,
                root_id,
                None,
                None,
                None,
            )

            return

        node_map = self._build_node_map(state)

        if state.root_id is None:
            self._draw_text(
                "Tree is empty.",
                (600, 350),
                self.explanation_font,
            )
            return

        events = self._get_events()

        active_node_id = state.active_node_id
        created_node_id = state.created_node_id
        removed_node_id = state.removed_node_id
        result_node_id = state.result_node_id

        compare_node_ids = set()
        visited_node_ids = set(state.visited_node_ids)

        replacement_node_id = None

        for event in events:
            if isinstance(event, CompareNodeEvent):
                compare_node_ids.add(event.node_id)

            elif isinstance(event, VisitBSTNodeEvent):
                visited_node_ids.add(event.node_id)

            elif isinstance(event, CreateBSTNodeEvent):
                created_node_id = event.node_id

            elif isinstance(event, DeleteBSTNodeEvent):
                removed_node_id = event.node_id

            elif isinstance(event, ReplaceNodeValueEvent):
                replacement_node_id = event.node_id

        self._render_tree_structure(
            node_map,
            state.root_id,
            active_node_id,
            created_node_id,
            removed_node_id,
            compare_node_ids,
            visited_node_ids,
            result_node_id,
            replacement_node_id,
        )

        if state.traversal_values:
            self._render_traversal_result(
                state.traversal_values
            )

    def _build_model_node_map(self, root):
        node_map = {}

        def visit(node):
            if node is None:
                return

            node_id = id(node)

            left_id = (
                id(node.left)
                if node.left is not None
                else None
            )

            right_id = (
                id(node.right)
                if node.right is not None
                else None
            )

            node_map[node_id] = type(
                "ModelNodeState",
                (),
                {
                    "node_id": node_id,
                    "value": node.value,
                    "left_id": left_id,
                    "right_id": right_id,
                },
            )()

            visit(node.left)
            visit(node.right)

        visit(root)

        return node_map

    def _calculate_positions(
        self,
        node_map,
        root_id,
    ):
        positions = {}

        if root_id is None or root_id not in node_map:
            return positions

        node_width = 90
        horizontal_spacing = 35
        level_height = 85

        available_left = 315
        available_right = self.surface.get_width() - 25

        available_width = (
            available_right - available_left
        )

        order = []

        def inorder(node_id, depth):
            if node_id is None:
                return

            node = node_map.get(node_id)

            if node is None:
                return

            inorder(node.left_id, depth + 1)

            order.append(
                (node_id, depth)
            )

            inorder(node.right_id, depth + 1)

        inorder(root_id, 0)

        if not order:
            return positions

        node_count = len(order)

        max_spacing = (
            node_width
            + horizontal_spacing
        )

        required_width = (
            node_count * max_spacing
        )

        spacing = horizontal_spacing

        if required_width > available_width:
            spacing = max(
                15,
                (
                    available_width
                    - node_count * node_width
                )
                / max(1, node_count - 1),
            )

        total_width = (
            node_count * node_width
            + max(0, node_count - 1) * spacing
        )

        start_x = (
            available_left
            + max(
                0,
                int(
                    (available_width - total_width)
                    / 2
                ),
            )
        )

        for index, (node_id, depth) in enumerate(order):
            x = (
                start_x
                + index * (node_width + spacing)
            )

            y = 240 + depth * level_height

            positions[node_id] = pygame.Rect(
                int(x),
                int(y),
                node_width,
                55,
            )

        return positions

    def _render_tree_structure(
        self,
        node_map,
        root_id,
        active_node_id=None,
        created_node_id=None,
        removed_node_id=None,
        compare_node_ids=None,
        visited_node_ids=None,
        result_node_id=None,
        replacement_node_id=None,
    ) -> None:
        if not node_map:
            return

        compare_node_ids = (
            compare_node_ids
            if compare_node_ids is not None
            else set()
        )

        visited_node_ids = (
            visited_node_ids
            if visited_node_ids is not None
            else set()
        )

        positions = self._calculate_positions(
            node_map,
            root_id,
        )

        if not positions:
            return

        # Draw edges first so they remain behind the nodes.
        for node_id, node in node_map.items():
            if node_id not in positions:
                continue

            source_rect = positions[node_id]

            if node.left_id is not None:
                self._draw_tree_edge(
                    source_rect,
                    positions.get(node.left_id),
                    "left",
                )

            if node.right_id is not None:
                self._draw_tree_edge(
                    source_rect,
                    positions.get(node.right_id),
                    "right",
                )

        for node_id, node in node_map.items():
            rect = positions.get(node_id)

            if rect is None:
                continue

            background = (65, 85, 115)

            if node_id in visited_node_ids:
                background = (80, 110, 160)

            if node_id in compare_node_ids:
                background = (180, 135, 55)

            if node_id == active_node_id:
                background = (70, 110, 180)

            if node_id == created_node_id:
                background = (65, 150, 105)

            if node_id == removed_node_id:
                background = (165, 75, 75)

            if node_id == result_node_id:
                background = (100, 150, 100)

            if node_id == replacement_node_id:
                background = (150, 105, 175)

            border_color = (210, 210, 210)

            if node_id in compare_node_ids:
                border_color = (255, 215, 90)

            if node_id == result_node_id:
                border_color = (150, 235, 150)

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
                str(node.value),
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

            node_id_text = self.edge_font.render(
                f"id {node.node_id}",
                True,
                (190, 190, 190),
            )

            node_id_rect = node_id_text.get_rect(
                centerx=rect.centerx,
                top=rect.bottom + 4,
            )

            self.surface.blit(
                node_id_text,
                node_id_rect,
            )

    def _draw_tree_edge(
        self,
        source_rect: pygame.Rect,
        target_rect: pygame.Rect | None,
        side: str,
    ) -> None:
        if target_rect is None:
            return

        start = (
            source_rect.centerx,
            source_rect.bottom,
        )

        end = (
            target_rect.centerx,
            target_rect.top,
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
            "down",
        )

    def _draw_arrow_head(
        self,
        position: tuple[int, int],
        color: tuple[int, int, int],
        direction: str,
    ) -> None:
        x, y = position
        size = 7

        if direction == "down":
            points = [
                (x, y),
                (x - size, y - size),
                (x + size, y - size),
            ]

        else:
            return

        pygame.draw.polygon(
            self.surface,
            color,
            points,
        )

    def _render_traversal_result(
        self,
        values,
    ) -> None:
        text = (
            "Result: "
            + " -> ".join(
                str(value)
                for value in values
            )
        )

        rect = pygame.Rect(
            300,
            self.surface.get_height() - 55,
            self.surface.get_width() - 325,
            35,
        )

        pygame.draw.rect(
            self.surface,
            (40, 40, 40),
            rect,
            border_radius=6,
        )

        self._draw_text(
            text,
            (rect.x + 10, rect.y + 7),
            self.small_font,
        )