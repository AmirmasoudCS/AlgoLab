import pytest

from algolab.topics.stack.model import Stack


def test_new_stack_is_empty():
    stack = Stack()

    assert stack.is_empty is True
    assert stack.size == 0
    assert stack.top is None
    assert stack.to_list() == []


def test_push_adds_item_to_top():
    stack = Stack()

    stack.push(10)
    stack.push(20)
    stack.push(30)

    assert stack.to_list() == [10, 20, 30]
    assert stack.size == 3
    assert stack.top == 30


def test_pop_removes_and_returns_top_item():
    stack = Stack()

    stack.push(10)
    stack.push(20)
    stack.push(30)

    result = stack.pop()

    assert result == 30
    assert stack.to_list() == [10, 20]
    assert stack.size == 2
    assert stack.top == 20


def test_stack_follows_lifo_order():
    stack = Stack()

    stack.push(1)
    stack.push(2)
    stack.push(3)

    assert stack.pop() == 3
    assert stack.pop() == 2
    assert stack.pop() == 1
    assert stack.is_empty is True


def test_peek_returns_top_without_removing_it():
    stack = Stack()

    stack.push(10)
    stack.push(20)

    result = stack.peek()

    assert result == 20
    assert stack.to_list() == [10, 20]
    assert stack.size == 2
    assert stack.top == 20


def test_pop_empty_stack_raises():
    stack = Stack()

    with pytest.raises(IndexError, match="Cannot pop from an empty stack"):
        stack.pop()


def test_peek_empty_stack_raises():
    stack = Stack()

    with pytest.raises(IndexError, match="Cannot peek at an empty stack"):
        stack.peek()


def test_clear_removes_all_items():
    stack = Stack()

    stack.push(10)
    stack.push(20)
    stack.push(30)

    stack.clear()

    assert stack.is_empty is True
    assert stack.size == 0
    assert stack.top is None
    assert stack.to_list() == []


def test_to_list_returns_copy():
    stack = Stack()

    stack.push(10)
    stack.push(20)

    values = stack.to_list()
    values.append(30)

    assert stack.to_list() == [10, 20]
    assert stack.size == 2


def test_stack_accepts_different_value_types():
    stack = Stack()

    stack.push(10)
    stack.push("hello")
    stack.push(3.14)
    stack.push(None)

    assert stack.to_list() == [10, "hello", 3.14, None]
    assert stack.top is None
    assert stack.size == 4