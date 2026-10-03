from __future__ import annotations

import math
from dataclasses import dataclass, field

from algolab.core.serialization import (
    check_dict,
    check_int,
    check_number,
    checked_list,
)


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

    # Upper bounds accepted when loading a file.
    MAX_LOADED_NODES = 100
    MAX_LOADED_EDGES = 500
    MAX_LABEL_LENGTH = 12

    # Positions beyond this are not a canvas coordinate, just garbage.
    _MAX_COORDINATE = 100_000

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

    def add_node_at(
        self,
        x: float,
        y: float,
        label: str | None = None,
    ) -> int:
        """Add a node at an explicit position and return its id.

        The node is pinned where it is placed, and auto-layout is NOT
        re-run, so placing a node by hand never makes the other nodes
        move (unlike add_node, which re-spaces every unpinned node).
        """

        node_id = self._next_node_id
        self._next_node_id += 1

        self._nodes[node_id] = GraphNode(
            node_id=node_id,
            label=label if label is not None else str(node_id),
            x=float(x),
            y=float(y),
            pinned=True,
        )

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

        # For an undirected graph, (source, target) and (target, source)
        # represent the same connection. If the reverse direction was
        # added first, update that entry in place rather than storing a
        # second edge for the same pair, which would otherwise show up
        # twice in `edges` and double-count the pair in `adjacency()`.
        if not self._directed and (target, source) in self._edges:
            self._edges[(target, source)] = GraphEdge(target, source, weight)
            return

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

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        """Return a JSON-serializable snapshot of the whole graph.

        Node positions and pinned flags are saved so a loaded graph
        looks exactly as it did, and `next_node_id` is saved so ids are
        never reused after a node was deleted. Stored weights are kept
        even while the graph is unweighted (see set_weighted).
        """

        return {
            "directed": self._directed,
            "weighted": self._weighted,
            "next_node_id": self._next_node_id,
            "nodes": [
                {
                    "id": node.node_id,
                    "label": node.label,
                    "x": node.x,
                    "y": node.y,
                    "pinned": node.pinned,
                }
                for node in self._nodes.values()
            ],
            "edges": [
                {
                    "source": edge.source,
                    "target": edge.target,
                    "weight": edge.weight,
                }
                for edge in self._edges.values()
            ],
        }

    @classmethod
    def from_dict(cls, data: object) -> GraphModel:
        """Build a graph from a dict produced by to_dict().

        Raises:
            ValueError: If the data is malformed, an edge refers to a
                node that does not exist, a node id or edge appears
                twice, or a self-loop is present.
        """

        check_dict(data, "Graph")

        directed = data.get("directed")
        weighted = data.get("weighted")

        if not isinstance(directed, bool) or not isinstance(weighted, bool):
            raise ValueError("'directed' and 'weighted' must be true or false.")

        raw_nodes = checked_list(
            data, "Graph", cls.MAX_LOADED_NODES, key="nodes"
        )
        raw_edges = checked_list(
            data, "Graph", cls.MAX_LOADED_EDGES, key="edges"
        )

        graph = cls(directed=directed, weighted=weighted)

        for position, raw in enumerate(raw_nodes):
            if not isinstance(raw, dict):
                raise ValueError(f"Node {position} must be an object.")

            node_id = check_int(raw.get("id"), f"Node {position} id")

            if node_id < 0:
                raise ValueError(f"Node {position} id cannot be negative.")

            if node_id in graph._nodes:
                raise ValueError(f"Node id {node_id} appears twice.")

            label = raw.get("label")

            if (
                not isinstance(label, str)
                or not label
                or len(label) > cls.MAX_LABEL_LENGTH
                or not label.isprintable()
            ):
                raise ValueError(
                    f"Node {node_id} needs a label of 1 to "
                    f"{cls.MAX_LABEL_LENGTH} printable characters."
                )

            x = check_number(raw.get("x"), f"Node {node_id} x")
            y = check_number(raw.get("y"), f"Node {node_id} y")

            if abs(x) > cls._MAX_COORDINATE or abs(y) > cls._MAX_COORDINATE:
                raise ValueError(f"Node {node_id} has an unreasonable position.")

            pinned = raw.get("pinned")

            if not isinstance(pinned, bool):
                raise ValueError(f"Node {node_id} 'pinned' must be true or false.")

            graph._nodes[node_id] = GraphNode(
                node_id=node_id,
                label=label,
                x=float(x),
                y=float(y),
                pinned=pinned,
            )

        highest = max(graph._nodes, default=-1)
        next_node_id = check_int(data.get("next_node_id"), "'next_node_id'")

        if not highest < next_node_id <= 10**9:
            raise ValueError(
                "'next_node_id' must be larger than every node id."
            )

        graph._next_node_id = next_node_id

        seen: set = set()

        for position, raw in enumerate(raw_edges):
            if not isinstance(raw, dict):
                raise ValueError(f"Edge {position} must be an object.")

            source = check_int(raw.get("source"), f"Edge {position} source")
            target = check_int(raw.get("target"), f"Edge {position} target")

            if source not in graph._nodes or target not in graph._nodes:
                raise ValueError(
                    f"Edge {position} refers to a node that does not exist."
                )

            if source == target:
                raise ValueError(f"Edge {position} is a self-loop.")

            weight = check_number(raw.get("weight"), f"Edge {position} weight")

            identity = (
                (source, target)
                if directed
                else frozenset((source, target))
            )

            if identity in seen:
                raise ValueError(
                    f"Edge {position} duplicates an earlier edge between "
                    f"nodes {source} and {target}."
                )

            seen.add(identity)

            graph._edges[(source, target)] = GraphEdge(source, target, weight)

        return graph

    def replace_with(self, other: GraphModel) -> None:
        """Take over another graph's contents (it should not be reused)."""

        self._nodes = other._nodes
        self._edges = other._edges
        self._directed = other._directed
        self._weighted = other._weighted
        self._next_node_id = other._next_node_id