from algolab.topics.queue.model import Queue
from algolab.topics.queue.operations import (
    DequeueOperation,
    EnqueueOperation,
    PeekOperation,
)
from algolab.topics.queue.simulation import (
    CompleteQueueOperationEvent,
    DequeueItemEvent,
    EnqueueItemEvent,
    PeekItemEvent,
    QueueSimulationState,
    QueueSimulator,
    UpdateFrontEvent,
    UpdateRearEvent,
)


def test_enqueue_creates_expected_states():
    queue = Queue()
    queue.enqueue(10)
    queue.enqueue(20)
    queue.enqueue(30)

    simulation = QueueSimulator(queue).enqueue(40)

    assert len(simulation.states) == 5

    initial = simulation.states[0].data
    created = simulation.states[1].data
    inserted = simulation.states[2].data
    rear_updated = simulation.states[3].data
    complete = simulation.states[4].data

    assert isinstance(initial, QueueSimulationState)
    assert isinstance(created, QueueSimulationState)
    assert isinstance(inserted, QueueSimulationState)
    assert isinstance(rear_updated, QueueSimulationState)
    assert isinstance(complete, QueueSimulationState)

    assert initial.values == (10, 20, 30)
    assert initial.front_index == 0
    assert initial.rear_index == 2

    assert created.values == (10, 20, 30)
    assert created.front_index == 0
    assert created.rear_index == 2
    assert created.created_value == 40

    assert inserted.values == (10, 20, 30, 40)
    assert inserted.front_index == 0
    assert inserted.rear_index == 2
    assert inserted.created_value is None

    assert rear_updated.values == (10, 20, 30, 40)
    assert rear_updated.front_index == 0
    assert rear_updated.rear_index == 3

    assert complete.values == (10, 20, 30, 40)
    assert complete.front_index == 0
    assert complete.rear_index == 3


def test_enqueue_emits_expected_events():
    queue = Queue()
    queue.enqueue(10)
    queue.enqueue(20)

    simulation = QueueSimulator(queue).enqueue(30)

    created_events = simulation.states[1].events
    rear_events = simulation.states[3].events
    complete_events = simulation.states[4].events

    assert len(created_events) == 1
    assert isinstance(created_events[0], EnqueueItemEvent)
    assert created_events[0].value == 30

    assert len(rear_events) == 1
    assert isinstance(rear_events[0], UpdateRearEvent)
    assert rear_events[0].index == 2

    assert len(complete_events) == 1
    assert isinstance(
        complete_events[0],
        CompleteQueueOperationEvent,
    )
    assert complete_events[0].operation == "enqueue"


def test_enqueue_empty_queue_creates_expected_states():
    queue = Queue()

    simulation = QueueSimulator(queue).enqueue(10)

    assert len(simulation.states) == 5

    initial = simulation.states[0].data
    created = simulation.states[1].data
    inserted = simulation.states[2].data
    rear_updated = simulation.states[3].data
    complete = simulation.states[4].data

    assert initial.values == ()
    assert initial.front_index is None
    assert initial.rear_index is None

    assert created.values == ()
    assert created.front_index is None
    assert created.rear_index is None
    assert created.created_value == 10

    assert inserted.values == (10,)
    assert inserted.front_index == 0
    assert inserted.rear_index is None

    assert rear_updated.values == (10,)
    assert rear_updated.front_index == 0
    assert rear_updated.rear_index == 0

    assert complete.values == (10,)
    assert complete.front_index == 0
    assert complete.rear_index == 0


def test_enqueue_uses_enqueue_operation():
    queue = Queue()

    simulation = QueueSimulator(queue).enqueue(10)

    assert isinstance(simulation.operation, EnqueueOperation)


def test_dequeue_creates_expected_states():
    queue = Queue()
    queue.enqueue(10)
    queue.enqueue(20)
    queue.enqueue(30)

    simulation = QueueSimulator(queue).dequeue()

    assert len(simulation.states) == 4

    initial = simulation.states[0].data
    removed = simulation.states[1].data
    front_updated = simulation.states[2].data
    complete = simulation.states[3].data

    assert initial.values == (10, 20, 30)
    assert initial.front_index == 0
    assert initial.rear_index == 2

    assert removed.values == (20, 30)
    assert removed.front_index == 0
    assert removed.rear_index == 1
    assert removed.removed_value == 10

    assert front_updated.values == (20, 30)
    assert front_updated.front_index == 0
    assert front_updated.rear_index == 1

    assert complete.values == (20, 30)
    assert complete.front_index == 0
    assert complete.rear_index == 1


def test_dequeue_emits_expected_events():
    queue = Queue()
    queue.enqueue(10)
    queue.enqueue(20)

    simulation = QueueSimulator(queue).dequeue()

    removed_events = simulation.states[1].events
    pointer_events = simulation.states[2].events
    complete_events = simulation.states[3].events

    assert len(removed_events) == 1
    assert isinstance(removed_events[0], DequeueItemEvent)
    assert removed_events[0].value == 10

    assert len(pointer_events) == 2

    assert isinstance(pointer_events[0], UpdateFrontEvent)
    assert pointer_events[0].index == 0

    assert isinstance(pointer_events[1], UpdateRearEvent)
    assert pointer_events[1].index == 0

    assert len(complete_events) == 1
    assert isinstance(
        complete_events[0],
        CompleteQueueOperationEvent,
    )
    assert complete_events[0].operation == "dequeue"


