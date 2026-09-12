import pytest

from algolab.topics.stack.model import Stack
from algolab.topics.stack.operations import (
    PeekOperation,
    PopOperation,
    PushOperation,
)


def test_push_operation_commits_value():
    stack = Stack()
    operation = PushOperation(10)

    result = operation.commit(stack)

    assert result is None
    assert stack.to_list() == [10]


def test_push_operation_does_not_modify_stack_until_commit():
    stack = Stack()
    operation = PushOperation(10)

    assert stack.is_empty is True

    operation.commit(stack)

    assert stack.to_list() == [10]


def test_multiple_push_operations():
    stack = Stack()

    PushOperation(10).commit(stack)
    PushOperation(20).commit(stack)
    PushOperation(30).commit(stack)

    assert stack.to_list() == [10, 20, 30]
    assert stack.top == 30


def test_pop_operation_commits_removal():
    stack = Stack()
    stack.push(10)
    stack.push(20)
    stack.push(30)

    operation = PopOperation()

    result = operation.commit(stack)

    assert result == 30
    assert stack.to_list() == [10, 20]


def test_pop_operation_follows_lifo_order():
    stack = Stack()
    stack.push(10)
    stack.push(20)
    stack.push(30)

    operation = PopOperation()

    assert operation.commit(stack) == 30
    assert operation.commit(stack) == 20
    assert operation.commit(stack) == 10
    assert stack.is_empty is True


def test_pop_operation_on_empty_stack_raises():
    stack = Stack()
    operation = PopOperation()

    with pytest.raises(IndexError, match="Cannot pop from an empty stack"):
        operation.commit(stack)


def test_peek_operation_returns_top():
    stack = Stack()
    stack.push(10)
    stack.push(20)

    operation = PeekOperation()

    result = operation.commit(stack)

    assert result == 20
    assert stack.to_list() == [10, 20]


def test_peek_operation_does_not_modify_stack():
    stack = Stack()
    stack.push(10)
    stack.push(20)

    operation = PeekOperation()
    operation.commit(stack)

    assert stack.size == 2
    assert stack.top == 20
    assert stack.to_list() == [10, 20]


def test_peek_operation_on_empty_stack_raises():
    stack = Stack()
    operation = PeekOperation()

    with pytest.raises(IndexError, match="Cannot peek at an empty stack"):
        operation.commit(stack)