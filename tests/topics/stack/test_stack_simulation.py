
from algolab.topics.stack.model import Stack
from algolab.topics.stack.simulation import (
    CompleteStackOperationEvent,
    PeekItemEvent,
    PopItemEvent,
    PushItemEvent,
    StackSimulation,
    StackSimulationState,
    StackSimulator,
    UpdateTopEvent,
)


def test_push_creates_expected_states():
    stack = Stack()
    stack.push(1)
    stack.push(2)
    stack.push(3)

    simulation = StackSimulator(stack).push(4)

    assert len(simulation.states) == 4

    initial = simulation.states[0].data
    created = simulation.states[1].data
    pushed = simulation.states[2].data
    complete = simulation.states[3].data

    assert isinstance(initial, StackSimulationState)
    assert isinstance(created, StackSimulationState)
    assert isinstance(pushed, StackSimulationState)
    assert isinstance(complete, StackSimulationState)

    assert initial.values == (1, 2, 3)
    assert initial.top_index == 2

    assert created.values == (1, 2, 3)
    assert created.top_index == 2
    assert created.created_value == 4

    assert pushed.values == (1, 2, 3, 4)
    assert pushed.top_index == 3

    assert complete.values == (1, 2, 3, 4)
    assert complete.top_index == 3


def test_push_does_not_modify_original_model():
    stack = Stack()
    stack.push(1)
    stack.push(2)

    simulation = StackSimulator(stack).push(3)

    assert stack.to_list() == [1, 2]
    assert simulation.operation is not None


def test_push_events_are_correct():
    stack = Stack()

    simulation = StackSimulator(stack).push(10)

    assert isinstance(
        simulation.states[1].events[0],
        PushItemEvent,
    )

    assert simulation.states[1].events[0].value == 10

    assert isinstance(
        simulation.states[2].events[0],
        UpdateTopEvent,
    )

    assert simulation.states[2].events[0].index == 0

    assert isinstance(
        simulation.states[3].events[0],
        CompleteStackOperationEvent,
    )

    assert simulation.states[3].events[0].operation == "push"


def test_push_on_empty_stack_sets_top_to_zero():
    stack = Stack()

    simulation = StackSimulator(stack).push(10)

    initial = simulation.states[0].data
    created = simulation.states[1].data
    pushed = simulation.states[2].data

    assert initial.top_index is None

    assert created.values == ()
    assert created.top_index is None
    assert created.created_value == 10

    assert pushed.values == (10,)
    assert pushed.top_index == 0


def test_pop_creates_expected_states():
    stack = Stack()
    stack.push(1)
    stack.push(2)
    stack.push(3)

    simulation = StackSimulator(stack).pop()

    assert len(simulation.states) == 4

    initial = simulation.states[0].data
    removed = simulation.states[1].data
    popped = simulation.states[2].data
    complete = simulation.states[3].data

    assert initial.values == (1, 2, 3)
    assert initial.top_index == 2

    assert removed.values == (1, 2, 3)
    assert removed.top_index == 2
    assert removed.removed_value == 3

    assert popped.values == (1, 2)
    assert popped.top_index == 1

    assert complete.values == (1, 2)
    assert complete.top_index == 1


def test_pop_single_item_moves_top_to_none():
    stack = Stack()
    stack.push(10)

    simulation = StackSimulator(stack).pop()

    assert simulation.states[0].data.top_index == 0
    assert simulation.states[1].data.top_index == 0

    assert simulation.states[2].data.values == ()
    assert simulation.states[2].data.top_index is None

    assert simulation.states[3].data.top_index is None


def test_pop_empty_stack_creates_empty_operation_state():
    stack = Stack()

    simulation = StackSimulator(stack).pop()

    assert len(simulation.states) == 2

    initial = simulation.states[0].data
    complete = simulation.states[1].data

    assert initial.values == ()
    assert initial.top_index is None

    assert complete.values == ()
    assert complete.top_index is None
    assert complete.description == (
        "The stack is empty. Nothing can be popped."
    )

    event = simulation.states[1].events[0]

    assert isinstance(event, CompleteStackOperationEvent)
    assert event.operation == "pop_empty"


def test_pop_events_are_correct():
    stack = Stack()
    stack.push(10)
    stack.push(20)

    simulation = StackSimulator(stack).pop()

    assert isinstance(
        simulation.states[1].events[0],
        PopItemEvent,
    )

    assert simulation.states[1].events[0].value == 20

    assert isinstance(
        simulation.states[2].events[0],
        UpdateTopEvent,
    )

    assert simulation.states[2].events[0].index == 0


def test_peek_creates_expected_states():
    stack = Stack()
    stack.push(10)
    stack.push(20)

    simulation = StackSimulator(stack).peek()

    assert len(simulation.states) == 3

    initial = simulation.states[0].data
    peeked = simulation.states[1].data
    complete = simulation.states[2].data

    assert initial.values == (10, 20)
    assert initial.top_index == 1

    assert peeked.values == (10, 20)
    assert peeked.top_index == 1
    assert peeked.peeked_value == 20

    assert complete.values == (10, 20)
    assert complete.top_index == 1


def test_peek_does_not_modify_stack():
    stack = Stack()
    stack.push(10)
    stack.push(20)

    simulation = StackSimulator(stack).peek()

    assert stack.to_list() == [10, 20]
    assert simulation.states[1].data.values == (10, 20)


def test_peek_event_is_correct():
    stack = Stack()
    stack.push(10)

    simulation = StackSimulator(stack).peek()

    event = simulation.states[1].events[0]

    assert isinstance(event, PeekItemEvent)
    assert event.value == 10


def test_peek_empty_stack():
    stack = Stack()

    simulation = StackSimulator(stack).peek()

    assert len(simulation.states) == 2

    assert simulation.states[0].data.top_index is None
    assert simulation.states[1].data.top_index is None

    event = simulation.states[1].events[0]

    assert isinstance(event, CompleteStackOperationEvent)
    assert event.operation == "peek_empty"


def test_stack_simulation_commit_push():
    stack = Stack()

    simulation = StackSimulator(stack).push(10)

    result = simulation.commit(stack)

    assert result is None
    assert stack.to_list() == [10]


def test_stack_simulation_commit_pop():
    stack = Stack()
    stack.push(10)
    stack.push(20)

    simulation = StackSimulator(stack).pop()

    result = simulation.commit(stack)

    assert result == 20
    assert stack.to_list() == [10]


def test_stack_simulation_commit_peek():
    stack = Stack()
    stack.push(10)
    stack.push(20)

    simulation = StackSimulator(stack).peek()

    result = simulation.commit(stack)

    assert result == 20
    assert stack.to_list() == [10, 20]