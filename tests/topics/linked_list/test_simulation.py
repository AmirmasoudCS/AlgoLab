from algolab.topics.linked_list.model import LinkedListModel
from algolab.topics.linked_list.operations import (
    DeleteAtOperation,
    InsertAtBeginningOperation,
    InsertAtEndOperation,
    InsertAtOperation,
    SearchOperation,
)
from algolab.topics.linked_list.simulation import (
    CompleteOperationEvent,
    CreateNodeEvent,
    DeleteNodeEvent,
    LinkedListSimulation,
    LinkedListSimulationState,
    LinkedListSimulator,
    UpdateHeadEvent,
    UpdateLinkEvent,
    VisitNodeEvent,
)


def create_model(values: list[object]) -> LinkedListModel:
    """Create a linked list containing the given values."""

    model = LinkedListModel()

    for value in values:
        model.insert_at_end(value)

    return model


def test_insert_at_beginning_simulation():
    model = create_model([10, 20])
    simulator = LinkedListSimulator(model)

    simulation = simulator.insert_at_beginning(5)

    assert isinstance(simulation, LinkedListSimulation)
    assert isinstance(
        simulation.operation,
        InsertAtBeginningOperation,
    )

    assert len(simulation.states) == 4

    assert simulation.states[0].data.values == (10, 20)
    assert simulation.states[0].events == []

    assert simulation.states[1].data.values == (10, 20)
    assert isinstance(
        simulation.states[1].events[0],
        CreateNodeEvent,
    )
    assert simulation.states[1].events[0].index == 0
    assert simulation.states[1].events[0].data == 5

    assert simulation.states[2].data.values == (5, 10, 20)
    assert isinstance(
        simulation.states[2].events[0],
        UpdateHeadEvent,
    )
    assert simulation.states[2].events[0].index == 0

    assert isinstance(
        simulation.states[3].events[0],
        CompleteOperationEvent,
    )
    assert simulation.states[3].events[0].operation == (
        "insert_at_beginning"
    )


def test_insert_at_beginning_empty_list():
    model = LinkedListModel()
    simulator = LinkedListSimulator(model)

    simulation = simulator.insert_at_beginning(10)

    assert len(simulation.states) == 4
    assert simulation.states[0].data.values == ()
    assert simulation.states[2].data.values == (10,)

    assert isinstance(
        simulation.states[2].events[0],
        UpdateHeadEvent,
    )


def test_insert_at_end_simulation():
    model = create_model([10, 20])
    simulator = LinkedListSimulator(model)

    simulation = simulator.insert_at_end(30)

    assert isinstance(
        simulation.operation,
        InsertAtEndOperation,
    )

    assert len(simulation.states) == 6

    assert simulation.states[0].data.values == (10, 20)

    assert isinstance(
        simulation.states[1].events[0],
        VisitNodeEvent,
    )
    assert simulation.states[1].events[0].index == 0

    assert isinstance(
        simulation.states[2].events[0],
        VisitNodeEvent,
    )
    assert simulation.states[2].events[0].index == 1

    assert isinstance(
        simulation.states[3].events[0],
        CreateNodeEvent,
    )
    assert simulation.states[3].events[0].index == 2
    assert simulation.states[3].events[0].data == 30

    assert simulation.states[4].data.values == (10, 20, 30)

    assert isinstance(
        simulation.states[4].events[0],
        UpdateLinkEvent,
    )
    assert simulation.states[4].events[0].index == 1
    assert simulation.states[4].events[0].next_index == 2

    assert isinstance(
        simulation.states[5].events[0],
        CompleteOperationEvent,
    )
    assert simulation.states[5].events[0].operation == (
        "insert_at_end"
    )


