from __future__ import annotations

from collections import deque
from dataclasses import dataclass

from algolab.simulation.events import SimulationEvent
from algolab.simulation.state import SimulationState
from algolab.topics.graph.model import GraphModel


@dataclass(frozen=True)
class VisitGraphNodeEvent(SimulationEvent):
    """Indicates that a node is being visited (dequeued and marked)."""

    node_id: int


@dataclass(frozen=True)
class DiscoverGraphNodeEvent(SimulationEvent):
    """Indicates that a node was discovered through an edge and queued."""

    node_id: int
    from_node_id: int


@dataclass(frozen=True)
class ExamineGraphEdgeEvent(SimulationEvent):
    """Indicates that an edge is being looked at, whether or not it leads
    anywhere new."""

    source: int
    target: int


@dataclass(frozen=True)
class CompleteGraphAlgorithmEvent(SimulationEvent):
    """Indicates that the algorithm run has finished."""

    algorithm: str


@dataclass(frozen=True)
class GraphAlgorithmState:
    """
    Represents the visual state of a graph algorithm simulation.

    This shape is intentionally shared across BFS, DFS, Dijkstra, and
    Bellman-Ford rather than each algorithm inventing its own state,
    since the screen only needs to know "what's visited, what's in
    the frontier, what's currently active, what are the distances" no
    matter which algorithm produced it. Fields that don't apply to a
    given algorithm (e.g. distances for BFS/DFS) are simply left at
    their default.
    """

    description: str

    visited: frozenset[int] = frozenset()
    frontier: tuple[int, ...] = ()
    current_node: int | None = None

    # (source, target) of the edge currently being examined, if any.
    active_edge: tuple[int, int] | None = None

    # Running distance/cost table, used by Dijkstra and Bellman-Ford.
    # BFS and DFS leave this empty.
    distances: dict[int, float] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.distances is None:
            object.__setattr__(self, "distances", {})


@dataclass(frozen=True)
class GraphAlgorithmSimulation:
    """Represents a complete graph algorithm run."""

    states: tuple[SimulationState, ...]
    algorithm: str

    def commit(self, model: GraphModel) -> None:
        """
        Graph algorithms are read-only.

        Unlike insert/delete on a stack or a tree, running BFS never
        changes the graph itself, so there's nothing to commit. This
        method exists only so the graph screen can call
        `simulation.commit(model)` the same way every other topic
        screen does, without needing a special case.
        """

        return None


class BFSSimulator:
    """Creates a step-by-step simulation of breadth-first search."""

    def __init__(self, model: GraphModel) -> None:
        self.model = model

    def run(self, start_node_id: int) -> GraphAlgorithmSimulation:
        if self.model.get_node(start_node_id) is None:
            raise KeyError(f"No node with id {start_node_id}.")

        adjacency = self.model.adjacency()

        states: list[SimulationState] = []

        visited: set[int] = set()
        queue: deque[int] = deque([start_node_id])
        visited.add(start_node_id)

        def add_state(
            events: list[SimulationEvent],
            description: str,
            current_node: int | None,
            active_edge: tuple[int, int] | None = None,
        ) -> None:
            data = GraphAlgorithmState(
                description=description,
                visited=frozenset(visited),
                frontier=tuple(queue),
                current_node=current_node,
                active_edge=active_edge,
            )

            states.append(
                SimulationState(
                    data=data,
                    events=events,
                    step=len(states),
                )
            )

        add_state(
            events=[VisitGraphNodeEvent(node_id=start_node_id)],
            description=(
                f"Start BFS at node {self._label(start_node_id)}. "
                "Add it to the queue and mark it visited."
            ),
            current_node=start_node_id,
        )

        while queue:
            current = queue[0]

            neighbors = sorted(
                adjacency.get(current, []),
                key=lambda pair: pair[0],
            )

            any_new_neighbor = False

            for neighbor_id, _weight in neighbors:
                add_state(
                    events=[
                        ExamineGraphEdgeEvent(
                            source=current,
                            target=neighbor_id,
                        )
                    ],
                    description=(
                        f"Examine the edge from "
                        f"{self._label(current)} to "
                        f"{self._label(neighbor_id)}."
                    ),
                    current_node=current,
                    active_edge=(current, neighbor_id),
                )

                if neighbor_id in visited:
                    continue

                any_new_neighbor = True

                visited.add(neighbor_id)
                queue.append(neighbor_id)

                add_state(
                    events=[
                        DiscoverGraphNodeEvent(
                            node_id=neighbor_id,
                            from_node_id=current,
                        )
                    ],
                    description=(
                        f"Discover node {self._label(neighbor_id)} "
                        f"through {self._label(current)}. Mark it "
                        "visited and add it to the queue."
                    ),
                    current_node=current,
                    active_edge=(current, neighbor_id),
                )

            queue.popleft()

            if queue:
                add_state(
                    events=[VisitGraphNodeEvent(node_id=queue[0])],
                    description=(
                        f"Move to the next node in the queue: "
                        f"{self._label(queue[0])}."
                    ),
                    current_node=queue[0],
                )

        add_state(
            events=[CompleteGraphAlgorithmEvent(algorithm="bfs")],
            description="BFS is complete. Every reachable node has been visited.",
            current_node=None,
        )

        return GraphAlgorithmSimulation(
            states=tuple(states),
            algorithm="bfs",
        )

    def _label(self, node_id: int) -> str:
        node = self.model.get_node(node_id)
        return node.label if node is not None else str(node_id)