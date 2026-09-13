from __future__ import annotations

from dataclasses import dataclass

from algolab.simulation.events import SimulationEvent
from algolab.simulation.state import SimulationState
from algolab.topics.bst.model import BinarySearchTree, TreeNode
from algolab.topics.bst.operations import (
    BSTOperation,
    DeleteOperation,
    FindMaxOperation,
    FindMinOperation,
    InOrderTraversalOperation,
    InsertOperation,
    PostOrderTraversalOperation,
    PreOrderTraversalOperation,
    SearchOperation,
)


# ============================================================
# BST-specific events
# ============================================================


@dataclass(frozen=True)
class CompareNodeEvent(SimulationEvent):
    """Indicates that a target value is being compared with a node."""

    node_id: int
    target_value: object


@dataclass(frozen=True)
class VisitBSTNodeEvent(SimulationEvent):
    """Indicates that a BST node is being visited."""

    node_id: int


@dataclass(frozen=True)
class CreateBSTNodeEvent(SimulationEvent):
    """Indicates that a new BST node is being created."""

    node_id: int
    value: object


@dataclass(frozen=True)
class UpdateChildEvent(SimulationEvent):
    """Indicates that a node's left or right child was updated."""

    parent_id: int
    child_id: int | None
    side: str


@dataclass(frozen=True)
class DeleteBSTNodeEvent(SimulationEvent):
    """Indicates that a BST node is being deleted."""

    node_id: int
    value: object


@dataclass(frozen=True)
class ReplaceNodeValueEvent(SimulationEvent):
    """Indicates that a node's value is being replaced."""

    node_id: int
    old_value: object
    new_value: object


@dataclass(frozen=True)
class CompleteBSTOperationEvent(SimulationEvent):
    """Indicates that a BST operation has completed."""

    operation: str


# ============================================================
# Simulation state
# ============================================================


@dataclass(frozen=True)
class BSTNodeState:
    """Represents one node in a visual BST snapshot."""

    node_id: int
    value: object
    left_id: int | None = None
    right_id: int | None = None


@dataclass(frozen=True)
class BSTSimulationState:
    """Represents the visual state of a BST simulation."""

    nodes: tuple[BSTNodeState, ...]
    root_id: int | None
    description: str

    # Node currently being inspected or compared.
    active_node_id: int | None = None

    # Node created during INSERT.
    created_node_id: int | None = None

    # Node removed during DELETE.
    removed_node_id: int | None = None

    # Node whose value was inspected by MIN/MAX/SEARCH.
    result_node_id: int | None = None

    # Traversal information.
    visited_node_ids: tuple[int, ...] = ()
    traversal_values: tuple[object, ...] = ()


# ============================================================
# Complete simulation
# ============================================================


@dataclass(frozen=True)
class BSTSimulation:
    """Represents a complete binary search tree simulation."""

    states: tuple[SimulationState, ...]
    operation: BSTOperation

    def commit(self, model: BinarySearchTree) -> object | None:
        """Commit the simulated operation to the BST model."""
        return self.operation.commit(model)


# ============================================================
# Internal simulation tree
# ============================================================


@dataclass
class _SimulationNode:
    """Mutable internal node used while constructing a simulation."""

    node_id: int
    value: object
    left: _SimulationNode | None = None
    right: _SimulationNode | None = None


# ============================================================
# Simulator
# ============================================================


