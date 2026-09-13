from __future__ import annotations

import pytest

from algolab.simulation.events import SimulationEvent
from algolab.simulation.state import SimulationState
from algolab.topics.bst.model import BinarySearchTree
from algolab.topics.bst.operations import (
    DeleteOperation,
    FindMaxOperation,
    FindMinOperation,
    InOrderTraversalOperation,
    InsertOperation,
    PostOrderTraversalOperation,
    PreOrderTraversalOperation,
    SearchOperation,
)
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
)


# ============================================================
# Helpers
# ============================================================


def create_tree(
    values: list[int],
) -> BinarySearchTree[int]:
    """Create a BST containing the given values."""
    tree = BinarySearchTree[int]()

    for value in values:
        tree.insert(value)

    return tree


def get_data(
    simulation: BSTSimulation,
    index: int,
) -> BSTSimulationState:
    """Return topic-specific data from a simulation state."""
    return simulation.states[index].data


def get_events(
    simulation: BSTSimulation,
    index: int,
) -> list[SimulationEvent]:
    """Return events from a simulation state."""
    return simulation.states[index].events


# ============================================================
# Basic simulation structure
# ============================================================


def test_simulation_contains_generic_simulation_states() -> None:
    tree = create_tree([50, 30, 70])
    simulation = BSTSimulator(tree).insert(20)

    assert simulation.states

    for state in simulation.states:
        assert isinstance(state, SimulationState)
        assert isinstance(state.data, BSTSimulationState)


def test_simulation_states_have_sequential_steps() -> None:
    tree = create_tree([50, 30, 70])
    simulation = BSTSimulator(tree).insert(20)

    assert [state.step for state in simulation.states] == list(
        range(len(simulation.states))
    )


def test_simulation_does_not_modify_model() -> None:
    tree = create_tree([50, 30, 70])
    simulator = BSTSimulator(tree)

    simulator.insert(20)

    assert tree.in_order() == [30, 50, 70]
    assert tree.size == 3


def test_simulation_state_contains_immutable_node_snapshot() -> None:
    tree = create_tree([50, 30, 70])
    simulation = BSTSimulator(tree).insert(20)

    initial = get_data(simulation, 0)

    assert isinstance(initial.nodes, tuple)

    for node in initial.nodes:
        assert isinstance(node, BSTNodeState)


# ============================================================
# INSERT
# ============================================================


def test_insert_simulation_creates_root_for_empty_tree() -> None:
    tree = BinarySearchTree[int]()
    simulation = BSTSimulator(tree).insert(50)

    initial = get_data(simulation, 0)
    created = get_data(simulation, 1)
    complete = get_data(simulation, 2)

    assert initial.nodes == ()
    assert initial.root_id is None

    assert created.root_id == 0
    assert len(created.nodes) == 1
    assert created.nodes[0].value == 50
    assert created.created_node_id == 0

    assert isinstance(
        get_events(simulation, 1)[0],
        CreateBSTNodeEvent,
    )

    assert isinstance(
        get_events(simulation, 2)[0],
        CompleteBSTOperationEvent,
    )

    assert complete.description == "Insert operation is complete."


def test_insert_simulation_inserts_left_child() -> None:
    tree = create_tree([50])
    simulation = BSTSimulator(tree).insert(30)

    assert len(simulation.states) == 5

    comparison = get_data(simulation, 1)
    creation = get_data(simulation, 2)
    attached = get_data(simulation, 3)

    assert comparison.active_node_id == 0

    compare_event = get_events(simulation, 1)[0]

    assert isinstance(compare_event, CompareNodeEvent)
    assert compare_event.node_id == 0
    assert compare_event.target_value == 30

    assert creation.created_node_id == 1
    assert len(creation.nodes) == 1
    assert creation.nodes[0].value == 50

    create_event = get_events(simulation, 2)[0]

    assert isinstance(create_event, CreateBSTNodeEvent)
    assert create_event.node_id == 1
    assert create_event.value == 30

    assert len(attached.nodes) == 2

    root = next(
        node
        for node in attached.nodes
        if node.node_id == attached.root_id
    )

    assert root.value == 50
    assert root.left_id == 1
    assert root.right_id is None

    update_event = get_events(simulation, 3)[0]

    assert isinstance(update_event, UpdateChildEvent)
    assert update_event.parent_id == 0
    assert update_event.child_id == 1
    assert update_event.side == "left"


def test_insert_simulation_inserts_right_child() -> None:
    tree = create_tree([50])
    simulation = BSTSimulator(tree).insert(70)

    attached = get_data(simulation, 3)

    root = next(
        node
        for node in attached.nodes
        if node.node_id == attached.root_id
    )

    assert root.right_id == 1
    assert root.left_id is None

    update_event = get_events(simulation, 3)[0]

    assert isinstance(update_event, UpdateChildEvent)
    assert update_event.parent_id == 0
    assert update_event.child_id == 1
    assert update_event.side == "right"


