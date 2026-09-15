from __future__ import annotations

import math
from dataclasses import dataclass, field


@dataclass
class GraphNode:
    """A node placed on the graph canvas."""

    node_id: int
    label: str
    x: float
    y: float

    # True once the student drags this node. Pinned nodes are left
    # alone by auto-layout so a manually arranged graph doesn't keep
    # snapping back to the circle every time something else changes.
    pinned: bool = False


@dataclass(frozen=True)
class GraphEdge:
    """An edge between two nodes, by id."""

    source: int
    target: int
    weight: float = 1.0


class GraphModel:
    """
    Represents an editable graph.

    Directed and weighted are graph-level toggles rather than
    per-edge properties, since a student building a single lesson
    graph expects the whole graph to behave consistently, not a mix
    of directed and undirected edges in the same drawing.
    """

    def __init__(
        self,
        directed: bool = False,
        weighted: bool = False,
    ) -> None:
        self._nodes: dict[int, GraphNode] = {}
        self._edges: dict[tuple[int, int], GraphEdge] = {}

        self._directed = directed
        self._weighted = weighted

        self._next_node_id = 0

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def directed(self) -> bool:
        return self._directed

    @property
    def weighted(self) -> bool:
        return self._weighted

    @property
    def nodes(self) -> list[GraphNode]:
        return list(self._nodes.values())

    @property
    def edges(self) -> list[GraphEdge]:
        return list(self._edges.values())

    @property
    def is_empty(self) -> bool:
        return not self._nodes

    def get_node(self, node_id: int) -> GraphNode | None:
        return self._nodes.get(node_id)

    def has_edge(self, source: int, target: int) -> bool:
        if (source, target) in self._edges:
            return True

        if not self._directed and (target, source) in self._edges:
            return True

        return False

    # ------------------------------------------------------------------
    # Editing
    # ------------------------------------------------------------------

    def set_directed(self, directed: bool) -> None:
        """
        Change whether the graph is directed.

        Switching to undirected silently drops the "reverse"
        duplicate if both (a, b) and (b, a) already exist, since an
        undirected graph can't represent two distinct edges between
        the same pair of nodes.
        """

        if directed == self._directed:
            return

        self._directed = directed

        if not directed:
            seen: set[frozenset[int]] = set()
            deduplicated: dict[tuple[int, int], GraphEdge] = {}

            for key, edge in self._edges.items():
                pair = frozenset((edge.source, edge.target))

                if pair in seen:
                    continue

                seen.add(pair)
                deduplicated[key] = edge

            self._edges = deduplicated

    def set_weighted(self, weighted: bool) -> None:
        """
        Change whether edge weights are used.

        Turning weights off doesn't delete the stored weight values,
        it just means algorithms and rendering treat every edge as
        weight 1 until weighted is turned back on, so a student
        toggling back and forth doesn't lose their numbers.
        """

        self._weighted = weighted

    def add_node(self, label: str | None = None) -> int:
        """Add a node and return its id."""

        node_id = self._next_node_id
        self._next_node_id += 1

        node = GraphNode(
            node_id=node_id,
            label=label if label is not None else str(node_id),
            x=0.0,
            y=0.0,
        )

        self._nodes[node_id] = node

        self.recompute_layout()

        return node_id

    def remove_node(self, node_id: int) -> None:
        """Remove a node and every edge touching it."""

        if node_id not in self._nodes:
            raise KeyError(f"No node with id {node_id}.")

        del self._nodes[node_id]

        self._edges = {
            key: edge
            for key, edge in self._edges.items()
            if edge.source != node_id and edge.target != node_id
        }

        self.recompute_layout()

    def add_edge(
        self,
        source: int,
        target: int,
        weight: float = 1.0,
    ) -> None:
        """Add an edge between two existing nodes."""

        if source not in self._nodes or target not in self._nodes:
            raise KeyError("Both nodes must exist before adding an edge.")

        if source == target:
            raise ValueError("Self-loops are not supported.")

        self._edges[(source, target)] = GraphEdge(source, target, weight)

    def remove_edge(self, source: int, target: int) -> None:
        """Remove an edge, checking both directions when undirected."""

        if (source, target) in self._edges:
            del self._edges[(source, target)]
            return

        if not self._directed and (target, source) in self._edges:
            del self._edges[(target, source)]
            return

        raise KeyError(f"No edge between {source} and {target}.")

    def move_node(self, node_id: int, x: float, y: float) -> None:
        """Move a node to an explicit position and pin it there."""

        node = self._nodes.get(node_id)

        if node is None:
            raise KeyError(f"No node with id {node_id}.")

        node.x = x
        node.y = y
        node.pinned = True

    def unpin_all(self) -> None:
        """Release every manually placed node back to auto-layout."""

        for node in self._nodes.values():
            node.pinned = False

        self.recompute_layout()

    def clear(self) -> None:
        self._nodes.clear()
        self._edges.clear()
        self._next_node_id = 0

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------

    def recompute_layout(
        self,
        center_x: float = 0.0,
        center_y: float = 0.0,
        radius: float = 220.0,
    ) -> None:
        """
        Arrange every unpinned node evenly around a circle.

        This is intentionally simple rather than a force-directed
        layout: it's predictable, has no settling time, and a
        student can always drag a node exactly where they want it
        and have it stay put (see `pinned`).
        """

        unpinned = [
            node for node in self._nodes.values() if not node.pinned
        ]

        if not unpinned:
            return

        count = len(unpinned)

        for index, node in enumerate(unpinned):
            angle = (2 * math.pi * index) / count - (math.pi / 2)

            node.x = center_x + radius * math.cos(angle)
            node.y = center_y + radius * math.sin(angle)

    # ------------------------------------------------------------------
    # Algorithm support
    # ------------------------------------------------------------------

    def adjacency(self) -> dict[int, list[tuple[int, float]]]:
        """
        Return each node's neighbors as (neighbor_id, weight) pairs.

        Weight is reported as 1.0 for every edge when the graph is
        unweighted, regardless of what's stored, so algorithms never
        need to check `weighted` themselves.
        """

        result: dict[int, list[tuple[int, float]]] = {
            node_id: [] for node_id in self._nodes
        }

        for edge in self._edges.values():
            weight = edge.weight if self._weighted else 1.0

            result[edge.source].append((edge.target, weight))

            if not self._directed:
                result[edge.target].append((edge.source, weight))

        return result