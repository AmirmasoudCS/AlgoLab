import random

import pytest

from algolab.topics.circular_queue.model import CircularQueue


def _wrapped_queue():
    """A queue whose FRONT has moved and whose contents wrap around."""
    queue = CircularQueue(capacity=5)

    for value in (1, 2, 3, 4, 5):
        queue.enqueue(value)

    queue.dequeue()
    queue.dequeue()
    queue.dequeue()
    queue.enqueue(6)
    queue.enqueue(7)

    return queue


def test_to_dict_saves_the_physical_ring():
    data = _wrapped_queue().to_dict()

    assert data == {
        "capacity": 5, "front": 3, "size": 4,
        "slots": [6, 7, None, 4, 5],
    }


def test_round_trip_preserves_the_exact_ring_including_wraparound():
    original = _wrapped_queue()
    restored = CircularQueue.from_dict(original.to_dict())

    assert restored.slots_snapshot() == original.slots_snapshot()
    assert restored.front_index == original.front_index == 3
    assert restored.rear_index == original.rear_index == 1
    assert restored.to_list() == original.to_list() == [4, 5, 6, 7]
    assert restored.size == 4 and restored.capacity == 5


def test_a_loaded_queue_keeps_behaving_correctly():
    restored = CircularQueue.from_dict(_wrapped_queue().to_dict())

    assert restored.enqueue(8) == 2          # lands in the one free slot
    assert restored.is_full
    assert restored.dequeue() == 4 and restored.front_index == 4


def test_empty_queue_with_a_moved_front_round_trips():
    queue = CircularQueue(capacity=4)
    queue.enqueue(1)
    queue.dequeue()

    restored = CircularQueue.from_dict(queue.to_dict())

    assert restored.is_empty and restored.to_dict() == queue.to_dict()


def test_random_operations_always_round_trip():
    rng = random.Random(11)

    for _ in range(200):
        queue = CircularQueue(capacity=rng.randint(1, 12))

        for _ in range(rng.randint(0, 60)):
            if rng.random() < 0.55 and not queue.is_full:
                queue.enqueue(rng.randint(1, 99))
            elif not queue.is_empty:
                queue.dequeue()

        restored = CircularQueue.from_dict(queue.to_dict())

        assert restored.to_dict() == queue.to_dict()
        assert restored.to_list() == queue.to_list()


GOOD = {"capacity": 4, "front": 1, "size": 2, "slots": [None, 5, 6, None]}


def test_the_good_fixture_is_valid():
    assert CircularQueue.from_dict(GOOD).to_list() == [5, 6]


@pytest.mark.parametrize(
    "change",
    [
        {"capacity": 0},
        {"capacity": 65},
        {"capacity": "4"},
        {"capacity": True},
        {"front": 4},
        {"front": -1},
        {"front": 1.0},
        {"size": 5},
        {"size": -1},
        {"slots": [None, 5, 6]},                 # wrong length
        {"slots": [None, 5, 6, None, None]},     # wrong length
        {"slots": [None, None, 6, None]},        # an occupied slot is empty
        {"slots": [9, 5, 6, None]},              # an empty slot holds a value
        {"slots": [None, 5, [6], None]},         # not a scalar
        {"slots": "abcd"},
    ],
)
def test_from_dict_rejects_inconsistent_data(change):
    with pytest.raises(ValueError):
        CircularQueue.from_dict({**GOOD, **change})


@pytest.mark.parametrize("missing", ["capacity", "front", "size", "slots"])
def test_from_dict_rejects_missing_fields(missing):
    data = dict(GOOD)
    del data[missing]

    with pytest.raises(ValueError):
        CircularQueue.from_dict(data)


def test_from_dict_rejects_non_objects():
    for bad in (None, [], "ring"):
        with pytest.raises(ValueError):
            CircularQueue.from_dict(bad)


def test_replace_with_takes_over_capacity_and_ring():
    target = CircularQueue(capacity=3)
    target.replace_with(CircularQueue.from_dict(GOOD))

    assert target.capacity == 4 and target.front_index == 1
    assert target.to_list() == [5, 6]