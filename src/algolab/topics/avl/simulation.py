from __future__ import annotations

from dataclasses import dataclass

from algolab.simulation.events import SimulationEvent
from algolab.simulation.state import SimulationState
from algolab.topics.avl.model import AVLTree
from algolab.topics.avl.operations import DeleteOperation, InsertOperation
from algolab.topics.bst.simulation import (
    BSTNodeState,
    BSTSimulation,
    BSTSimulationState,
    BSTSimulator,
    CompareNodeEvent,
    CompleteBSTOperationEvent,
    CreateBSTNodeEvent,
    DeleteBSTNodeEvent,
    ReplaceNodeValueEvent,
    UpdateChildEvent,
    VisitBSTNodeEvent,
    _SimulationNode,
)


# ============================================================
# AVL-specific events
# ============================================================


@dataclass(frozen=True)
class CheckBalanceEvent(SimulationEvent):
    """Indicates that a node's height and balance factor were checked."""

    node_id: int
    height: int
    balance_factor: int


@dataclass(frozen=True)
class ImbalanceEvent(SimulationEvent):
    """Indicates that a node's balance factor left the range [-1, 1]."""

    node_id: int
    balance_factor: int
    case: str


@dataclass(frozen=True)
class RotateEvent(SimulationEvent):
    """Indicates that a rotation was performed at a node."""

    node_id: int
    new_root_id: int
    direction: str


# ============================================================
# Simulation state
# ============================================================


@dataclass(frozen=True)
class AVLNodeState(BSTNodeState):
    """One node in a visual AVL snapshot (BST node plus height/balance)."""

    height: int = 1
    balance: int = 0


@dataclass(frozen=True)
class AVLSimulationState(BSTSimulationState):
    """Visual state of an AVL simulation (BST state plus rebalancing info)."""

    # Node whose balance factor is outside [-1, 1].
    unbalanced_node_id: int | None = None

    # The two nodes involved in a rotation that was just performed.
    rotation_node_ids: tuple[int, ...] = ()


# ============================================================
# Internal simulation tree
# ============================================================


@dataclass
class _AVLSimulationNode(_SimulationNode):
    """Mutable internal node used while constructing an AVL simulation."""

    height: int = 1


def _height(node: _AVLSimulationNode | None) -> int:
    return node.height if node is not None else 0


def _balance(node: _AVLSimulationNode | None) -> int:
    if node is None:
        return 0

    return _height(node.left) - _height(node.right)


class _Run:
    """Mutable builder for one simulation: the working tree, the
    states produced so far, and how many rotations were performed."""

    def __init__(
        self,
        simulator: AVLSimulator,
        root: _AVLSimulationNode | None,
    ) -> None:
        self.simulator = simulator
        self.root = root
        self.states: list[SimulationState] = []
        self.rotations = 0

    def add(
        self,
        description: str,
        events: list[SimulationEvent] | None = None,
        **flags,
    ) -> None:
        self.states.append(
            self.simulator._create_state(
                root=self.root,
                step=len(self.states),
                description=description,
                events=events,
                **flags,
            )
        )


def _signed(value: int) -> str:
    """Format a balance factor: +1, -1, or plain 0 (never +0)."""
    return "0" if value == 0 else f"{value:+d}"


def _complete_text(name: str, rotations: int) -> str:
    if rotations == 0:
        return f"{name} operation is complete. No rotation was needed."

    noun = "rotation" if rotations == 1 else "rotations"

    return f"{name} operation is complete after {rotations} {noun}."


# ============================================================
# Simulator
# ============================================================