def test_insert_simulation_searches_multiple_levels() -> None:
    tree = create_tree([50, 30, 70])
    simulation = BSTSimulator(tree).insert(20)

    comparison_events = [
        event
        for state in simulation.states
        for event in state.events
        if isinstance(event, CompareNodeEvent)
    ]

    assert len(comparison_events) == 2

    assert comparison_events[0].node_id == 0
    assert comparison_events[0].target_value == 20

    assert comparison_events[1].node_id == 1
    assert comparison_events[1].target_value == 20


def test_insert_simulation_duplicate_does_not_change_snapshot() -> None:
    tree = create_tree([50, 30, 70])
    simulation = BSTSimulator(tree).insert(50)

    assert get_data(simulation, -1).nodes == get_data(
        simulation,
        0,
    ).nodes

    assert "already exists" in get_data(
        simulation,
        -1,
    ).description


def test_insert_simulation_commit_changes_model() -> None:
    tree = create_tree([50, 30, 70])
    simulation = BSTSimulator(tree).insert(20)

    result = simulation.commit(tree)

    assert result is not None
    assert tree.in_order() == [20, 30, 50, 70]


def test_insert_simulation_uses_insert_operation() -> None:
    tree = create_tree([50])
    simulation = BSTSimulator(tree).insert(30)

    assert isinstance(simulation.operation, InsertOperation)


# ============================================================
# SEARCH
# ============================================================


def test_search_simulation_finds_existing_value() -> None:
    tree = create_tree([50, 30, 70, 20, 40, 60, 80])
    simulation = BSTSimulator(tree).search(60)

    result_states = [
        state
        for state in simulation.states
        if get_data(simulation, state.step).result_node_id
        is not None
    ]

    assert result_states

    result = get_data(
        simulation,
        result_states[0].step,
    )

    assert result.result_node_id is not None
    assert result.description.startswith("Found 60")


def test_search_simulation_has_comparisons() -> None:
    tree = create_tree([50, 30, 70, 20, 40, 60, 80])
    simulation = BSTSimulator(tree).search(60)

    comparison_events = [
        event
        for state in simulation.states
        for event in state.events
        if isinstance(event, CompareNodeEvent)
    ]

    assert len(comparison_events) == 3
    assert comparison_events[0].target_value == 60
    assert comparison_events[1].target_value == 60


def test_search_simulation_not_found() -> None:
    tree = create_tree([50, 30, 70])
    simulation = BSTSimulator(tree).search(100)

    final = get_data(simulation, -1)

    assert final.result_node_id is None
    assert "not present" in final.description

    complete_event = get_events(simulation, -1)[0]

    assert isinstance(
        complete_event,
        CompleteBSTOperationEvent,
    )
    assert complete_event.operation == "search_not_found"


def test_search_simulation_empty_tree() -> None:
    tree = BinarySearchTree[int]()
    simulation = BSTSimulator(tree).search(50)

    assert len(simulation.states) == 3
    assert get_data(simulation, -1).root_id is None
    assert "not present" in get_data(simulation, -2).description


def test_search_simulation_commit() -> None:
    tree = create_tree([50, 30, 70])
    simulation = BSTSimulator(tree).search(30)

    result = simulation.commit(tree)

    assert result is tree.search(30)


def test_search_simulation_uses_search_operation() -> None:
    tree = create_tree([50])
    simulation = BSTSimulator(tree).search(50)

    assert isinstance(simulation.operation, SearchOperation)


# ============================================================
# DELETE
# ============================================================


def test_delete_simulation_empty_tree() -> None:
    tree = BinarySearchTree[int]()
    simulation = BSTSimulator(tree).delete(50)

    assert len(simulation.states) == 2

    final = get_data(simulation, -1)

    assert final.root_id is None

    event = get_events(simulation, -1)[0]

    assert isinstance(event, CompleteBSTOperationEvent)
    assert event.operation == "delete_empty"


def test_delete_simulation_leaf() -> None:
    tree = create_tree([50, 30, 70])
    simulation = BSTSimulator(tree).delete(30)

    final = get_data(simulation, -2)

    assert all(node.value != 30 for node in final.nodes)

    delete_events = [
        event
        for state in simulation.states
        for event in state.events
        if isinstance(event, DeleteBSTNodeEvent)
    ]

    assert len(delete_events) == 1
    assert delete_events[0].value == 30


