from __future__ import annotations

import math
import random

import pygame

from algolab.simulation.simulator import Simulator
from algolab.topics.graph.model import GraphEdge, GraphModel
from algolab.topics.graph.simulation import (
    BFSSimulator,
    BellmanFordSimulator,
    DFSSimulator,
    DijkstraSimulator,
)
from algolab.ui.components.button import Button
from algolab.ui.components.info_panel import InfoPanel
from algolab.ui.components.numeric_input import NumericInput
from algolab.ui.components.storage_controls import StorageControls
from algolab.ui.components.surface import draw_arrow, draw_panel, draw_toggle_button
from algolab.ui.screens.screen import Screen
from algolab.ui.theme import Color, Font

NODE_RADIUS = 24

# How close (in pixels) a click must be to an edge's line to hit it.
EDGE_HIT_DISTANCE = 8

# A hand-placed node must be at least this far from every other node's
# center: two radii plus a small gap, so circles never overlap.
MIN_NODE_DISTANCE = NODE_RADIUS * 2 + 6

# How many edits Undo can step back through.
MAX_UNDO_STEPS = 50


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

    Drawing by hand uses a small tool palette:

    select  click a node to select it, drag to move it, click empty
            canvas to clear the selection (the original behavior).
    node    click empty canvas to place a node right there.
    edge    click one node, then another, to connect them (a line
            follows the cursor in between).

    In every tool, right-clicking a node deletes it (with its edges)
    and right-clicking an edge deletes just that edge. Every edit can
    be undone and redone (Ctrl+Z / Ctrl+Y, or the Undo and Redo
    buttons); loading a file starts a fresh history.
    """

    # The Tools row (label, Undo/Redo, three tool buttons) is inserted
    # above the edit buttons. Everything from the edit buttons down is
    # shifted by this amount (cascade shift) and the panel grows to match.
    TOOLS_ROW_SHIFT = 52

    TOOLS = (("select", "Select"), ("node", "Node"), ("edge", "Edge"))

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

        self.tool = "select"
        self._edge_source: int | None = None

        # Undo/redo hold complete snapshots of (graph data, label counter).
        self._undo_stack: list[tuple[dict, int]] = []
        self._redo_stack: list[tuple[dict, int]] = []

        self.directed_buttons = self._create_toggle_buttons(
            160, "Undirected", "Directed"
        )
        self.weighted_buttons = self._create_toggle_buttons(
            204, "Unweighted", "Weighted"
        )

        self.randomize_button = Button(
            pygame.Rect(140, 117, 95, 24),
            "Randomize",
        )

        self.info_button = Button(
            pygame.Rect(surface.get_width() - 115, 15, 100, 38),
            "Info",
        )
        self.info_panel = InfoPanel(
            "Graph - Time Complexity",
            [
                ("BFS", "O(V + E)", "V = nodes, E = edges"),
                ("DFS", "O(V + E)", ""),
                ("Dijkstra", "O((V+E) log V)", "Binary-heap implementation"),
                ("Bellman-Ford", "O(V * E)", "Handles negative weights"),
            ],
        )

        # Save / Load buttons (left of Info) and their dialog.
        self.storage = StorageControls(
            surface,
            "graph",
            "Graph",
            capture=self._capture_structure,
            restore=self._restore_structure,
        )

        shift = self.TOOLS_ROW_SHIFT

        self.tool_buttons = {
            "select": Button(pygame.Rect(15, 278, 70, 34), "Select"),
            "node": Button(pygame.Rect(90, 278, 70, 34), "Node"),
            "edge": Button(pygame.Rect(165, 278, 70, 34), "Edge"),
        }
        self.undo_button = Button(pygame.Rect(110, 246, 60, 24), "Undo")
        self.redo_button = Button(pygame.Rect(175, 246, 60, 24), "Redo")

        self.edit_buttons = self._create_edit_buttons()
        self.algorithm_buttons = self._create_algorithm_buttons()
        self.navigation_buttons = self._create_navigation_buttons()

        for index, button in enumerate(self.speed_buttons):
            button.rect = pygame.Rect(15 + index * 62, 588 + shift, 58, 28)

        self.weight_input = NumericInput(pygame.Rect(160, 391 + shift, 75, 30), 1)

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
        shift = self.TOOLS_ROW_SHIFT

        return {
            "add_node": Button(
                pygame.Rect(15, 264 + shift, 110, 34), "Add Node", variant="primary"
            ),
            "remove_node": Button(
                pygame.Rect(130, 264 + shift, 105, 34), "Remove Node", variant="danger"
            ),
            "add_edge": Button(
                pygame.Rect(15, 302 + shift, 110, 34), "Add Edge", variant="primary"
            ),
            "remove_edge": Button(
                pygame.Rect(130, 302 + shift, 105, 34), "Remove Edge", variant="danger"
            ),
            "clear": Button(
                pygame.Rect(15, 340 + shift, 220, 34), "Clear Graph", variant="danger"
            ),
        }

    def _create_algorithm_buttons(self) -> dict[str, Button]:
        shift = self.TOOLS_ROW_SHIFT

        return {
            "BFS": Button(pygame.Rect(15, 464 + shift, 110, 34), "BFS"),
            "DFS": Button(pygame.Rect(130, 464 + shift, 105, 34), "DFS"),
            "Dijkstra": Button(pygame.Rect(15, 502 + shift, 110, 34), "Dijkstra"),
            "Bellman-Ford": Button(pygame.Rect(130, 502 + shift, 105, 34), "Bellman-Ford"),
        }

    def _create_navigation_buttons(self) -> list[Button]:
        labels = ["|<", "<", ">", ">|", "P"]

        buttons = []

        x = 15
        y = 626 + self.TOOLS_ROW_SHIFT
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

    @staticmethod
    def _label_for(index: int) -> str:
        """The label for the index-th node ever created: A, B, ... Z, A1, B1, ..."""

        letter = chr(ord("A") + index % 26)
        suffix = index // 26

        return f"{letter}{suffix}" if suffix else letter

    def _next_label(self) -> str:
        index = self._label_counter
        self._label_counter += 1

        return self._label_for(index)

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
        if self.info_panel.handle_event(event):
            return

        if self.storage.handle_event(event):
            return

        if self.handle_back_event(event):
            return

        if self.handle_speed_event(event):
            return

        self.weight_input.handle_event(event)

        if event.type == pygame.KEYDOWN and self._handle_history_shortcut(event):
            return

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

        self._handle_canvas_event(event)

        for tool, button in self.tool_buttons.items():
            if button.handle_event(event):
                self._set_tool(tool)

        if self.undo_button.handle_event(event):
            self._undo()

        if self.redo_button.handle_event(event):
            self._redo()

        for index, button in enumerate(self.directed_buttons):
            if button.handle_event(event):
                self._set_directed(index == 1)

        for index, button in enumerate(self.weighted_buttons):
            if button.handle_event(event):
                self._set_weighted(index == 1)

        if self.randomize_button.handle_event(event):
            self._randomize()

        if self.info_button.handle_event(event):
            self.info_panel.open()

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
            elif self._canvas_rect().collidepoint(event.pos):
                self._click_empty_canvas(event.pos)

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            if self._canvas_rect().collidepoint(event.pos):
                self._right_click(event.pos)

        elif event.type == pygame.MOUSEMOTION and self._mouse_down_node is not None:
            if not self._is_dragging:
                dx = event.pos[0] - self._mouse_down_pos[0]
                dy = event.pos[1] - self._mouse_down_pos[1]

                if dx * dx + dy * dy > 25:
                    self._is_dragging = True

                    # One undo step per drag, taken before the first move.
                    self._commit(self._snapshot())

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
                if not self._is_dragging:
                    self._click_node(self._mouse_down_node)

                self._mouse_down_node = None
                self._is_dragging = False

    def _click_empty_canvas(self, position: tuple[int, int]) -> None:
        if self.tool == "node":
            self._add_node_at(position)
        elif self.tool == "edge":
            self._edge_source = None
        elif self.current_simulation is None:
            self.selected_nodes = []

    def _click_node(self, node_id: int) -> None:
        if self.tool == "edge":
            self._edge_click(node_id)
        elif self.tool == "select" and self.current_simulation is None:
            self._toggle_selection(node_id)

    def _toggle_selection(self, node_id: int) -> None:
        if node_id in self.selected_nodes:
            self.selected_nodes.remove(node_id)
            return

        if len(self.selected_nodes) >= 2:
            self.selected_nodes = []

        self.selected_nodes.append(node_id)

    def _edge_click(self, node_id: int) -> None:
        """Edge tool: first click picks the source, second picks the target."""

        if self._busy():
            return

        if self._edge_source is None:
            self._edge_source = node_id
            self.error_message = None
            return

        source = self._edge_source

        # Clicking the pending node again cancels instead of looping.
        if node_id == source:
            self._edge_source = None
            return

        self._create_edge(source, node_id)
        self._edge_source = None

    def _right_click(self, position: tuple[int, int]) -> None:
        """Right-click: delete the node or edge under the cursor, or
        cancel a pending edge / clear the selection on empty canvas."""

        node_id = self._node_at(position)
        edge = None if node_id is not None else self._edge_at(position)

        if node_id is None and edge is None:
            self._edge_source = None

            if self.current_simulation is None:
                self.selected_nodes = []

            return

        if self._busy():
            return

        if node_id is not None:
            self._remove_node(node_id)
        else:
            self._delete_edge(edge)

    # ------------------------------------------------------------------
    # Hit testing
    # ------------------------------------------------------------------

    @staticmethod
    def _distance_to_segment(
        point: tuple[float, float],
        start: tuple[float, float],
        end: tuple[float, float],
    ) -> float:
        """Shortest distance from a point to the segment start-end."""

        dx = end[0] - start[0]
        dy = end[1] - start[1]
        length_squared = dx * dx + dy * dy

        if length_squared == 0:
            return math.hypot(point[0] - start[0], point[1] - start[1])

        t = ((point[0] - start[0]) * dx + (point[1] - start[1]) * dy) / length_squared
        t = max(0.0, min(1.0, t))

        return math.hypot(
            point[0] - (start[0] + t * dx),
            point[1] - (start[1] + t * dy),
        )

    def _edge_at(self, position: tuple[int, int]) -> GraphEdge | None:
        """The edge whose line passes closest to `position`, if any is
        within EDGE_HIT_DISTANCE. Nodes are tested first by callers."""

        best: GraphEdge | None = None
        best_distance = EDGE_HIT_DISTANCE

        for edge in self.model.edges:
            source = self.model.get_node(edge.source)
            target = self.model.get_node(edge.target)

            if source is None or target is None:
                continue

            distance = self._distance_to_segment(
                position, (source.x, source.y), (target.x, target.y)
            )

            if distance <= best_distance:
                best = edge
                best_distance = distance

        return best

    def _find_edge(self, first: int, second: int) -> GraphEdge | None:
        """The stored edge joining two nodes (either way when undirected)."""

        for edge in self.model.edges:
            if (edge.source, edge.target) == (first, second):
                return edge

            if not self.model.directed and (edge.source, edge.target) == (second, first):
                return edge

        return None

    # ------------------------------------------------------------------
    # Undo / redo
    # ------------------------------------------------------------------

    def _snapshot(self) -> tuple[dict, int]:
        """Everything an edit can change: the graph and the label counter."""

        return self.model.to_dict(), self._label_counter

    def _commit(self, before: tuple[dict, int]) -> None:
        """Record `before` as an undo step. Call after a successful edit."""

        self._undo_stack.append(before)
        del self._undo_stack[:-MAX_UNDO_STEPS]
        self._redo_stack.clear()

    def _apply_snapshot(self, snapshot: tuple[dict, int]) -> bool:
        data, counter = snapshot

        try:
            loaded = GraphModel.from_dict(data)
        except ValueError as error:
            self.error_message = f"Could not restore that state: {error}"
            return False

        self.model.replace_with(loaded)
        self._label_counter = counter

        self.selected_nodes = []
        self._edge_source = None
        self._mouse_down_node = None
        self._is_dragging = False
        self.error_message = None

        return True

    def _undo(self) -> None:
        if self.current_simulation is not None or not self._undo_stack:
            return

        current = self._snapshot()

        if self._apply_snapshot(self._undo_stack.pop()):
            self._redo_stack.append(current)

    def _redo(self) -> None:
        if self.current_simulation is not None or not self._redo_stack:
            return

        current = self._snapshot()

        if self._apply_snapshot(self._redo_stack.pop()):
            self._undo_stack.append(current)

    def _handle_history_shortcut(self, event: pygame.event.Event) -> bool:
        """Ctrl+Z undo, Ctrl+Shift+Z / Ctrl+Y redo (Cmd on a Mac)."""

        modifiers = getattr(event, "mod", 0)

        if not modifiers & (pygame.KMOD_CTRL | pygame.KMOD_META):
            return False

        if event.key == pygame.K_z:
            if modifiers & pygame.KMOD_SHIFT:
                self._redo()
            else:
                self._undo()

            return True

        if event.key == pygame.K_y:
            self._redo()
            return True

        return False

    # ------------------------------------------------------------------
    # Editing actions
    # ------------------------------------------------------------------

    def _set_tool(self, tool: str) -> None:
        self.tool = tool
        self._edge_source = None
        self.error_message = None

    def _busy(self) -> bool:
        """True (with a message) while an algorithm is running, since
        editing the graph under it would make the animation meaningless."""

        if self.current_simulation is None:
            return False

        self.error_message = "Let the algorithm finish before editing."

        return True

    def _node_limit_reached(self) -> bool:
        if len(self.model.nodes) < GraphModel.MAX_LOADED_NODES:
            return False

        self.error_message = (
            f"A graph here can have at most {GraphModel.MAX_LOADED_NODES} nodes."
        )

        return True

    def _set_directed(self, directed: bool) -> None:
        if directed == self.model.directed or self._busy():
            return

        before = self._snapshot()

        self.model.set_directed(directed)

        self._commit(before)
        self.error_message = None

    def _set_weighted(self, weighted: bool) -> None:
        if weighted == self.model.weighted or self._busy():
            return

        before = self._snapshot()

        self.model.set_weighted(weighted)

        self._commit(before)
        self.error_message = None

    def _add_node(self) -> None:
        if self._busy() or self._node_limit_reached():
            return

        before = self._snapshot()

        self.model.add_node(label=self._next_label())
        self._relayout()

        self._commit(before)
        self.error_message = None

    def _add_node_at(self, position: tuple[int, int]) -> None:
        """Node tool: place a node where the canvas was clicked."""

        if self._busy() or self._node_limit_reached():
            return

        canvas = self._canvas_rect()

        x = max(canvas.left + NODE_RADIUS, min(canvas.right - NODE_RADIUS, position[0]))
        y = max(canvas.top + NODE_RADIUS, min(canvas.bottom - NODE_RADIUS, position[1]))

        if self._too_close_to_a_node(x, y):
            self.error_message = "Too close to another node."
            return

        before = self._snapshot()

        self.model.add_node_at(x, y, label=self._next_label())

        self._commit(before)
        self.error_message = None

    def _too_close_to_a_node(self, x: float, y: float) -> bool:
        return any(
            math.hypot(node.x - x, node.y - y) < MIN_NODE_DISTANCE
            for node in self.model.nodes
        )

    def _remove_selected_node(self) -> None:
        if self._busy():
            return

        if len(self.selected_nodes) != 1:
            self.error_message = "Select exactly one node to remove it."
            return

        self._remove_node(self.selected_nodes[0])

    def _remove_node(self, node_id: int) -> None:
        before = self._snapshot()

        self.model.remove_node(node_id)
        self._relayout()

        self.selected_nodes = [n for n in self.selected_nodes if n != node_id]

        if self._edge_source == node_id:
            self._edge_source = None

        self._commit(before)
        self.error_message = None

    def _add_edge(self) -> None:
        if self._busy():
            return

        if len(self.selected_nodes) != 2:
            self.error_message = "Select exactly two nodes to add an edge."
            return

        source, target = self.selected_nodes

        if self._create_edge(source, target):
            self.selected_nodes = []

    def _create_edge(self, source: int, target: int) -> bool:
        """Add an edge (or, when weighted, update an existing edge's
        weight). Returns True if the graph changed."""

        weight = self.weight_input.value if self.model.weighted else 1.0
        existing = self._find_edge(source, target)

        if existing is not None:
            if not self.model.weighted:
                self.error_message = "Those nodes are already connected."
                return False

            if existing.weight == weight:
                self.error_message = f"Already connected with weight {weight:g}."
                return False
        elif len(self.model.edges) >= GraphModel.MAX_LOADED_EDGES:
            self.error_message = (
                f"A graph here can have at most {GraphModel.MAX_LOADED_EDGES} edges."
            )
            return False

        before = self._snapshot()

        try:
            self.model.add_edge(source, target, weight)
        except (KeyError, ValueError) as error:
            self.error_message = str(error)
            return False

        self._commit(before)
        self.error_message = None

        return True

    def _remove_edge(self) -> None:
        if self._busy():
            return

        if len(self.selected_nodes) != 2:
            self.error_message = "Select exactly two nodes to remove an edge."
            return

        source, target = self.selected_nodes
        edge = self._find_edge(source, target)

        if edge is None:
            labels = [self.model.get_node(n).label for n in (source, target)]
            self.error_message = f"No edge between {labels[0]} and {labels[1]}."
            return

        self._delete_edge(edge)
        self.selected_nodes = []

    def _delete_edge(self, edge: GraphEdge) -> None:
        before = self._snapshot()

        self.model.remove_edge(edge.source, edge.target)

        self._commit(before)
        self.error_message = None

    def _clear_graph(self) -> None:
        if self._busy():
            return

        before = self._snapshot()
        changed = not self.model.is_empty or self._label_counter != 0

        self.model.clear()
        self.selected_nodes = []
        self._edge_source = None
        self._label_counter = 0
        self.status_message = None
        self.error_message = None

        if changed:
            self._commit(before)

    def _randomize(self) -> None:
        """
        Replace the graph with random nodes and edges, instantly and
        without animation (same behavior as the sorting screen's
        Randomize). Overrides any in-progress algorithm run rather
        than refusing, consistent with the other editing actions on
        this screen once a simulation is in flight.

        Edges are picked with has_edge() guarding against duplicates,
        and always between two distinct freshly created nodes, so
        add_edge() never sees a self-loop or a missing node.
        """

        before = self._snapshot()

        self.cancel_current_simulation()

        self.model.clear()
        self.selected_nodes = []
        self._edge_source = None
        self._label_counter = 0
        self.status_message = None
        self.error_message = None

        node_count = random.randint(5, 7)

        node_ids = [
            self.model.add_node(label=self._next_label())
            for _ in range(node_count)
        ]

        # A few more edges than nodes gives a reasonably connected
        # graph without guaranteeing full connectivity, which is fine
        # for a random practice graph.
        target_edge_count = random.randint(node_count, node_count + 2)
        max_attempts = target_edge_count * 10
        attempts = 0

        while (
            len(self.model.edges) < target_edge_count
            and attempts < max_attempts
        ):
            attempts += 1

            source, target = random.sample(node_ids, 2)

            if self.model.has_edge(source, target):
                continue

            weight = random.randint(1, 9) if self.model.weighted else 1.0

            try:
                self.model.add_edge(source, target, weight)
            except (KeyError, ValueError):
                continue

        self._relayout()

        self._commit(before)

    # ------------------------------------------------------------------
    # Save / Load
    # ------------------------------------------------------------------

    def _capture_structure(self) -> tuple[str | None, dict]:
        """Current graph as (mode, data) for the Save dialog.

        The mode ("undirected", "directed-weighted", ...) describes the
        graph in suggested file names and in the Load list; the data
        itself says which it is.
        """

        mode = "directed" if self.model.directed else "undirected"

        if self.model.weighted:
            mode += "-weighted"

        return mode, self.model.to_dict()

    def _restore_structure(self, mode: str | None, data: dict) -> None:
        """Replace the graph with loaded data (from the Load dialog).

        GraphModel.from_dict() validates everything first (including
        that every edge refers to a real node) and raises ValueError on
        bad data, so nothing below runs for a bad file. Directed and
        weighted come from the file.

        Node positions are kept exactly as saved (clamped to the canvas
        in case a file was edited by hand). Auto-layout is deliberately
        NOT re-run: when some nodes were dragged, the others keep their
        old circle positions, and recomputing them would make the
        loaded graph look different from the saved one.
        """

        loaded = GraphModel.from_dict(data)

        self.cancel_current_simulation()

        self.model.replace_with(loaded)

        canvas = self._canvas_rect()

        for node in self.model.nodes:
            node.x = max(
                canvas.left + NODE_RADIUS,
                min(canvas.right - NODE_RADIUS, node.x),
            )
            node.y = max(
                canvas.top + NODE_RADIUS,
                min(canvas.bottom - NODE_RADIUS, node.y),
            )

        # Continue labelling after the loaded nodes without ever
        # repeating a label that is already on the canvas.
        used = {node.label for node in self.model.nodes}
        counter = len(used)

        while self._label_for(counter) in used:
            counter += 1

        self._label_counter = counter

        self.selected_nodes = []
        self._edge_source = None
        self._mouse_down_node = None
        self._mouse_down_pos = None
        self._is_dragging = False

        # A loaded file is a fresh start: nothing before it can be undone.
        self._undo_stack.clear()
        self._redo_stack.clear()

        self.status_message = None
        self.error_message = None
        self.step_timer = 0.0

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

        self._edge_source = None

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
        self.update_speed_buttons(dt)

        for button in self.directed_buttons:
            button.update(dt)

        for button in self.weighted_buttons:
            button.update(dt)

        self.randomize_button.update(dt)

        self.info_button.update(dt)

        self.storage.update(dt)

        for button in self.tool_buttons.values():
            button.update(dt)

        self.undo_button.update(dt)
        self.redo_button.update(dt)

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
        self._render_graph()

        self.info_button.render(self.surface)
        self.storage.render(self.surface)
        self.info_panel.render(self.surface)

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

        idle = self.current_simulation is None

        self.undo_button.enabled = idle and bool(self._undo_stack)
        self.redo_button.enabled = idle and bool(self._redo_stack)

    def _render_control_panel(self) -> None:
        shift = self.TOOLS_ROW_SHIFT

        panel_rect = pygame.Rect(10, 70, 250, 630 + shift)
        draw_panel(self.surface, panel_rect, elevated=True)

        self._draw_text("TA Controls", (25, 80), self.control_font)

        self._draw_text(
            "Graph Settings",
            (25, 120),
            self.section_font,
            color=Color.TEXT_SECONDARY,
        )

        self.randomize_button.render(self.surface)

        self._render_toggle_row(self.directed_buttons, self.model.directed)
        self._render_toggle_row(self.weighted_buttons, self.model.weighted)

        self._draw_text(
            "Tools",
            (25, 249),
            self.section_font,
            color=Color.TEXT_SECONDARY,
        )

        self.undo_button.render(self.surface)
        self.redo_button.render(self.surface)

        for tool, button in self.tool_buttons.items():
            draw_toggle_button(self.surface, button, tool == self.tool)

        for button in self.edit_buttons.values():
            button.render(self.surface)

        self._draw_text(
            "Edge Weight:",
            (15, 396 + shift),
            self.small_font,
            color=Color.TEXT_SECONDARY,
        )

        if self.model.weighted:
            self.weight_input.render(self.surface)
        else:
            self._draw_text(
                "1 (unweighted)",
                (160, 396 + shift),
                self.small_font,
                color=Color.TEXT_MUTED,
            )

        self._render_selection_status()

        for button in self.algorithm_buttons.values():
            button.render(self.surface)

        self._draw_text(
            "Simulation",
            (25, 562 + shift),
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
                    (15, 669 + shift),
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

    TOOL_HINTS = {
        "select": "Click nodes to select them. Drag to move.",
        "node": "Click empty space to add a node.",
        "edge": "Click one node, then another, to connect them.",
    }

    def _render_selection_status(self) -> None:
        if self.error_message is not None:
            text = self.error_message
            color = Color.STATE_DANGER
        elif self.tool == "edge" and self._edge_source is not None:
            source = self.model.get_node(self._edge_source)
            text = f"Edge from {source.label}: click the target node."
            color = Color.ACCENT
        elif self.tool == "select" and self.selected_nodes:
            labels = [
                self.model.get_node(node_id).label
                for node_id in self.selected_nodes
                if self.model.get_node(node_id) is not None
            ]
            text = "Selected: " + ", ".join(labels)
            color = Color.TEXT_SECONDARY
        else:
            text = self.TOOL_HINTS[self.tool]
            color = Color.TEXT_MUTED

        area = pygame.Rect(15, 428 + self.TOOLS_ROW_SHIFT, 220, 32)
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
                "Build a graph with the Node and Edge tools (or the buttons), "
                "then select one node and choose an algorithm to run it from "
                "there. Right-click a node or an edge to delete it."
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
                "Graph is empty. Add a node, or pick the Node tool and click here.",
                True,
                Color.TEXT_MUTED,
            )
            self.surface.blit(text, text.get_rect(center=area.center))
            self._render_node_ghost()
            return

        state = self._get_algorithm_state()

        self._render_edges(state)
        self._render_pending_edge()
        self._render_nodes(state)
        self._render_node_ghost()

    def _render_pending_edge(self) -> None:
        """Edge tool: a line from the chosen node to the cursor."""

        if self.tool != "edge" or self._edge_source is None:
            return

        source = self.model.get_node(self._edge_source)
        mouse = pygame.mouse.get_pos()

        if source is None or not self._canvas_rect().collidepoint(mouse):
            return

        hovered = self._node_at(mouse)
        source_pos = (source.x, source.y)

        if hovered is not None and hovered != self._edge_source:
            target = self.model.get_node(hovered)
            start, end = self._shrink_to_radius(source_pos, (target.x, target.y))
        else:
            start, _ = self._shrink_to_radius(source_pos, mouse)
            end = mouse

        if self.model.directed:
            draw_arrow(self.surface, start, end, Color.ACCENT, width=2)
        else:
            pygame.draw.line(self.surface, Color.ACCENT, start, end, 2)

    def _render_node_ghost(self) -> None:
        """Node tool: a ring where a click would place a node, red when
        that spot is not allowed (too close to a node, or at the limit)."""

        if self.tool != "node" or self.current_simulation is not None:
            return

        mouse = pygame.mouse.get_pos()
        canvas = self._canvas_rect()

        if not canvas.collidepoint(mouse):
            return

        x = max(canvas.left + NODE_RADIUS, min(canvas.right - NODE_RADIUS, mouse[0]))
        y = max(canvas.top + NODE_RADIUS, min(canvas.bottom - NODE_RADIUS, mouse[1]))

        allowed = (
            len(self.model.nodes) < GraphModel.MAX_LOADED_NODES
            and not self._too_close_to_a_node(x, y)
        )

        color = Color.STATE_SUCCESS if allowed else Color.STATE_DANGER

        pygame.draw.circle(self.surface, color, (int(x), int(y)), NODE_RADIUS, 2)

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

        if node_id in self.selected_nodes or node_id == self._edge_source:
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