from __future__ import annotations

import math

import pygame

from algolab.simulation.simulator import Simulator
from algolab.topics.graph.model import GraphModel
from algolab.topics.graph.simulation import (
    BFSSimulator,
    BellmanFordSimulator,
    DFSSimulator,
    DijkstraSimulator,
)
from algolab.ui.components.button import Button
from algolab.ui.components.numeric_input import NumericInput
from algolab.ui.components.surface import draw_arrow, draw_panel, draw_toggle_button
from algolab.ui.screens.screen import Screen
from algolab.ui.theme import Color, Font

NODE_RADIUS = 24


class GraphScreen(Screen):
    """
    Interactive graph editor and algorithm visualizer.

    There is deliberately no separate "edit mode" / "run mode"
    toggle. Instead, clicking nodes on the canvas builds a list of up
    to two selected nodes, which both edge editing (add/remove an
    edge between the two selected nodes) and algorithm running (the
    first selected node is the start node) read from. This keeps the
    control surface flat instead of doubling it behind a mode switch,
    at the cost of "selection" doing double duty, which is called out
    in the on-screen status text so it stays legible to a student.
    """

    ALGORITHMS = {
        "BFS": BFSSimulator,
        "DFS": DFSSimulator,
        "Dijkstra": DijkstraSimulator,
        "Bellman-Ford": BellmanFordSimulator,
    }

    def __init__(self, surface: pygame.Surface, on_back=None) -> None:
        super().__init__(surface, on_back)

        self.model = GraphModel(directed=False, weighted=False)
        self.simulator = Simulator()

        self.current_simulation = None
        self.operation_committed = False
        self.status_message: str | None = None
        self.error_message: str | None = None

        self.control_font = Font.H1()
        self.section_font = Font.H2()
        self.node_font = Font.get(18, bold=True)
        self.small_font = Font.SMALL()
        self.explanation_font = Font.BODY()
        self.label_font = Font.LABEL()

        self._label_counter = 0
        self.selected_nodes: list[int] = []

        self._mouse_down_node: int | None = None
        self._mouse_down_pos: tuple[int, int] | None = None
        self._is_dragging = False

        self.directed_buttons = self._create_toggle_buttons(
            160, "Undirected", "Directed"
        )
        self.weighted_buttons = self._create_toggle_buttons(
            204, "Unweighted", "Weighted"
        )

        self.edit_buttons = self._create_edit_buttons()
        self.algorithm_buttons = self._create_algorithm_buttons()
        self.navigation_buttons = self._create_navigation_buttons()

        self.weight_input = NumericInput(pygame.Rect(160, 391, 75, 30), 1)

        self.step_timer = 0.0
        self.step_interval = 1.4

    # ------------------------------------------------------------------
    # UI creation
    # ------------------------------------------------------------------

    def _create_toggle_buttons(
        self,
        y: int,
        off_label: str,
        on_label: str,
    ) -> list[Button]:
        return [
            Button(pygame.Rect(15, y, 110, 34), off_label),
            Button(pygame.Rect(130, y, 105, 34), on_label),
        ]

    def _create_edit_buttons(self) -> dict[str, Button]:
        return {
            "add_node": Button(
                pygame.Rect(15, 264, 110, 34), "Add Node", variant="primary"
            ),
            "remove_node": Button(
                pygame.Rect(130, 264, 105, 34), "Remove Node", variant="danger"
            ),
            "add_edge": Button(
                pygame.Rect(15, 302, 110, 34), "Add Edge", variant="primary"
            ),
            "remove_edge": Button(
                pygame.Rect(130, 302, 105, 34), "Remove Edge", variant="danger"
            ),
            "clear": Button(
                pygame.Rect(15, 340, 220, 34), "Clear Graph", variant="danger"
            ),
        }

    def _create_algorithm_buttons(self) -> dict[str, Button]:
        return {
            "BFS": Button(pygame.Rect(15, 464, 110, 34), "BFS"),
            "DFS": Button(pygame.Rect(130, 464, 105, 34), "DFS"),
            "Dijkstra": Button(pygame.Rect(15, 502, 110, 34), "Dijkstra"),
            "Bellman-Ford": Button(pygame.Rect(130, 502, 105, 34), "Bellman-Ford"),
        }

    def _create_navigation_buttons(self) -> list[Button]:
        labels = ["|<", "<", ">", ">|", "P"]

        buttons = []

        x = 15
        y = 602
        width = 40
        height = 35
        spacing = 45

        for index, label in enumerate(labels):
            buttons.append(
                Button(
                    pygame.Rect(x + index * spacing, y, width, height),
                    label,
                )
            )

        return buttons

    def _next_label(self) -> str:
        index = self._label_counter
        self._label_counter += 1

        letter = chr(ord("A") + index % 26)
        suffix = index // 26

        return f"{letter}{suffix}" if suffix else letter

    # ------------------------------------------------------------------
    # Canvas geometry
    # ------------------------------------------------------------------

    def _canvas_rect(self) -> pygame.Rect:
        return pygame.Rect(
            280,
            210,
            self.surface.get_width() - 300,
            self.surface.get_height() - 230,
        )

    def _relayout(self) -> None:
        rect = self._canvas_rect()
        radius = min(rect.width, rect.height) * 0.4

        self.model.recompute_layout(
            center_x=rect.centerx,
            center_y=rect.centery,
            radius=radius,
        )

    def _node_at(self, position: tuple[int, int]) -> int | None:
        if position[0] < 280:
            return None

        for node in self.model.nodes:
            distance = math.hypot(node.x - position[0], node.y - position[1])

            if distance <= NODE_RADIUS:
                return node.node_id

        return None

    # ------------------------------------------------------------------
    # Event handling
    # ------------------------------------------------------------------

    def handle_event(self, event: pygame.event.Event) -> None:
        if self.handle_back_event(event):
            return

        self.weight_input.handle_event(event)

        self._handle_canvas_event(event)

        for index, button in enumerate(self.directed_buttons):
            if button.handle_event(event):
                self._set_directed(index == 1)

        for index, button in enumerate(self.weighted_buttons):
            if button.handle_event(event):
                self._set_weighted(index == 1)

        if self.edit_buttons["add_node"].handle_event(event):
            self._add_node()

        if self.edit_buttons["remove_node"].handle_event(event):
            self._remove_selected_node()

        if self.edit_buttons["add_edge"].handle_event(event):
            self._add_edge()

        if self.edit_buttons["remove_edge"].handle_event(event):
            self._remove_edge()

        if self.edit_buttons["clear"].handle_event(event):
            self._clear_graph()

        for label, button in self.algorithm_buttons.items():
            if button.handle_event(event):
                self._run_algorithm(label)

        for index, button in enumerate(self.navigation_buttons):
            if button.handle_event(event):
                self._handle_navigation(index)

    def _handle_canvas_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            node_id = self._node_at(event.pos)

            if node_id is not None:
                self._mouse_down_node = node_id
                self._mouse_down_pos = event.pos
                self._is_dragging = False

        elif event.type == pygame.MOUSEMOTION and self._mouse_down_node is not None:
            if not self._is_dragging:
                dx = event.pos[0] - self._mouse_down_pos[0]
                dy = event.pos[1] - self._mouse_down_pos[1]

                if dx * dx + dy * dy > 25:
                    self._is_dragging = True

            if self._is_dragging:
                canvas = self._canvas_rect()

                x = max(
                    canvas.left + NODE_RADIUS,
                    min(canvas.right - NODE_RADIUS, event.pos[0]),
                )

                y = max(
                    canvas.top + NODE_RADIUS,
                    min(canvas.bottom - NODE_RADIUS, event.pos[1]),
                )

                self.model.move_node(self._mouse_down_node, x, y)

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self._mouse_down_node is not None:
                if not self._is_dragging and self.current_simulation is None:
                    self._toggle_selection(self._mouse_down_node)

                self._mouse_down_node = None
                self._is_dragging = False

    def _toggle_selection(self, node_id: int) -> None:
        if node_id in self.selected_nodes:
            self.selected_nodes.remove(node_id)
            return

        if len(self.selected_nodes) >= 2:
            self.selected_nodes = []

        self.selected_nodes.append(node_id)

    # ------------------------------------------------------------------
    # Editing actions
    # ------------------------------------------------------------------

    def _set_directed(self, directed: bool) -> None:
        if self.current_simulation is not None:
            return

        self.model.set_directed(directed)
        self.error_message = None

    def _set_weighted(self, weighted: bool) -> None:
        if self.current_simulation is not None:
            return

        self.model.set_weighted(weighted)
        self.error_message = None

    def _add_node(self) -> None:
        if self.current_simulation is not None:
            return

        self.model.add_node(label=self._next_label())
        self._relayout()
        self.error_message = None

    def _remove_selected_node(self) -> None:
        if self.current_simulation is not None:
            return

        if len(self.selected_nodes) != 1:
            self.error_message = "Select exactly one node to remove it."
            return

        node_id = self.selected_nodes[0]
        self.model.remove_node(node_id)
        self._relayout()

        self.selected_nodes = []
        self.error_message = None

    def _add_edge(self) -> None:
        if self.current_simulation is not None:
            return

        if len(self.selected_nodes) != 2:
            self.error_message = "Select exactly two nodes to add an edge."
            return

        source, target = self.selected_nodes
        weight = self.weight_input.value if self.model.weighted else 1.0

        try:
            self.model.add_edge(source, target, weight)
        except (KeyError, ValueError) as error:
            self.error_message = str(error)
            return

        self.selected_nodes = []
        self.error_message = None

    def _remove_edge(self) -> None:
        if self.current_simulation is not None:
            return

        if len(self.selected_nodes) != 2:
            self.error_message = "Select exactly two nodes to remove an edge."
            return

        source, target = self.selected_nodes

        try:
            self.model.remove_edge(source, target)
        except KeyError as error:
            self.error_message = str(error)
            return

        self.selected_nodes = []
        self.error_message = None

    def _clear_graph(self) -> None:
        if self.current_simulation is not None:
            return

        self.model.clear()
        self.selected_nodes = []
        self._label_counter = 0
        self.status_message = None
        self.error_message = None

    # ------------------------------------------------------------------
    # Algorithm running
    # ------------------------------------------------------------------

    def _run_algorithm(self, label: str) -> None:
        if self.current_simulation is not None:
            return

        if len(self.selected_nodes) != 1:
            self.error_message = (
                "Select exactly one node as the start node before "
                "running an algorithm."
            )
            return

        start_node_id = self.selected_nodes[0]
        simulator_class = self.ALGORITHMS[label]

        try:
            simulation = simulator_class(self.model).run(start_node_id)
        except (KeyError, ValueError) as error:
            self.error_message = str(error)
            return

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

        # Algorithms are read-only; commit() is a deliberate no-op, but
        # calling it keeps this screen's flow identical to every other
        # topic screen rather than special-casing graphs here.
        self.current_simulation.commit(self.model)

        self.operation_committed = True
        self.current_simulation = None

        self.simulator.reset()
        self.selected_nodes = []

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    def update(self, dt: float) -> None:
        self.update_back_button(dt)

        for button in self.directed_buttons:
            button.update(dt)

        for button in self.weighted_buttons:
            button.update(dt)

        for button in self.edit_buttons.values():
            button.update(dt)

        for button in self.algorithm_buttons.values():
            button.update(dt)

        self._sync_toggle_and_algorithm_buttons()

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
        self._render_graph()

    def _draw_text(
        self,
        text: str,
        position: tuple[int, int],
        font: pygame.font.Font,
        color: tuple[int, int, int] = Color.TEXT_PRIMARY,
    ) -> None:
        rendered = font.render(text, True, color)
        self.surface.blit(rendered, position)

    def _sync_toggle_and_algorithm_buttons(self) -> None:
        algorithm_enabled = (
            len(self.selected_nodes) == 1 and self.current_simulation is None
        )

        for button in self.algorithm_buttons.values():
            button.enabled = algorithm_enabled

    def _render_control_panel(self) -> None:
        panel_rect = pygame.Rect(10, 70, 250, 630)
        draw_panel(self.surface, panel_rect, elevated=True)

        self._draw_text("TA Controls", (25, 80), self.control_font)

        self._draw_text(
            "Graph Settings",
            (25, 120),
            self.section_font,
            color=Color.TEXT_SECONDARY,
        )

        self._render_toggle_row(self.directed_buttons, self.model.directed)
        self._render_toggle_row(self.weighted_buttons, self.model.weighted)

        for button in self.edit_buttons.values():
            button.render(self.surface)

        self._draw_text(
            "Edge Weight:",
            (15, 396),
            self.small_font,
            color=Color.TEXT_SECONDARY,
        )

        if self.model.weighted:
            self.weight_input.render(self.surface)
        else:
            self._draw_text(
                "1 (unweighted)",
                (160, 396),
                self.small_font,
                color=Color.TEXT_MUTED,
            )

        self._render_selection_status()

        for button in self.algorithm_buttons.values():
            button.render(self.surface)

        self._draw_text(
            "Simulation",
            (25, 562),
            self.section_font,
            color=Color.TEXT_SECONDARY,
        )

        for index, button in enumerate(self.navigation_buttons):
            if index == 4:
                draw_toggle_button(self.surface, button, self.simulator.running)
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
                    (15, 645),
                    self.small_font,
                    color=Color.TEXT_MUTED,
                )

    def _render_toggle_row(self, buttons: list[Button], active: bool) -> None:
        """
        Render a two-option on/off toggle (Directed/Undirected,
        Weighted/Unweighted) with the active option lit up green,
        using the same shared toggle style as the pause button.
        """

        for index, button in enumerate(buttons):
            is_on = (index == 1) == active
            draw_toggle_button(self.surface, button, is_on)

    def _render_selection_status(self) -> None:
        if self.error_message is not None:
            text = self.error_message
            color = Color.STATE_DANGER
        elif self.selected_nodes:
            labels = [
                self.model.get_node(node_id).label
                for node_id in self.selected_nodes
                if self.model.get_node(node_id) is not None
            ]
            text = "Selected: " + ", ".join(labels)
            color = Color.TEXT_SECONDARY
        else:
            text = "Click nodes to select them."
            color = Color.TEXT_MUTED

        area = pygame.Rect(15, 428, 220, 32)
        self._draw_wrapped_text(text, area, self.small_font, color)

    def _draw_wrapped_text(
        self,
        text: str,
        rect: pygame.Rect,
        font: pygame.font.Font,
        color: tuple[int, int, int],
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

        if state is not None:
            description = state.data.description
        elif self.status_message is not None:
            description = self.status_message
        else:
            description = (
                "Build a graph, then select one node and choose an "
                "algorithm to run it from there."
            )

        description_rect = pygame.Rect(295, 112, panel_rect.width - 30, 75)

        self._draw_wrapped_text(
            description,
            description_rect,
            self.explanation_font,
            Color.TEXT_SECONDARY,
        )

    def _get_algorithm_state(self):
        if self.simulator.state is None:
            return None

        return self.simulator.state.data

    def _render_graph(self) -> None:
        if self.model.is_empty:
            area = self._canvas_rect()
            text = self.explanation_font.render(
                "Graph is empty. Add a node to begin.",
                True,
                Color.TEXT_MUTED,
            )
            self.surface.blit(text, text.get_rect(center=area.center))
            return

        state = self._get_algorithm_state()

        self._render_edges(state)
        self._render_nodes(state)

    def _active_edge_matches(
        self,
        state,
        source: int,
        target: int,
    ) -> bool:
        if state is None or state.active_edge is None:
            return False

        if state.active_edge == (source, target):
            return True

        if not self.model.directed and state.active_edge == (target, source):
            return True

        return False

    def _render_edges(self, state) -> None:
        for edge in self.model.edges:
            source_node = self.model.get_node(edge.source)
            target_node = self.model.get_node(edge.target)

            if source_node is None or target_node is None:
                continue

            source_pos = (source_node.x, source_node.y)
            target_pos = (target_node.x, target_node.y)

            start, end = self._shrink_to_radius(source_pos, target_pos)

            active = self._active_edge_matches(state, edge.source, edge.target)

            color = Color.STATE_COMPARING if active else Color.BORDER
            width = 3 if active else 2

            if self.model.directed:
                draw_arrow(self.surface, start, end, color, width=width)
            else:
                pygame.draw.line(self.surface, color, start, end, width)

            if self.model.weighted:
                midpoint = (
                    (start[0] + end[0]) / 2,
                    (start[1] + end[1]) / 2,
                )

                weight_text = self.label_font.render(
                    f"{edge.weight:g}", True, Color.TEXT_SECONDARY
                )

                weight_rect = weight_text.get_rect(center=midpoint)

                pygame.draw.rect(
                    self.surface,
                    Color.BG,
                    weight_rect.inflate(6, 2),
                )

                self.surface.blit(weight_text, weight_rect)

    def _shrink_to_radius(
        self,
        source_pos: tuple[float, float],
        target_pos: tuple[float, float],
    ) -> tuple[tuple[float, float], tuple[float, float]]:
        dx = target_pos[0] - source_pos[0]
        dy = target_pos[1] - source_pos[1]
        distance = math.hypot(dx, dy) or 1.0

        unit_x, unit_y = dx / distance, dy / distance

        start = (
            source_pos[0] + unit_x * NODE_RADIUS,
            source_pos[1] + unit_y * NODE_RADIUS,
        )

        end = (
            target_pos[0] - unit_x * NODE_RADIUS,
            target_pos[1] - unit_y * NODE_RADIUS,
        )

        return start, end

    def _node_color(self, node_id: int, state) -> tuple[int, int, int]:
        if state is not None:
            if node_id == state.current_node:
                return Color.STATE_ACTIVE

            if node_id in state.visited:
                return Color.STATE_VISITED

            return Color.STATE_DEFAULT

        if node_id in self.selected_nodes:
            return Color.STATE_COMPARING

        return Color.STATE_DEFAULT

    def _render_nodes(self, state) -> None:
        for node in self.model.nodes:
            position = (int(node.x), int(node.y))
            color = self._node_color(node.node_id, state)

            pygame.draw.circle(self.surface, Color.BG, (position[0], position[1] + 2), NODE_RADIUS)
            pygame.draw.circle(self.surface, color, position, NODE_RADIUS)

            border_color = tuple(min(255, channel + 45) for channel in color)
            pygame.draw.circle(self.surface, border_color, position, NODE_RADIUS, 2)

            label_text = self.node_font.render(node.label, True, Color.TEXT_PRIMARY)
            self.surface.blit(label_text, label_text.get_rect(center=position))

            if state is not None and state.distances:
                distance = state.distances.get(node.node_id)

                if distance is not None and not math.isinf(distance):
                    distance_text = self.label_font.render(
                        f"d={distance:g}", True, Color.TEXT_SECONDARY
                    )

                    distance_rect = distance_text.get_rect(
                        centerx=position[0],
                        top=position[1] + NODE_RADIUS + 4,
                    )

                    self.surface.blit(distance_text, distance_rect)