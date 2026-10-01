import pytest

from algolab.topics.queue.model import Queue


def test_round_trip_preserves_front_to_rear_order():
    queue = Queue()

    for value in (10, 20, 30):
        queue.enqueue(value)

    restored = Queue.from_dict(queue.to_dict())

    assert restored.to_list() == [10, 20, 30]
    assert restored.front == 10 and restored.rear == 30
    assert restored.dequeue() == 10


def test_empty_queue_round_trips():
    assert Queue.from_dict(Queue().to_dict()).is_empty


def test_mixed_scalars_round_trip():
    queue = Queue()

    for value in (1, "two", 3.5, None):
        queue.enqueue(value)

    assert Queue.from_dict(queue.to_dict()).to_list() == [1, "two", 3.5, None]


@pytest.mark.parametrize(
    "bad",
    [None, [], {}, {"items": "abc"}, {"items": [[1]]}, {"items": [float("nan")]}],
)
def test_from_dict_rejects_malformed_data(bad):
    with pytest.raises(ValueError):
        Queue.from_dict(bad)


def test_from_dict_rejects_oversized_queues():
    with pytest.raises(ValueError, match="at most"):
        Queue.from_dict({"items": list(range(Queue.MAX_LOADED_ITEMS + 1))})


def test_replace_with_takes_over_the_other_queue():
    target = Queue()
    target.enqueue(1)
    source = Queue.from_dict({"items": [7, 8]})

    target.replace_with(source)

    assert target.to_list() == [7, 8]