def test_insert_at_end_empty_list():
    model = LinkedListModel()
    simulator = LinkedListSimulator(model)

    simulation = simulator.insert_at_end(10)

    assert len(simulation.states) == 4
    assert simulation.states[0].data.values == ()
    assert simulation.states[2].data.values == (10,)

    assert isinstance(
        simulation.states[1].events[0],
        CreateNodeEvent,
    )

    assert isinstance(
        simulation.states[2].events[0],
        UpdateHeadEvent,
    )


def test_insert_at_middle_simulation():
    model = create_model([10, 30, 40])
    simulator = LinkedListSimulator(model)

    simulation = simulator.insert_at(
        index=1,
        data=20,
    )

    assert isinstance(
        simulation.operation,
        InsertAtOperation,
    )

    assert len(simulation.states) == 5

    assert simulation.states[0].data.values == (
        10,
        30,
        40,
    )

    assert isinstance(
        simulation.states[1].events[0],
        VisitNodeEvent,
    )
    assert simulation.states[1].events[0].index == 0

    assert isinstance(
        simulation.states[2].events[0],
        CreateNodeEvent,
    )
    assert simulation.states[2].events[0].index == 1
    assert simulation.states[2].events[0].data == 20

    assert simulation.states[3].data.values == (
        10,
        20,
        30,
        40,
    )

    assert isinstance(
        simulation.states[3].events[0],
        UpdateLinkEvent,
    )
    assert simulation.states[3].events[0].index == 0
    assert simulation.states[3].events[0].next_index == 1


def test_insert_at_zero_uses_beginning_simulation():
    model = create_model([10, 20])
    simulator = LinkedListSimulator(model)

    simulation = simulator.insert_at(
        index=0,
        data=5,
    )

    assert isinstance(
        simulation.operation,
        InsertAtBeginningOperation,
    )


def test_insert_at_end_index_uses_end_simulation():
    model = create_model([10, 20])
    simulator = LinkedListSimulator(model)

    simulation = simulator.insert_at(
        index=2,
        data=30,
    )

    assert isinstance(
        simulation.operation,
        InsertAtEndOperation,
    )


def test_insert_at_invalid_index():
    model = create_model([10, 20])
    simulator = LinkedListSimulator(model)

    try:
        simulator.insert_at(
            index=3,
            data=30,
        )
        assert False
    except IndexError:
        pass


def test_delete_at_beginning_simulation():
    model = create_model([10, 20, 30])
    simulator = LinkedListSimulator(model)

    simulation = simulator.delete_at(0)

    assert isinstance(
        simulation.operation,
        DeleteAtOperation,
    )

    assert len(simulation.states) == 5

    assert simulation.states[0].data.values == (
        10,
        20,
        30,
    )

    assert isinstance(
        simulation.states[1].events[0],
        VisitNodeEvent,
    )
    assert simulation.states[1].events[0].index == 0

    assert isinstance(
        simulation.states[2].events[0],
        DeleteNodeEvent,
    )
    assert simulation.states[2].events[0].index == 0
    assert simulation.states[2].events[0].data == 10

    assert simulation.states[3].data.values == (
        20,
        30,
    )

    assert isinstance(
        simulation.states[3].events[0],
        UpdateHeadEvent,
    )
    assert simulation.states[3].events[0].index == 0

    assert isinstance(
        simulation.states[4].events[0],
        CompleteOperationEvent,
    )
    assert simulation.states[4].events[0].operation == (
        "delete_at"
    )


def test_delete_at_middle_simulation():
    model = create_model([10, 20, 30])
    simulator = LinkedListSimulator(model)

    simulation = simulator.delete_at(1)

    assert len(simulation.states) == 6

    assert simulation.states[0].data.values == (
        10,
        20,
        30,
    )

    assert simulation.states[1].data.current_index == 0
    assert simulation.states[2].data.current_index == 1

    assert isinstance(
        simulation.states[3].events[0],
        DeleteNodeEvent,
    )
    assert simulation.states[3].events[0].index == 1
    assert simulation.states[3].events[0].data == 20

    assert simulation.states[4].data.values == (
        10,
        30,
    )

    assert isinstance(
        simulation.states[4].events[0],
        UpdateLinkEvent,
    )
    assert simulation.states[4].events[0].index == 0
    assert simulation.states[4].events[0].next_index == 1

    assert isinstance(
        simulation.states[5].events[0],
        CompleteOperationEvent,
    )
    assert simulation.states[5].events[0].operation == (
        "delete_at"
    )