def test_delete_simulation_leaf_updates_parent_link() -> None:
    tree = create_tree([50, 30, 70])
    simulation = BSTSimulator(tree).delete(30)

    state = simulation.states[-2].data

    root = next(
        node
        for node in state.nodes
        if node.node_id == state.root_id
    )

    assert root.left_id is None


def test_delete_simulation_one_child() -> None:
    tree = create_tree([50, 30, 20])
    simulation = BSTSimulator(tree).delete(30)

    final = get_data(simulation, -2)

    assert [node.value for node in final.nodes] == [50, 20]

    root = next(
        node
        for node in final.nodes
        if node.node_id == final.root_id
    )

    assert root.left_id is not None

    replacement = next(
        node
        for node in final.nodes
        if node.node_id == root.left_id
    )

    assert replacement.value == 20


def test_delete_simulation_root_with_one_child() -> None:
    tree = create_tree([50, 30])
    simulation = BSTSimulator(tree).delete(50)

    final = get_data(simulation, -2)

    assert final.root_id is not None

    root = next(
        node
        for node in final.nodes
        if node.node_id == final.root_id
    )

    assert root.value == 30


def test_delete_simulation_two_children_uses_successor() -> None:
    tree = create_tree([50, 30, 70, 20, 40, 60, 80])
    simulation = BSTSimulator(tree).delete(50)

    replacement_events = [
        event
        for state in simulation.states
        for event in state.events
        if isinstance(event, ReplaceNodeValueEvent)
    ]

    assert len(replacement_events) == 1

    replacement_event = replacement_events[0]

    assert replacement_event.old_value == 50
    assert replacement_event.new_value == 60


def test_delete_simulation_two_children_removes_successor() -> None:
    tree = create_tree([50, 30, 70, 20, 40, 60, 80])
    simulation = BSTSimulator(tree).delete(50)

    delete_events = [
        event
        for state in simulation.states
        for event in state.events
        if isinstance(event, DeleteBSTNodeEvent)
    ]

    assert len(delete_events) == 1
    assert delete_events[0].value == 60


def test_delete_simulation_two_children_final_tree_shape() -> None:
    tree = create_tree([50, 30, 70, 20, 40, 60, 80])
    simulation = BSTSimulator(tree).delete(50)

    final = get_data(simulation, -2)

    root = next(
        node
        for node in final.nodes
        if node.node_id == final.root_id
    )

    assert root.value == 60

    left = next(
        node
        for node in final.nodes
        if node.node_id == root.left_id
    )

    right = next(
        node
        for node in final.nodes
        if node.node_id == root.right_id
    )

    assert left.value == 30
    assert right.value == 70


def test_delete_simulation_missing_value() -> None:
    tree = create_tree([50, 30, 70])
    simulation = BSTSimulator(tree).delete(100)

    final = get_data(simulation, -1)

    assert final.nodes == get_data(simulation, 0).nodes

    event = get_events(simulation, -1)[0]

    assert isinstance(event, CompleteBSTOperationEvent)
    assert event.operation == "delete_not_found"


def test_delete_simulation_commit() -> None:
    tree = create_tree([50, 30, 70])
    simulation = BSTSimulator(tree).delete(30)

    result = simulation.commit(tree)

    assert result == 30
    assert tree.in_order() == [50, 70]


def test_delete_simulation_uses_delete_operation() -> None:
    tree = create_tree([50])
    simulation = BSTSimulator(tree).delete(50)

    assert isinstance(simulation.operation, DeleteOperation)


# ============================================================
# MINIMUM
# ============================================================


def test_find_min_simulation_empty_tree() -> None:
    tree = BinarySearchTree[int]()
    simulation = BSTSimulator(tree).find_min()

    assert len(simulation.states) == 2

    event = get_events(simulation, -1)[0]

    assert isinstance(event, CompleteBSTOperationEvent)
    assert event.operation == "find_min_empty"


def test_find_min_simulation_finds_leftmost_node() -> None:
    tree = create_tree([50, 30, 70, 20, 40, 60, 80])
    simulation = BSTSimulator(tree).find_min()

    result_states = [
        get_data(simulation, index)
        for index in range(len(simulation.states))
        if get_data(simulation, index).result_node_id is not None
    ]

    assert result_states

    result = result_states[-1]

    assert result.result_node_id is not None

    result_node = next(
        node
        for node in result.nodes
        if node.node_id == result.result_node_id
    )

    assert result_node.value == 20


def test_find_min_simulation_visits_nodes() -> None:
    tree = create_tree([50, 30, 20])
    simulation = BSTSimulator(tree).find_min()

    visits = [
        event
        for state in simulation.states
        for event in state.events
        if isinstance(event, VisitBSTNodeEvent)
    ]

    assert [event.node_id for event in visits] == [0, 1, 2]


