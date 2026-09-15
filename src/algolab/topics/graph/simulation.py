from __future__ import annotations

import heapq
import math
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
class RelaxEdgeEvent(SimulationEvent):
    """
    Indicates that an edge improved a node's known distance.

    Used by Dijkstra and Bellman-Ford. "Relaxing" an edge means: if
    going through this edge gives a shorter known path to the target
    than what we currently have recorded, update the record.
    """

    source: int
    target: int
    old_distance: float
    new_distance: float


@dataclass(frozen=True)
class NegativeCycleDetectedEvent(SimulationEvent):
    """
    Indicates Bellman-Ford found an edge that still relaxes after
    every node has had a chance to settle, meaning the graph contains
    a negative-weight cycle and shortest paths aren't well-defined.
    """

    source: int
    target: int


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


class DFSSimulator:
    """
    Creates a step-by-step simulation of depth-first search.

    Structurally this is BFS with a stack instead of a queue, which
    is exactly why the traversal order differs: BFS explores all of
    a node's neighbors before moving deeper, DFS immediately follows
    the first unvisited neighbor as far as it can before backtracking.
    """

    def __init__(self, model: GraphModel) -> None:
        self.model = model

    def run(self, start_node_id: int) -> GraphAlgorithmSimulation:
        if self.model.get_node(start_node_id) is None:
            raise KeyError(f"No node with id {start_node_id}.")

        adjacency = self.model.adjacency()

        states: list[SimulationState] = []

        visited: set[int] = set()
        stack: list[int] = [start_node_id]

        def add_state(
            events: list[SimulationEvent],
            description: str,
            current_node: int | None,
            active_edge: tuple[int, int] | None = None,
        ) -> None:
            data = GraphAlgorithmState(
                description=description,
                visited=frozenset(visited),
                frontier=tuple(stack),
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
            events=[],
            description=(
                f"Start DFS at node {self._label(start_node_id)}. "
                "Push it onto the stack."
            ),
            current_node=None,
        )

        while stack:
            current = stack[-1]

            if current not in visited:
                visited.add(current)

                add_state(
                    events=[VisitGraphNodeEvent(node_id=current)],
                    description=(
                        f"Visit node {self._label(current)} and mark "
                        "it visited."
                    ),
                    current_node=current,
                )

            neighbors = sorted(
                adjacency.get(current, []),
                key=lambda pair: pair[0],
            )

            next_unvisited = next(
                (
                    neighbor_id
                    for neighbor_id, _weight in neighbors
                    if neighbor_id not in visited
                ),
                None,
            )

            if next_unvisited is None:
                # No unvisited neighbor from here, so this node is
                # fully explored and DFS backtracks to the previous
                # node on the stack.
                for neighbor_id, _weight in neighbors:
                    add_state(
                        events=[
                            ExamineGraphEdgeEvent(
                                source=current,
                                target=neighbor_id,
                            )
                        ],
                        description=(
                            f"Edge from {self._label(current)} to "
                            f"{self._label(neighbor_id)} leads "
                            "somewhere already visited."
                        ),
                        current_node=current,
                        active_edge=(current, neighbor_id),
                    )

                stack.pop()

                if stack:
                    add_state(
                        events=[],
                        description=(
                            f"Node {self._label(current)} has no "
                            "unvisited neighbors left. Backtrack to "
                            f"{self._label(stack[-1])}."
                        ),
                        current_node=stack[-1],
                    )

                continue

            add_state(
                events=[
                    ExamineGraphEdgeEvent(
                        source=current,
                        target=next_unvisited,
                    )
                ],
                description=(
                    f"Follow the edge from {self._label(current)} to "
                    f"the unvisited node {self._label(next_unvisited)}."
                ),
                current_node=current,
                active_edge=(current, next_unvisited),
            )

            stack.append(next_unvisited)

            add_state(
                events=[
                    DiscoverGraphNodeEvent(
                        node_id=next_unvisited,
                        from_node_id=current,
                    )
                ],
                description=(
                    f"Push node {self._label(next_unvisited)} onto "
                    "the stack."
                ),
                current_node=current,
                active_edge=(current, next_unvisited),
            )

        add_state(
            events=[CompleteGraphAlgorithmEvent(algorithm="dfs")],
            description="DFS is complete. Every reachable node has been visited.",
            current_node=None,
        )

        return GraphAlgorithmSimulation(
            states=tuple(states),
            algorithm="dfs",
        )

    def _label(self, node_id: int) -> str:
        node = self.model.get_node(node_id)
        return node.label if node is not None else str(node_id)