def test_delete_at_end_simulation():
    model = create_model([10, 20, 30])
    simulator = LinkedListSimulator(model)

    simulation = simulator.delete_at(2)

    assert simulation.states[-2].data.values == (
        10,
        20,
    )

    assert isinstance(
        simulation.states[-2].events[0],
        UpdateLinkEvent,
    )

    assert simulation.states[-2].events[0].index == 1
    assert simulation.states[-2].events[0].next_index is None


def test_delete_only_node_simulation():
    model = create_model([10])
    simulator = LinkedListSimulator(model)

    simulation = simulator.delete_at(0)

    assert simulation.states[-2].data.values == ()

    assert isinstance(
        simulation.states[-2].events[0],
        UpdateHeadEvent,
    )
    assert simulation.states[-2].events[0].index is None


def test_delete_at_invalid_index():
    model = create_model([10, 20])
    simulator = LinkedListSimulator(model)

    try:
        simulator.delete_at(2)
        assert False
    except IndexError:
        pass


def test_search_found_simulation():
    model = create_model([10, 20, 30])
    simulator = LinkedListSimulator(model)

    simulation = simulator.search(20)

    assert isinstance(
        simulation.operation,
        SearchOperation,
    )

    assert simulation.states[0].data.values == (
        10,
        20,
        30,
    )

    assert simulation.states[1].data.current_index == 0
    assert simulation.states[2].data.current_index == 1

    assert isinstance(
        simulation.states[3].events[0],
        CompleteOperationEvent,
    )
    assert simulation.states[3].events[0].operation == (
        "search_found"
    )

    assert simulation.states[3].data.current_index == 1


def test_search_not_found_simulation():
    model = create_model([10, 20, 30])
    simulator = LinkedListSimulator(model)

    simulation = simulator.search(50)

    assert isinstance(
        simulation.operation,
        SearchOperation,
    )

    assert simulation.states[-1].data.current_index is None

    assert isinstance(
        simulation.states[-1].events[0],
        CompleteOperationEvent,
    )
    assert simulation.states[-1].events[0].operation == (
        "search_not_found"
    )


def test_search_empty_list():
    model = LinkedListModel()
    simulator = LinkedListSimulator(model)

    simulation = simulator.search(10)

    assert len(simulation.states) == 2
    assert simulation.states[0].data.values == ()
    assert simulation.states[1].data.values == ()

    assert isinstance(
        simulation.states[1].events[0],
        CompleteOperationEvent,
    )

    assert simulation.states[1].events[0].operation == (
        "search_not_found"
    )


def test_simulation_does_not_modify_model():
    model = create_model([10, 20, 30])
    simulator = LinkedListSimulator(model)

    simulator.insert_at_beginning(5)
    simulator.insert_at_end(40)
    simulator.insert_at(1, 15)
    simulator.delete_at(1)

    assert model.to_list() == [10, 20, 30]


def test_commit_applies_simulated_operation():
    model = create_model([10, 20, 30])
    simulator = LinkedListSimulator(model)

    simulation = simulator.insert_at(
        index=1,
        data=15,
    )

    simulation.commit(model)

    assert model.to_list() == [10, 15, 20, 30]


def test_simulation_states_are_linked_list_simulation_states():
    model = create_model([10, 20])
    simulator = LinkedListSimulator(model)

    simulation = simulator.insert_at_end(30)

    for state in simulation.states:
        assert isinstance(
            state.data,
            LinkedListSimulationState,
        )