def test_find_min_simulation_uses_operation() -> None:
    tree = create_tree([50])
    simulation = BSTSimulator(tree).find_min()

    assert isinstance(simulation.operation, FindMinOperation)


# ============================================================
# MAXIMUM
# ============================================================


def test_find_max_simulation_empty_tree() -> None:
    tree = BinarySearchTree[int]()
    simulation = BSTSimulator(tree).find_max()

    assert len(simulation.states) == 2

    event = get_events(simulation, -1)[0]

    assert isinstance(event, CompleteBSTOperationEvent)
    assert event.operation == "find_max_empty"


def test_find_max_simulation_finds_rightmost_node() -> None:
    tree = create_tree([50, 30, 70, 20, 40, 60, 80])
    simulation = BSTSimulator(tree).find_max()

    result = get_data(simulation, -2)

    assert result.result_node_id is not None

    result_node = next(
        node
        for node in result.nodes
        if node.node_id == result.result_node_id
    )

    assert result_node.value == 80


def test_find_max_simulation_visits_nodes() -> None:
    tree = create_tree([50, 70, 80])
    simulation = BSTSimulator(tree).find_max()

    visits = [
        event
        for state in simulation.states
        for event in state.events
        if isinstance(event, VisitBSTNodeEvent)
    ]

    assert [event.node_id for event in visits] == [0, 1, 2]


def test_find_max_simulation_uses_operation() -> None:
    tree = create_tree([50])
    simulation = BSTSimulator(tree).find_max()

    assert isinstance(simulation.operation, FindMaxOperation)


# ============================================================
# TRAVERSALS
# ============================================================


@pytest.mark.parametrize(
    ("method_name", "operation_type", "expected"),
    [
        (
            "in_order",
            InOrderTraversalOperation,
            [20, 30, 40, 50, 60, 70, 80],
        ),
        (
            "pre_order",
            PreOrderTraversalOperation,
            [50, 30, 20, 40, 70, 60, 80],
        ),
        (
            "post_order",
            PostOrderTraversalOperation,
            [20, 40, 30, 60, 80, 70, 50],
        ),
    ],
)
def test_traversal_simulation(
    method_name: str,
    operation_type: type,
    expected: list[int],
) -> None:
    tree = create_tree([50, 30, 70, 20, 40, 60, 80])

    simulator = BSTSimulator(tree)
    simulation_method = getattr(simulator, method_name)
    simulation = simulation_method()

    final = get_data(simulation, -1)

    assert list(final.traversal_values) == expected
    assert isinstance(simulation.operation, operation_type)


@pytest.mark.parametrize(
    "method_name",
    [
        "in_order",
        "pre_order",
        "post_order",
    ],
)
def test_traversal_simulation_visits_every_node(
    method_name: str,
) -> None:
    tree = create_tree([50, 30, 70, 20, 40, 60, 80])

    simulator = BSTSimulator(tree)
    simulation = getattr(simulator, method_name)()

    final = get_data(simulation, -1)

    assert len(final.visited_node_ids) == 7
    assert len(final.traversal_values) == 7


@pytest.mark.parametrize(
    "method_name",
    [
        "in_order",
        "pre_order",
        "post_order",
    ],
)
def test_traversal_simulation_contains_visit_events(
    method_name: str,
) -> None:
    tree = create_tree([50, 30, 70])

    simulator = BSTSimulator(tree)
    simulation = getattr(simulator, method_name)()

    visit_events = [
        event
        for state in simulation.states
        for event in state.events
        if isinstance(event, VisitBSTNodeEvent)
    ]

    assert len(visit_events) == 3


# ============================================================
# Commit behavior
# ============================================================


def test_find_min_simulation_commit() -> None:
    tree = create_tree([50, 30, 20])
    simulation = BSTSimulator(tree).find_min()

    result = simulation.commit(tree)

    assert result.value == 20


def test_find_max_simulation_commit() -> None:
    tree = create_tree([50, 70, 80])
    simulation = BSTSimulator(tree).find_max()

    result = simulation.commit(tree)

    assert result.value == 80


def test_in_order_simulation_commit() -> None:
    tree = create_tree([50, 30, 70])
    simulation = BSTSimulator(tree).in_order()

    result = simulation.commit(tree)

    assert result == [30, 50, 70]


def test_pre_order_simulation_commit() -> None:
    tree = create_tree([50, 30, 70])
    simulation = BSTSimulator(tree).pre_order()

    result = simulation.commit(tree)

    assert result == [50, 30, 70]


def test_post_order_simulation_commit() -> None:
    tree = create_tree([50, 30, 70])
    simulation = BSTSimulator(tree).post_order()

    result = simulation.commit(tree)

    assert result == [30, 70, 50]