class DijkstraSimulator:
    """Creates a step-by-step simulation of Dijkstra's shortest-path algorithm."""

    def __init__(self, model: GraphModel) -> None:
        self.model = model

    def run(self, start_node_id: int) -> GraphAlgorithmSimulation:
        if self.model.get_node(start_node_id) is None:
            raise KeyError(f"No node with id {start_node_id}.")

        adjacency = self.model.adjacency()

        for neighbors in adjacency.values():
            for _neighbor_id, weight in neighbors:
                if weight < 0:
                    raise ValueError(
                        "Dijkstra requires non-negative edge weights. "
                        "Use Bellman-Ford for graphs with negative weights."
                    )

        states: list[SimulationState] = []

        distances: dict[int, float] = {
            node.node_id: math.inf for node in self.model.nodes
        }
        distances[start_node_id] = 0.0

        visited: set[int] = set()
        heap: list[tuple[float, int]] = [(0.0, start_node_id)]

        def add_state(
            events: list[SimulationEvent],
            description: str,
            current_node: int | None,
            active_edge: tuple[int, int] | None = None,
        ) -> None:
            frontier = tuple(
                node_id for _distance, node_id in sorted(heap)
            )

            data = GraphAlgorithmState(
                description=description,
                visited=frozenset(visited),
                frontier=frontier,
                current_node=current_node,
                active_edge=active_edge,
                distances=dict(distances),
            )

            states.append(
                SimulationState(
                    data=data,
                    events=events,
                    step=len(states),
                )
            )

        add_state(
            events=[],
            description=(
                f"Start Dijkstra at node {self._label(start_node_id)}. "
                "Its distance is 0; every other node starts at infinity."
            ),
            current_node=None,
        )

        while heap:
            current_distance, current = heapq.heappop(heap)

            if current in visited:
                continue

            visited.add(current)

            add_state(
                events=[VisitGraphNodeEvent(node_id=current)],
                description=(
                    f"Finalize node {self._label(current)} with "
                    f"distance {current_distance:g}. No shorter path "
                    "to it can exist, since every remaining edge weight "
                    "is non-negative."
                ),
                current_node=current,
            )

            neighbors = sorted(
                adjacency.get(current, []),
                key=lambda pair: pair[0],
            )

            for neighbor_id, weight in neighbors:
                add_state(
                    events=[
                        ExamineGraphEdgeEvent(
                            source=current,
                            target=neighbor_id,
                        )
                    ],
                    description=(
                        f"Examine the edge from {self._label(current)} "
                        f"to {self._label(neighbor_id)} "
                        f"(weight {weight:g})."
                    ),
                    current_node=current,
                    active_edge=(current, neighbor_id),
                )

                if neighbor_id in visited:
                    continue

                candidate = current_distance + weight

                if candidate < distances[neighbor_id]:
                    old_distance = distances[neighbor_id]
                    distances[neighbor_id] = candidate

                    heapq.heappush(heap, (candidate, neighbor_id))

                    old_label = (
                        "infinity"
                        if math.isinf(old_distance)
                        else f"{old_distance:g}"
                    )

                    add_state(
                        events=[
                            RelaxEdgeEvent(
                                source=current,
                                target=neighbor_id,
                                old_distance=old_distance,
                                new_distance=candidate,
                            )
                        ],
                        description=(
                            f"Relax {self._label(neighbor_id)}: "
                            f"{old_label} -> {candidate:g} through "
                            f"{self._label(current)}."
                        ),
                        current_node=current,
                        active_edge=(current, neighbor_id),
                    )

        add_state(
            events=[CompleteGraphAlgorithmEvent(algorithm="dijkstra")],
            description=(
                "Dijkstra is complete. Every reachable node has its "
                "shortest distance from the start."
            ),
            current_node=None,
        )

        return GraphAlgorithmSimulation(
            states=tuple(states),
            algorithm="dijkstra",
        )

    def _label(self, node_id: int) -> str:
        node = self.model.get_node(node_id)
        return node.label if node is not None else str(node_id)


