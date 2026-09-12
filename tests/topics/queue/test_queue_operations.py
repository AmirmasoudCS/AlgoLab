import pytest

from algolab.topics.queue.model import Queue
from algolab.topics.queue.operations import (
    DequeueOperation,
    EnqueueOperation,
    PeekOperation,
)


def test_enqueue_operation_adds_value():
    queue = Queue()
    operation = EnqueueOperation(10)

    result = operation.commit(queue)

    assert result is None
    assert queue.to_list() == [10]


def test_enqueue_operation_adds_value_to_rear():
    queue = Queue()
    queue.enqueue(10)

    operation = EnqueueOperation(20)

    operation.commit(queue)

    assert queue.to_list() == [10, 20]
    assert queue.front == 10
    assert queue.rear == 20


def test_dequeue_operation_removes_front_value():
    queue = Queue()
    queue.enqueue(10)
    queue.enqueue(20)

    operation = DequeueOperation()

    result = operation.commit(queue)

    assert result == 10
    assert queue.to_list() == [20]


def test_dequeue_operation_on_empty_queue_raises_error():
    queue = Queue()
    operation = DequeueOperation()

    with pytest.raises(
        IndexError,
        match="Cannot dequeue from an empty queue.",
    ):
        operation.commit(queue)


def test_peek_operation_returns_front_value():
    queue = Queue()
    queue.enqueue(10)
    queue.enqueue(20)

    operation = PeekOperation()

    result = operation.commit(queue)

    assert result == 10
    assert queue.to_list() == [10, 20]


def test_peek_operation_does_not_modify_queue():
    queue = Queue()
    queue.enqueue(10)
    queue.enqueue(20)

    operation = PeekOperation()

    operation.commit(queue)

    assert queue.size == 2
    assert queue.front == 10
    assert queue.rear == 20
    assert queue.to_list() == [10, 20]


def test_peek_operation_on_empty_queue_raises_error():
    queue = Queue()
    operation = PeekOperation()

    with pytest.raises(IndexError) as error:
        operation.commit(queue)

    assert str(error.value) == "Cannot peek at an empty queue."