class AVLSimulator(BSTSimulator):
    """Creates step-by-step simulations for AVL tree operations.

    Search, find_min, find_max, and the traversals never change the
    tree's shape, so they are inherited unchanged from BSTSimulator.
    Only insert and delete (which rebalance) are overridden, along with
    the snapshot helpers so every state carries heights and balance
    factors.
    """

    def __init__(self, model: AVLTree) -> None:
        super().__init__(model)

    # --------------------------------------------------------
    # INSERT
    # --------------------------------------------------------

    def insert(self, value: object) -> BSTSimulation:
        """Create a simulation for inserting a value."""

        root, next_id = self._copy_tree()
        run = _Run(self, root)

        run.add("Initial state of the AVL tree.")

        if run.root is None:
            new_node = _AVLSimulationNode(node_id=next_id, value=value)
            run.root = new_node

            run.add(
                (
                    f"Create a new root node containing {value}. "
                    "A single node is always balanced."
                ),
                events=[CreateBSTNodeEvent(node_id=next_id, value=value)],
                created_node_id=next_id,
            )
            run.add(
                _complete_text("Insert", 0),
                events=[CompleteBSTOperationEvent(operation="insert")],
            )

            return BSTSimulation(
                states=tuple(run.states),
                operation=InsertOperation(value),
            )

        # Walk down exactly like a plain BST, remembering the path so
        # the retrace can walk back up it.
        path: list[_AVLSimulationNode] = []
        current = run.root

        while True:
            path.append(current)

            run.add(
                f"Compare {value} with node {current.value}.",
                events=[
                    CompareNodeEvent(
                        node_id=current.node_id,
                        target_value=value,
                    )
                ],
                active_node_id=current.node_id,
            )

            if value == current.value:
                run.add(
                    (
                        f"Value {value} already exists. "
                        "Insertion cannot continue."
                    ),
                    active_node_id=current.node_id,
                )

                return BSTSimulation(
                    states=tuple(run.states),
                    operation=InsertOperation(value),
                    should_commit=False,
                )

            child = current.left if value < current.value else current.right

            if child is None:
                break

            current = child

        new_node = _AVLSimulationNode(node_id=next_id, value=value)

        run.add(
            (
                f"Create a new node containing {value} "
                "before attaching it to the tree."
            ),
            events=[CreateBSTNodeEvent(node_id=next_id, value=value)],
            active_node_id=current.node_id,
            created_node_id=next_id,
        )

        side = "left" if value < current.value else "right"

        if side == "left":
            current.left = new_node
        else:
            current.right = new_node

        run.add(
            (
                f"Attach {value} as the {side.upper()} child "
                f"of {current.value}. Now retrace upward and check "
                "the balance of each ancestor."
            ),
            events=[
                UpdateChildEvent(
                    parent_id=current.node_id,
                    child_id=next_id,
                    side=side,
                )
            ],
            active_node_id=current.node_id,
            created_node_id=next_id,
        )

        self._retrace(run, path)

        run.add(
            _complete_text("Insert", run.rotations),
            events=[CompleteBSTOperationEvent(operation="insert")],
        )

        return BSTSimulation(
            states=tuple(run.states),
            operation=InsertOperation(value),
        )

    # --------------------------------------------------------
    # DELETE
    # --------------------------------------------------------

    def delete(self, value: object) -> BSTSimulation:
        """Create a simulation for deleting a value."""

        root, _ = self._copy_tree()
        run = _Run(self, root)

        run.add("Initial state of the AVL tree.")

        if run.root is None:
            run.add(
                "The tree is empty. Nothing can be deleted.",
                events=[CompleteBSTOperationEvent(operation="delete_empty")],
            )

            return BSTSimulation(
                states=tuple(run.states),
                operation=DeleteOperation(value),
                should_commit=False,
            )

        # path holds the ancestors of `current` (root first).
        path: list[_AVLSimulationNode] = []
        current: _AVLSimulationNode | None = run.root

        while current is not None:
            run.add(
                f"Compare {value} with node {current.value}.",
                events=[
                    CompareNodeEvent(
                        node_id=current.node_id,
                        target_value=value,
                    )
                ],
                active_node_id=current.node_id,
            )

            if value == current.value:
                break

            path.append(current)
            current = current.left if value < current.value else current.right

        if current is None:
            run.add(f"Value {value} is not present in the tree.")
            run.add(
                "Delete operation is complete.",
                events=[
                    CompleteBSTOperationEvent(operation="delete_not_found")
                ],
            )

            return BSTSimulation(
                states=tuple(run.states),
                operation=DeleteOperation(value),
                should_commit=False,
            )

        if current.left is None or current.right is None:
            self._delete_with_at_most_one_child(run, path, current, value)
        else:
            self._delete_with_two_children(run, path, current)

        self._retrace(run, path)

        run.add(
            _complete_text("Delete", run.rotations),
            events=[CompleteBSTOperationEvent(operation="delete")],
        )

        return BSTSimulation(
            states=tuple(run.states),
            operation=DeleteOperation(value),
        )

    def _delete_with_at_most_one_child(
        self,
        run: _Run,
        path: list[_AVLSimulationNode],
        current: _AVLSimulationNode,
        value: object,
    ) -> None:
        parent = path[-1] if path else None
        child = current.left or current.right

        if child is None:
            run.add(
                (
                    f"Node {current.value} is a leaf. "
                    "It can be removed directly."
                ),
                active_node_id=current.node_id,
            )
            text = f"Delete leaf node {value} from the tree."
        else:
            run.add(
                (
                    f"Node {current.value} has one child. "
                    "Its child will replace it."
                ),
                active_node_id=current.node_id,
            )
            text = f"Replace node {value} with its child."

        deleted_id = current.node_id

        if parent is None:
            run.root = child
        elif parent.left is current:
            parent.left = child
        else:
            parent.right = child

        run.add(
            text,
            events=[DeleteBSTNodeEvent(node_id=deleted_id, value=value)],
            removed_node_id=deleted_id,
        )

    def _delete_with_two_children(
        self,
        run: _Run,
        path: list[_AVLSimulationNode],
        current: _AVLSimulationNode,
    ) -> None:
        run.add(
            (
                f"Node {current.value} has two children. "
                "Find its in-order successor."
            ),
            active_node_id=current.node_id,
        )

        # `current` is now an ancestor of the node that will actually
        # be unlinked, so it joins the retrace path.
        path.append(current)

        successor = current.right

        while successor.left is not None:
            run.add(
                (
                    f"Move to node {successor.left.value} "
                    "while searching for the minimum."
                ),
                events=[
                    CompareNodeEvent(
                        node_id=successor.node_id,
                        target_value=successor.left.value,
                    )
                ],
                active_node_id=successor.node_id,
            )

            path.append(successor)
            successor = successor.left

        successor_parent = path[-1]

        run.add(
            f"The in-order successor is {successor.value}.",
            events=[VisitBSTNodeEvent(node_id=successor.node_id)],
            active_node_id=successor.node_id,
            result_node_id=successor.node_id,
        )

        old_value = current.value
        current.value = successor.value

        run.add(
            (
                f"Replace {old_value} with its in-order "
                f"successor {successor.value}."
            ),
            events=[
                ReplaceNodeValueEvent(
                    node_id=current.node_id,
                    old_value=old_value,
                    new_value=successor.value,
                )
            ],
            active_node_id=current.node_id,
        )

        successor_child = successor.right

        if successor_parent.left is successor:
            successor_parent.left = successor_child
            side = "left"
        else:
            successor_parent.right = successor_child
            side = "right"

        run.add(
            (
                "Remove the original successor node "
                f"{successor.value}. Now retrace upward from "
                f"{successor_parent.value}."
            ),
            events=[
                DeleteBSTNodeEvent(
                    node_id=successor.node_id,
                    value=successor.value,
                ),
                UpdateChildEvent(
                    parent_id=successor_parent.node_id,
                    child_id=(
                        successor_child.node_id
                        if successor_child is not None
                        else None
                    ),
                    side=side,
                ),
            ],
            active_node_id=successor_parent.node_id,
            removed_node_id=successor.node_id,
        )

    # --------------------------------------------------------
    # Retrace + rotations (shared by insert and delete)
    # --------------------------------------------------------

    def _retrace(
        self,
        run: _Run,
        path: list[_AVLSimulationNode],
    ) -> None:
        """Walk back up `path` (deepest node last), updating heights and
        rotating wherever a balance factor leaves [-1, 1].

        Stops early once a subtree's height is back to what it was
        before the operation, since no ancestor can be affected then.
        This matches AVLTree, which rebalances every ancestor but
        changes nothing above that point.
        """

        for index in range(len(path) - 1, -1, -1):
            node = path[index]
            parent = path[index - 1] if index > 0 else None

            old_height = node.height
            node.height = 1 + max(_height(node.left), _height(node.right))
            balance = _balance(node)

            summary = (
                f"Retrace: node {node.value} has left height "
                f"{_height(node.left)} and right height "
                f"{_height(node.right)}, so its balance factor is "
                f"{_signed(balance)}."
            )
            check_event = CheckBalanceEvent(
                node_id=node.node_id,
                height=node.height,
                balance_factor=balance,
            )

            if abs(balance) <= 1:
                if node.height == old_height:
                    tail = (
                        " Balanced, and its height did not change, so "
                        "no ancestor is affected. Retracing stops."
                    )
                elif parent is not None:
                    tail = (
                        " Balanced, but its height changed, so check "
                        "its parent next."
                    )
                else:
                    tail = " Balanced. This is the root, so retracing is done."

                run.add(
                    summary + tail,
                    events=[check_event],
                    active_node_id=node.node_id,
                )

                if node.height == old_height:
                    return

                continue

            # Unbalanced: report it, then name the case.
            run.add(
                (
                    summary
                    + " That is outside -1 to +1, so this node is "
                    "unbalanced."
                ),
                events=[check_event],
                active_node_id=node.node_id,
                unbalanced_node_id=node.node_id,
            )

            heavy = "left" if balance > 0 else "right"
            child = node.left if balance > 0 else node.right
            child_balance = _balance(child)

            # A child leaning the opposite way needs a double rotation.
            needs_double = (
                child_balance < 0 if balance > 0 else child_balance > 0
            )

            case = {
                ("left", False): "Left-Left",
                ("left", True): "Left-Right",
                ("right", False): "Right-Right",
                ("right", True): "Right-Left",
            }[(heavy, needs_double)]

            final_direction = "right" if balance > 0 else "left"
            first_direction = "left" if balance > 0 else "right"

            if needs_double:
                plan = (
                    f"Fix: rotate {first_direction} at {child.value}, "
                    f"then rotate {final_direction} at {node.value}."
                )
            else:
                plan = f"Fix: rotate {final_direction} at {node.value}."

            run.add(
                (
                    f"The {heavy} child {child.value} has balance "
                    f"factor {_signed(child_balance)}, so this is the "
                    f"{case} case. {plan}"
                ),
                events=[
                    ImbalanceEvent(
                        node_id=node.node_id,
                        balance_factor=balance,
                        case=case,
                    )
                ],
                active_node_id=child.node_id,
                unbalanced_node_id=node.node_id,
            )

            if needs_double:
                pivot, moved = self._rotate(child, first_direction)

                if heavy == "left":
                    node.left = pivot
                else:
                    node.right = pivot

                run.rotations += 1

                run.add(
                    self._rotation_text(child, pivot, moved, first_direction),
                    events=[
                        RotateEvent(
                            node_id=child.node_id,
                            new_root_id=pivot.node_id,
                            direction=first_direction,
                        )
                    ],
                    rotation_node_ids=(child.node_id, pivot.node_id),
                )

            pivot, moved = self._rotate(node, final_direction)

            if parent is None:
                run.root = pivot
            elif parent.left is node:
                parent.left = pivot
            else:
                parent.right = pivot

            run.rotations += 1

            text = self._rotation_text(node, pivot, moved, final_direction)
            text += (
                f" This subtree is balanced again: {pivot.value} now has "
                f"balance factor {_signed(_balance(pivot))}."
            )

            if pivot.height == old_height:
                text += (
                    f" The subtree height is back to {old_height}, so no "
                    "ancestor is affected. Retracing stops."
                )
            elif parent is not None:
                text += " The subtree height changed, so check its parent next."

            run.add(
                text,
                events=[
                    RotateEvent(
                        node_id=node.node_id,
                        new_root_id=pivot.node_id,
                        direction=final_direction,
                    )
                ],
                rotation_node_ids=(node.node_id, pivot.node_id),
            )

            if pivot.height == old_height:
                return

    @staticmethod
    def _rotate(
        node: _AVLSimulationNode,
        direction: str,
    ) -> tuple[_AVLSimulationNode, _AVLSimulationNode | None]:
        """Rotate at `node` and fix both heights.

        Returns the new subtree root and the inner subtree that moved
        from one side of the pivot to the other (or None).
        """

        if direction == "right":
            pivot = node.left
            moved = pivot.right
            node.left = moved
            pivot.right = node
        else:
            pivot = node.right
            moved = pivot.left
            node.right = moved
            pivot.left = node

        node.height = 1 + max(_height(node.left), _height(node.right))
        pivot.height = 1 + max(_height(pivot.left), _height(pivot.right))

        return pivot, moved

    @staticmethod
    def _rotation_text(
        node: _AVLSimulationNode,
        pivot: _AVLSimulationNode,
        moved: _AVLSimulationNode | None,
        direction: str,
    ) -> str:
        text = (
            f"Rotate {direction} at {node.value}: {pivot.value} moves up "
            f"and becomes the parent of {node.value}."
        )

        if moved is not None:
            side = "left" if direction == "right" else "right"
            text += (
                f" The subtree rooted at {moved.value} is re-attached "
                f"as the {side} child of {node.value}."
            )

        return text

    # --------------------------------------------------------
    # Snapshot helpers (override BST versions to carry AVL data)
    # --------------------------------------------------------

    def _copy_tree(
        self,
    ) -> tuple[_AVLSimulationNode | None, int]:
        """Copy the model tree, keeping each node's stored height."""

        next_id = 0

        def copy_node(node) -> _AVLSimulationNode | None:
            nonlocal next_id

            if node is None:
                return None

            simulation_node = _AVLSimulationNode(
                node_id=next_id,
                value=node.value,
                height=node.height,
            )

            next_id += 1

            simulation_node.left = copy_node(node.left)
            simulation_node.right = copy_node(node.right)

            return simulation_node

        return copy_node(self.model.root), next_id

    def _create_state(
        self,
        root: _AVLSimulationNode | None,
        step: int,
        description: str,
        events: list[SimulationEvent] | None = None,
        active_node_id: int | None = None,
        created_node_id: int | None = None,
        removed_node_id: int | None = None,
        result_node_id: int | None = None,
        visited_node_ids: tuple[int, ...] = (),
        traversal_values: tuple[object, ...] = (),
        unbalanced_node_id: int | None = None,
        rotation_node_ids: tuple[int, ...] = (),
    ) -> SimulationState:
        """Create a generic simulation state containing AVL data."""

        data = AVLSimulationState(
            nodes=self._snapshot_nodes(root),
            root_id=root.node_id if root is not None else None,
            description=description,
            active_node_id=active_node_id,
            created_node_id=created_node_id,
            removed_node_id=removed_node_id,
            result_node_id=result_node_id,
            visited_node_ids=visited_node_ids,
            traversal_values=traversal_values,
            unbalanced_node_id=unbalanced_node_id,
            rotation_node_ids=rotation_node_ids,
        )

        return SimulationState(
            data=data,
            events=events or [],
            step=step,
        )

    def _snapshot_nodes(
        self,
        root: _AVLSimulationNode | None,
    ) -> tuple[AVLNodeState, ...]:
        nodes: list[AVLNodeState] = []

        def visit(node: _AVLSimulationNode | None) -> None:
            if node is None:
                return

            nodes.append(
                AVLNodeState(
                    node_id=node.node_id,
                    value=node.value,
                    left_id=node.left.node_id if node.left else None,
                    right_id=node.right.node_id if node.right else None,
                    height=node.height,
                    balance=_balance(node),
                )
            )

            visit(node.left)
            visit(node.right)

        visit(root)

        return tuple(nodes)