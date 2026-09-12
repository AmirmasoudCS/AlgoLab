import pytest

from algolab.topics.queue.model import Queue


def test_new_queue_is_empty():
    queue = Queue()

    assert queue.is_empty is True
    assert queue.size == 0
    assert queue.front is None
    assert queue.rear is None
    assert queue.to_list() == []


def test_enqueue_adds_item_to_rear():
    queue = Queue()

    queue.enqueue(10)

    assert queue.is_empty is False
    assert queue.size == 1
    assert queue.front == 10
    assert queue.rear == 10
    assert queue.to_list() == [10]


def test_enqueue_preserves_fifo_order():
    queue = Queue()

    queue.enqueue(10)
    queue.enqueue(20)
    queue.enqueue(30)

    assert queue.to_list() == [10, 20, 30]
    assert queue.front == 10
    assert queue.rear == 30


def test_dequeue_removes_front_item():
    queue = Queue()

    queue.enqueue(10)
    queue.enqueue(20)
    queue.enqueue(30)

    result = queue.dequeue()

    assert result == 10
    assert queue.to_list() == [20, 30]
    assert queue.front == 20
    assert queue.rear == 30


def test_dequeue_follows_fifo_order():
    queue = Queue()

    queue.enqueue(10)
    queue.enqueue(20)
    queue.enqueue(30)

    assert queue.dequeue() == 10
    assert queue.dequeue() == 20
    assert queue.dequeue() == 30

    assert queue.is_empty is True


def test_dequeue_single_item_makes_queue_empty():
    queue = Queue()
    queue.enqueue(10)

    result = queue.dequeue()

    assert result == 10
    assert queue.is_empty is True
    assert queue.size == 0
    assert queue.front is None
    assert queue.rear is None
    assert queue.to_list() == []


def test_dequeue_empty_queue_raises_error():
    queue = Queue()

    try:
        queue.dequeue()
        assert False
    except IndexError as error:
        assert str(error) == "Cannot dequeue from an empty queue."


def test_peek_returns_front_without_removing():
    queue = Queue()

    queue.enqueue(10)
    queue.enqueue(20)

    result = queue.peek()

    assert result == 10
    assert queue.to_list() == [10, 20]
    assert queue.size == 2


def test_peek_empty_queue_raises_error():
    queue = Queue()

    with pytest.raises(IndexError) as error:
        queue.peek()

    assert str(error.value) == "Cannot peek at an empty queue."


def test_clear_removes_all_items():
    queue = Queue()

    queue.enqueue(10)
    queue.enqueue(20)
    queue.enqueue(30)

    queue.clear()

    assert queue.is_empty is True
    assert queue.size == 0
    assert queue.front is None
    assert queue.rear is None
    assert queue.to_list() == []


def test_to_list_returns_copy():
    queue = Queue()

    queue.enqueue(10)
    queue.enqueue(20)

    values = queue.to_list()
    values.append(30)

    assert queue.to_list() == [10, 20]