class BellmanFordSimulator:
    """
    Creates a step-by-step simulation of the Bellman-Ford algorithm.

    Unlike Dijkstra, this handles negative edge weights correctly and
    can detect a negative-weight cycle, at the cost of examining
    every edge up to (node count - 1) times instead of always picking
    the closest unvisited node next.
    """

    def __init__(self, model: GraphModel) -> None:
        self.model = model

    def run(self, start_node_id: int) -> GraphAlgorithmSimulation:
        if self.model.get_node(start_node_id) is None:
            raise KeyError(f"No node with id {start_node_id}.")

        adjacency = self.model.adjacency()

        edge_list = [
            (source, target, weight)
            for source, neighbors in adjacency.items()
            for target, weight in neighbors
        ]

        node_count = len(self.model.nodes)

        states: list[SimulationState] = []

        distances: dict[int, float] = {
            node.node_id: math.inf for node in self.model.nodes
        }
        distances[start_node_id] = 0.0

        def add_state(
            events: list[SimulationEvent],
            description: str,
            active_edge: tuple[int, int] | None = None,
        ) -> None:
            data = GraphAlgorithmState(
                description=description,
                visited=frozenset(
                    node_id
                    for node_id, distance in distances.items()
                    if not math.isinf(distance)
                ),
                frontier=(),
                current_node=None,
                active_edge=active_edge,
                distances=dict(distances),
            )

            states.append(
                SimulationState(
                    data=data,
                    events=events,
                    step=len(states),
                )
            )

        add_state(
            events=[],
            description=(
                f"Start Bellman-Ford at node {self._label(start_node_id)}. "
                "Its distance is 0; every other node starts at infinity."
            ),
        )

        for iteration in range(max(node_count - 1, 0)):
            any_update = False

            for source, target, weight in edge_list:
                add_state(
                    events=[
                        ExamineGraphEdgeEvent(
                            source=source,
                            target=target,
                        )
                    ],
                    description=(
                        f"Pass {iteration + 1}: examine the edge from "
                        f"{self._label(source)} to {self._label(target)} "
                        f"(weight {weight:g})."
                    ),
                    active_edge=(source, target),
                )

                if math.isinf(distances[source]):
                    continue

                candidate = distances[source] + weight

                if candidate < distances[target]:
                    old_distance = distances[target]
                    distances[target] = candidate
                    any_update = True

                    old_label = (
                        "infinity"
                        if math.isinf(old_distance)
                        else f"{old_distance:g}"
                    )

                    add_state(
                        events=[
                            RelaxEdgeEvent(
                                source=source,
                                target=target,
                                old_distance=old_distance,
                                new_distance=candidate,
                            )
                        ],
                        description=(
                            f"Relax {self._label(target)}: "
                            f"{old_label} -> {candidate:g} through "
                            f"{self._label(source)}."
                        ),
                        active_edge=(source, target),
                    )

            if not any_update:
                add_state(
                    events=[],
                    description=(
                        f"No distance changed during pass "
                        f"{iteration + 1}, so every shortest path has "
                        "already been found. Stopping early."
                    ),
                )

                break

        for source, target, weight in edge_list:
            if math.isinf(distances[source]):
                continue

            if distances[source] + weight < distances[target]:
                add_state(
                    events=[
                        NegativeCycleDetectedEvent(
                            source=source,
                            target=target,
                        )
                    ],
                    description=(
                        f"The edge from {self._label(source)} to "
                        f"{self._label(target)} can still be relaxed "
                        "after every node has settled. The graph "
                        "contains a negative-weight cycle, so shortest "
                        "paths are not well-defined."
                    ),
                    active_edge=(source, target),
                )

                return GraphAlgorithmSimulation(
                    states=tuple(states),
                    algorithm="bellman_ford",
                )

        add_state(
            events=[CompleteGraphAlgorithmEvent(algorithm="bellman_ford")],
            description=(
                "Bellman-Ford is complete. Every reachable node has "
                "its shortest distance from the start."
            ),
        )

        return GraphAlgorithmSimulation(
            states=tuple(states),
            algorithm="bellman_ford",
        )

    def _label(self, node_id: int) -> str:
        node = self.model.get_node(node_id)
        return node.label if node is not None else str(node_id)