class BSTSimulator:
    """Creates step-by-step simulations for BST operations."""

    def __init__(self, model: BinarySearchTree) -> None:
        self.model = model

    # --------------------------------------------------------
    # INSERT
    # --------------------------------------------------------

    def insert(self, value: object) -> BSTSimulation:
        """Create a simulation for inserting a value."""

        root, next_id = self._copy_tree()

        states: list[SimulationState] = []

        states.append(
            self._create_state(
                root=root,
                step=0,
                description="Initial state of the binary search tree.",
            )
        )

        # Empty tree.
        if root is None:
            new_node = _SimulationNode(
                node_id=next_id,
                value=value,
            )

            states.append(
                self._create_state(
                    root=new_node,
                    step=1,
                    description=(
                        f"Create a new root node containing {value}."
                    ),
                    events=[
                        CreateBSTNodeEvent(
                            node_id=next_id,
                            value=value,
                        )
                    ],
                    created_node_id=next_id,
                )
            )

            states.append(
                self._create_state(
                    root=new_node,
                    step=2,
                    description="Insert operation is complete.",
                    events=[
                        CompleteBSTOperationEvent(
                            operation="insert",
                        )
                    ],
                )
            )

            return BSTSimulation(
                states=tuple(states),
                operation=InsertOperation(value),
            )

        current = root

        while True:
            states.append(
                self._create_state(
                    root=root,
                    step=len(states),
                    description=(
                        f"Compare {value} with node {current.value}."
                    ),
                    events=[
                        CompareNodeEvent(
                            node_id=current.node_id,
                            target_value=value,
                        )
                    ],
                    active_node_id=current.node_id,
                )
            )

            if value == current.value:
                states.append(
                    self._create_state(
                        root=root,
                        step=len(states),
                        description=(
                            f"Value {value} already exists. "
                            "Insertion cannot continue."
                        ),
                        events=[],
                        active_node_id=current.node_id,
                    )
                )

                return BSTSimulation(
                    states=tuple(states),
                    operation=InsertOperation(value),
                )

            if value < current.value:
                if current.left is not None:
                    current = current.left
                    continue

                new_node = _SimulationNode(
                    node_id=next_id,
                    value=value,
                )

                states.append(
                    self._create_state(
                        root=root,
                        step=len(states),
                        description=(
                            f"Create a new node containing {value} "
                            "before attaching it to the tree."
                        ),
                        events=[
                            CreateBSTNodeEvent(
                                node_id=next_id,
                                value=value,
                            )
                        ],
                        active_node_id=current.node_id,
                        created_node_id=next_id,
                    )
                )

                current.left = new_node

                states.append(
                    self._create_state(
                        root=root,
                        step=len(states),
                        description=(
                            f"Attach {value} as the LEFT child "
                            f"of {current.value}."
                        ),
                        events=[
                            UpdateChildEvent(
                                parent_id=current.node_id,
                                child_id=next_id,
                                side="left",
                            )
                        ],
                        active_node_id=current.node_id,
                    )
                )

                states.append(
                    self._create_state(
                        root=root,
                        step=len(states),
                        description="Insert operation is complete.",
                        events=[
                            CompleteBSTOperationEvent(
                                operation="insert",
                            )
                        ],
                    )
                )

                return BSTSimulation(
                    states=tuple(states),
                    operation=InsertOperation(value),
                )

            if current.right is not None:
                current = current.right
                continue

            new_node = _SimulationNode(
                node_id=next_id,
                value=value,
            )

            states.append(
                self._create_state(
                    root=root,
                    step=len(states),
                    description=(
                        f"Create a new node containing {value} "
                        "before attaching it to the tree."
                    ),
                    events=[
                        CreateBSTNodeEvent(
                            node_id=next_id,
                            value=value,
                        )
                    ],
                    active_node_id=current.node_id,
                    created_node_id=next_id,
                )
            )

            current.right = new_node

            states.append(
                self._create_state(
                    root=root,
                    step=len(states),
                    description=(
                        f"Attach {value} as the RIGHT child "
                        f"of {current.value}."
                    ),
                    events=[
                        UpdateChildEvent(
                            parent_id=current.node_id,
                            child_id=next_id,
                            side="right",
                        )
                    ],
                    active_node_id=current.node_id,
                )
            )

            states.append(
                self._create_state(
                    root=root,
                    step=len(states),
                    description="Insert operation is complete.",
                    events=[
                        CompleteBSTOperationEvent(
                            operation="insert",
                        )
                    ],
                )
            )

            return BSTSimulation(
                states=tuple(states),
                operation=InsertOperation(value),
            )

    # --------------------------------------------------------
    # SEARCH
    # --------------------------------------------------------

    def search(self, value: object) -> BSTSimulation:
        """Create a simulation for searching for a value."""

        root, _ = self._copy_tree()
        states: list[SimulationState] = []

        states.append(
            self._create_state(
                root=root,
                step=0,
                description="Initial state of the binary search tree.",
            )
        )

        current = root

        while current is not None:
            states.append(
                self._create_state(
                    root=root,
                    step=len(states),
                    description=(
                        f"Compare {value} with node {current.value}."
                    ),
                    events=[
                        CompareNodeEvent(
                            node_id=current.node_id,
                            target_value=value,
                        )
                    ],
                    active_node_id=current.node_id,
                )
            )

            if value == current.value:
                states.append(
                    self._create_state(
                        root=root,
                        step=len(states),
                        description=(
                            f"Found {value} in the binary search tree."
                        ),
                        events=[
                            VisitBSTNodeEvent(
                                node_id=current.node_id,
                            )
                        ],
                        active_node_id=current.node_id,
                        result_node_id=current.node_id,
                    )
                )

                states.append(
                    self._create_state(
                        root=root,
                        step=len(states),
                        description="Search operation is complete.",
                        events=[
                            CompleteBSTOperationEvent(
                                operation="search",
                            )
                        ],
                        result_node_id=current.node_id,
                    )
                )

                return BSTSimulation(
                    states=tuple(states),
                    operation=SearchOperation(value),
                )

            if value < current.value:
                current = current.left
            else:
                current = current.right

        not_found_description = (
            f"Value {value} is not present in the tree."
        )

        states.append(
            self._create_state(
                root=root,
                step=len(states),
                description=not_found_description,
                events=[],
            )
        )

        states.append(
            self._create_state(
                root=root,
                step=len(states),
                description=(
                    f"Search operation is complete. "
                    f"Value {value} is not present in the tree."
                ),
                events=[
                    CompleteBSTOperationEvent(
                        operation="search_not_found",
                    )
                ],
            )
        )

        return BSTSimulation(
            states=tuple(states),
            operation=SearchOperation(value),
        )

    # --------------------------------------------------------
    # DELETE
    # --------------------------------------------------------

    def delete(self, value: object) -> BSTSimulation:
        """Create a simulation for deleting a value."""

        root, _ = self._copy_tree()
        states: list[SimulationState] = []

        states.append(
            self._create_state(
                root=root,
                step=0,
                description="Initial state of the binary search tree.",
            )
        )

        if root is None:
            states.append(
                self._create_state(
                    root=root,
                    step=1,
                    description=(
                        "The tree is empty. Nothing can be deleted."
                    ),
                    events=[
                        CompleteBSTOperationEvent(
                            operation="delete_empty",
                        )
                    ],
                )
            )

            return BSTSimulation(
                states=tuple(states),
                operation=DeleteOperation(value),
            )

        parent: _SimulationNode | None = None
        current = root

        # Search for the node first.
        while current is not None:
            states.append(
                self._create_state(
                    root=root,
                    step=len(states),
                    description=(
                        f"Compare {value} with node {current.value}."
                    ),
                    events=[
                        CompareNodeEvent(
                            node_id=current.node_id,
                            target_value=value,
                        )
                    ],
                    active_node_id=current.node_id,
                )
            )

            if value == current.value:
                break

            parent = current

            if value < current.value:
                current = current.left
            else:
                current = current.right

        if current is None:
            states.append(
                self._create_state(
                    root=root,
                    step=len(states),
                    description=(
                        f"Value {value} is not present in the tree."
                    ),
                )
            )

            states.append(
                self._create_state(
                    root=root,
                    step=len(states),
                    description="Delete operation is complete.",
                    events=[
                        CompleteBSTOperationEvent(
                            operation="delete_not_found",
                        )
                    ],
                )
            )

            return BSTSimulation(
                states=tuple(states),
                operation=DeleteOperation(value),
            )

        # Case 1: leaf node.
        if current.left is None and current.right is None:
            states.append(
                self._create_state(
                    root=root,
                    step=len(states),
                    description=(
                        f"Node {current.value} is a leaf. "
                        "It can be removed directly."
                    ),
                    active_node_id=current.node_id,
                )
            )

            deleted_id = current.node_id

            root = self._replace_child(
                root=root,
                parent=parent,
                old_child=current,
                new_child=None,
            )

            states.append(
                self._create_state(
                    root=root,
                    step=len(states),
                    description=(
                        f"Delete leaf node {value} from the tree."
                    ),
                    events=[
                        DeleteBSTNodeEvent(
                            node_id=deleted_id,
                            value=value,
                        )
                    ],
                    removed_node_id=deleted_id,
                )
            )

            states.append(
                self._create_state(
                    root=root,
                    step=len(states),
                    description="Delete operation is complete.",
                    events=[
                        CompleteBSTOperationEvent(
                            operation="delete",
                        )
                    ],
                )
            )

            return BSTSimulation(
                states=tuple(states),
                operation=DeleteOperation(value),
            )

        # Case 2: one child.
        if current.left is None or current.right is None:
            child = current.left or current.right

            states.append(
                self._create_state(
                    root=root,
                    step=len(states),
                    description=(
                        f"Node {current.value} has one child. "
                        "Its child will replace it."
                    ),
                    active_node_id=current.node_id,
                )
            )

            deleted_id = current.node_id

            root = self._replace_child(
                root=root,
                parent=parent,
                old_child=current,
                new_child=child,
            )

            states.append(
                self._create_state(
                    root=root,
                    step=len(states),
                    description=(
                        f"Replace node {value} with its child."
                    ),
                    events=[
                        DeleteBSTNodeEvent(
                            node_id=deleted_id,
                            value=value,
                        )
                    ],
                    removed_node_id=deleted_id,
                )
            )

            states.append(
                self._create_state(
                    root=root,
                    step=len(states),
                    description="Delete operation is complete.",
                    events=[
                        CompleteBSTOperationEvent(
                            operation="delete",
                        )
                    ],
                )
            )

            return BSTSimulation(
                states=tuple(states),
                operation=DeleteOperation(value),
            )

        # Case 3: two children.
        states.append(
            self._create_state(
                root=root,
                step=len(states),
                description=(
                    f"Node {current.value} has two children. "
                    "Find its in-order successor."
                ),
                active_node_id=current.node_id,
            )
        )

        successor_parent = current
        successor = current.right

        while successor.left is not None:
            states.append(
                self._create_state(
                    root=root,
                    step=len(states),
                    description=(
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
            )

            successor_parent = successor
            successor = successor.left

        states.append(
            self._create_state(
                root=root,
                step=len(states),
                description=(
                    f"The in-order successor is {successor.value}."
                ),
                events=[
                    VisitBSTNodeEvent(
                        node_id=successor.node_id,
                    )
                ],
                active_node_id=successor.node_id,
                result_node_id=successor.node_id,
            )
        )

        old_value = current.value
        current.value = successor.value

        states.append(
            self._create_state(
                root=root,
                step=len(states),
                description=(
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
        )

        successor_child = successor.right

        if successor_parent.left is successor:
            successor_parent.left = successor_child
            side = "left"
        else:
            successor_parent.right = successor_child
            side = "right"

        states.append(
            self._create_state(
                root=root,
                step=len(states),
                description=(
                    f"Remove the original successor node "
                    f"{successor.value}."
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
        )

        states.append(
            self._create_state(
                root=root,
                step=len(states),
                description="Delete operation is complete.",
                events=[
                    CompleteBSTOperationEvent(
                        operation="delete",
                    )
                ],
            )
        )

        return BSTSimulation(
            states=tuple(states),
            operation=DeleteOperation(value),
        )

    # --------------------------------------------------------
    # FIND MIN
    # --------------------------------------------------------

    def find_min(self) -> BSTSimulation:
        """Create a simulation for finding the minimum value."""

        root, _ = self._copy_tree()
        states: list[SimulationState] = []

        states.append(
            self._create_state(
                root=root,
                step=0,
                description="Initial state of the binary search tree.",
            )
        )

        if root is None:
            states.append(
                self._create_state(
                    root=root,
                    step=1,
                    description=(
                        "The tree is empty. A minimum does not exist."
                    ),
                    events=[
                        CompleteBSTOperationEvent(
                            operation="find_min_empty",
                        )
                    ],
                )
            )

            return BSTSimulation(
                states=tuple(states),
                operation=FindMinOperation(),
            )

        current = root

        while current.left is not None:
            states.append(
                self._create_state(
                    root=root,
                    step=len(states),
                    description=(
                        f"Node {current.value} has a LEFT child. "
                        "Move left."
                    ),
                    events=[
                        VisitBSTNodeEvent(
                            node_id=current.node_id,
                        )
                    ],
                    active_node_id=current.node_id,
                )
            )

            current = current.left

        states.append(
            self._create_state(
                root=root,
                step=len(states),
                description=(
                    f"Node {current.value} has no LEFT child. "
                    "It is the minimum."
                ),
                events=[
                    VisitBSTNodeEvent(
                        node_id=current.node_id,
                    )
                ],
                active_node_id=current.node_id,
                result_node_id=current.node_id,
            )
        )

        states.append(
            self._create_state(
                root=root,
                step=len(states),
                description=(
                    f"Find minimum operation is complete. "
                    f"Minimum is {current.value}."
                ),
                events=[
                    CompleteBSTOperationEvent(
                        operation="find_min",
                    )
                ],
                result_node_id=current.node_id,
            )
        )

        return BSTSimulation(
            states=tuple(states),
            operation=FindMinOperation(),
        )

    # --------------------------------------------------------
    # FIND MAX
    # --------------------------------------------------------

    def find_max(self) -> BSTSimulation:
        """Create a simulation for finding the maximum value."""

        root, _ = self._copy_tree()
        states: list[SimulationState] = []

        states.append(
            self._create_state(
                root=root,
                step=0,
                description="Initial state of the binary search tree.",
            )
        )

        if root is None:
            states.append(
                self._create_state(
                    root=root,
                    step=1,
                    description=(
                        "The tree is empty. A maximum does not exist."
                    ),
                    events=[
                        CompleteBSTOperationEvent(
                            operation="find_max_empty",
                        )
                    ],
                )
            )

            return BSTSimulation(
                states=tuple(states),
                operation=FindMaxOperation(),
            )

        current = root

        while current.right is not None:
            states.append(
                self._create_state(
                    root=root,
                    step=len(states),
                    description=(
                        f"Node {current.value} has a RIGHT child. "
                        "Move right."
                    ),
                    events=[
                        VisitBSTNodeEvent(
                            node_id=current.node_id,
                        )
                    ],
                    active_node_id=current.node_id,
                )
            )

            current = current.right

        states.append(
            self._create_state(
                root=root,
                step=len(states),
                description=(
                    f"Node {current.value} has no RIGHT child. "
                    "It is the maximum."
                ),
                events=[
                    VisitBSTNodeEvent(
                        node_id=current.node_id,
                    )
                ],
                active_node_id=current.node_id,
                result_node_id=current.node_id,
            )
        )

        states.append(
            self._create_state(
                root=root,
                step=len(states),
                description=(
                    f"Find maximum operation is complete. "
                    f"Maximum is {current.value}."
                ),
                events=[
                    CompleteBSTOperationEvent(
                        operation="find_max",
                    )
                ],
                result_node_id=current.node_id,
            )
        )

        return BSTSimulation(
            states=tuple(states),
            operation=FindMaxOperation(),
        )

    # --------------------------------------------------------
    # TRAVERSALS
    # --------------------------------------------------------

    def in_order(self) -> BSTSimulation:
        """Create a simulation for in-order traversal."""
        return self._traversal(
            operation=InOrderTraversalOperation(),
            traversal_name="in-order",
            order="in_order",
        )

    def pre_order(self) -> BSTSimulation:
        """Create a simulation for pre-order traversal."""
        return self._traversal(
            operation=PreOrderTraversalOperation(),
            traversal_name="pre-order",
            order="pre_order",
        )

    def post_order(self) -> BSTSimulation:
        """Create a simulation for post-order traversal."""
        return self._traversal(
            operation=PostOrderTraversalOperation(),
            traversal_name="post-order",
            order="post_order",
        )

    def _traversal(
        self,
        operation: BSTOperation,
        traversal_name: str,
        order: str,
    ) -> BSTSimulation:
        root, _ = self._copy_tree()
        states: list[SimulationState] = []

        states.append(
            self._create_state(
                root=root,
                step=0,
                description="Initial state of the binary search tree.",
            )
        )

        visited_nodes: list[int] = []
        traversal_values: list[object] = []

        if order == "in_order":
            node_order = self._in_order_nodes(root)
        elif order == "pre_order":
            node_order = self._pre_order_nodes(root)
        else:
            node_order = self._post_order_nodes(root)

        for node in node_order:
            visited_nodes.append(node.node_id)
            traversal_values.append(node.value)

            states.append(
                self._create_state(
                    root=root,
                    step=len(states),
                    description=(
                        f"Visit node {node.value} "
                        f"as part of the {traversal_name} traversal."
                    ),
                    events=[
                        VisitBSTNodeEvent(
                            node_id=node.node_id,
                        )
                    ],
                    active_node_id=node.node_id,
                    visited_node_ids=tuple(visited_nodes),
                    traversal_values=tuple(traversal_values),
                )
            )

        states.append(
            self._create_state(
                root=root,
                step=len(states),
                description=(
                    f"{traversal_name.capitalize()} traversal "
                    "is complete."
                ),
                events=[
                    CompleteBSTOperationEvent(
                        operation=traversal_name.replace("-", "_"),
                    )
                ],
                visited_node_ids=tuple(visited_nodes),
                traversal_values=tuple(traversal_values),
            )
        )

        return BSTSimulation(
            states=tuple(states),
            operation=operation,
        )

    # --------------------------------------------------------
    # Snapshot helpers
    # --------------------------------------------------------

    def _copy_tree(
        self,
    ) -> tuple[_SimulationNode | None, int]:
        """Copy the model tree and assign stable simulation node IDs."""

        next_id = 0

        def copy_node(
            node: TreeNode | None,
        ) -> _SimulationNode | None:
            nonlocal next_id

            if node is None:
                return None

            simulation_node = _SimulationNode(
                node_id=next_id,
                value=node.value,
            )

            next_id += 1

            simulation_node.left = copy_node(node.left)
            simulation_node.right = copy_node(node.right)

            return simulation_node

        return copy_node(self.model.root), next_id

    def _create_state(
        self,
        root: _SimulationNode | None,
        step: int,
        description: str,
        events: list[SimulationEvent] | None = None,
        active_node_id: int | None = None,
        created_node_id: int | None = None,
        removed_node_id: int | None = None,
        result_node_id: int | None = None,
        visited_node_ids: tuple[int, ...] = (),
        traversal_values: tuple[object, ...] = (),
    ) -> SimulationState:
        """Create a generic simulation state containing BST data."""

        nodes = self._snapshot_nodes(root)

        data = BSTSimulationState(
            nodes=nodes,
            root_id=root.node_id if root is not None else None,
            description=description,
            active_node_id=active_node_id,
            created_node_id=created_node_id,
            removed_node_id=removed_node_id,
            result_node_id=result_node_id,
            visited_node_ids=visited_node_ids,
            traversal_values=traversal_values,
        )

        return SimulationState(
            data=data,
            events=events or [],
            step=step,
        )

    def _snapshot_nodes(
        self,
        root: _SimulationNode | None,
    ) -> tuple[BSTNodeState, ...]:
        """Convert the mutable simulation tree into an immutable snapshot."""

        nodes: list[BSTNodeState] = []

        def visit(node: _SimulationNode | None) -> None:
            if node is None:
                return

            nodes.append(
                BSTNodeState(
                    node_id=node.node_id,
                    value=node.value,
                    left_id=node.left.node_id if node.left else None,
                    right_id=node.right.node_id if node.right else None,
                )
            )

            visit(node.left)
            visit(node.right)

        visit(root)

        return tuple(nodes)

    def _replace_child(
        self,
        root: _SimulationNode,
        parent: _SimulationNode | None,
        old_child: _SimulationNode,
        new_child: _SimulationNode | None,
    ) -> _SimulationNode | None:
        """Replace a parent's child, or replace the root."""

        if parent is None:
            return new_child

        if parent.left is old_child:
            parent.left = new_child
        else:
            parent.right = new_child

        return root

    # --------------------------------------------------------
    # Traversal helpers
    # --------------------------------------------------------

    def _in_order_nodes(
        self,
        node: _SimulationNode | None,
    ) -> list[_SimulationNode]:
        nodes: list[_SimulationNode] = []

        def visit(current: _SimulationNode | None) -> None:
            if current is None:
                return

            visit(current.left)
            nodes.append(current)
            visit(current.right)

        visit(node)

        return nodes

    def _pre_order_nodes(
        self,
        node: _SimulationNode | None,
    ) -> list[_SimulationNode]:
        nodes: list[_SimulationNode] = []

        def visit(current: _SimulationNode | None) -> None:
            if current is None:
                return

            nodes.append(current)
            visit(current.left)
            visit(current.right)

        visit(node)

        return nodes

    def _post_order_nodes(
        self,
        node: _SimulationNode | None,
    ) -> list[_SimulationNode]:
        nodes: list[_SimulationNode] = []

        def visit(current: _SimulationNode | None) -> None:
            if current is None:
                return

            visit(current.left)
            visit(current.right)
            nodes.append(current)

        visit(node)

        return nodes