def test_dequeue_single_item_moves_front_and_rear_to_none():
    queue = Queue()
    queue.enqueue(10)

    simulation = QueueSimulator(queue).dequeue()

    assert len(simulation.states) == 4

    initial = simulation.states[0].data
    removed = simulation.states[1].data
    updated = simulation.states[2].data
    complete = simulation.states[3].data

    assert initial.values == (10,)
    assert initial.front_index == 0
    assert initial.rear_index == 0

    assert removed.values == ()
    assert removed.front_index is None
    assert removed.rear_index is None
    assert removed.removed_value == 10

    assert updated.values == ()
    assert updated.front_index is None
    assert updated.rear_index is None

    assert complete.values == ()
    assert complete.front_index is None
    assert complete.rear_index is None


def test_dequeue_empty_queue_creates_expected_states():
    queue = Queue()

    simulation = QueueSimulator(queue).dequeue()

    assert len(simulation.states) == 2

    initial = simulation.states[0].data
    complete_state = simulation.states[1]
    complete = complete_state.data

    assert initial.values == ()
    assert initial.front_index is None
    assert initial.rear_index is None

    assert complete.values == ()
    assert complete.front_index is None
    assert complete.rear_index is None

    event = complete_state.events[0]

    assert isinstance(event, CompleteQueueOperationEvent)
    assert event.operation == "dequeue_empty"


def test_dequeue_uses_dequeue_operation():
    queue = Queue()
    queue.enqueue(10)

    simulation = QueueSimulator(queue).dequeue()

    assert isinstance(simulation.operation, DequeueOperation)


def test_peek_creates_expected_states():
    queue = Queue()
    queue.enqueue(10)
    queue.enqueue(20)
    queue.enqueue(30)

    simulation = QueueSimulator(queue).peek()

    assert len(simulation.states) == 3

    initial = simulation.states[0].data
    peeked = simulation.states[1].data
    complete = simulation.states[2].data

    assert initial.values == (10, 20, 30)
    assert initial.front_index == 0
    assert initial.rear_index == 2

    assert peeked.values == (10, 20, 30)
    assert peeked.front_index == 0
    assert peeked.rear_index == 2
    assert peeked.peeked_value == 10

    assert complete.values == (10, 20, 30)
    assert complete.front_index == 0
    assert complete.rear_index == 2


def test_peek_emits_expected_event():
    queue = Queue()
    queue.enqueue(10)
    queue.enqueue(20)

    simulation = QueueSimulator(queue).peek()

    peek_events = simulation.states[1].events
    complete_events = simulation.states[2].events

    assert len(peek_events) == 1
    assert isinstance(peek_events[0], PeekItemEvent)
    assert peek_events[0].value == 10

    assert len(complete_events) == 1
    assert isinstance(
        complete_events[0],
        CompleteQueueOperationEvent,
    )
    assert complete_events[0].operation == "peek"


def test_peek_does_not_modify_queue_state():
    queue = Queue()
    queue.enqueue(10)
    queue.enqueue(20)

    simulation = QueueSimulator(queue).peek()

    for state in simulation.states:
        data = state.data

        assert data.values == (10, 20)
        assert data.front_index == 0
        assert data.rear_index == 1


def test_peek_empty_queue_creates_expected_states():
    queue = Queue()

    simulation = QueueSimulator(queue).peek()

    assert len(simulation.states) == 2

    initial = simulation.states[0].data
    complete_state = simulation.states[1]
    complete = complete_state.data

    assert initial.values == ()
    assert initial.front_index is None
    assert initial.rear_index is None

    assert complete.values == ()
    assert complete.front_index is None
    assert complete.rear_index is None

    event = complete_state.events[0]

    assert isinstance(event, CompleteQueueOperationEvent)
    assert event.operation == "peek_empty"


def test_peek_uses_peek_operation():
    queue = Queue()
    queue.enqueue(10)

    simulation = QueueSimulator(queue).peek()

    assert isinstance(simulation.operation, PeekOperation)


def test_simulation_commit_enqueue():
    queue = Queue()
    queue.enqueue(10)

    simulation = QueueSimulator(queue).enqueue(20)

    result = simulation.commit(queue)

    assert result is None
    assert queue.to_list() == [10, 20]


def test_simulation_commit_dequeue():
    queue = Queue()
    queue.enqueue(10)
    queue.enqueue(20)

    simulation = QueueSimulator(queue).dequeue()

    result = simulation.commit(queue)

    assert result == 10
    assert queue.to_list() == [20]


def test_simulation_commit_peek():
    queue = Queue()
    queue.enqueue(10)
    queue.enqueue(20)

    simulation = QueueSimulator(queue).peek()

    result = simulation.commit(queue)

    assert result == 10
    assert queue.to_list() == [10, 20]