import pytest

from algolab.topics.stack.model import Stack


def test_to_dict_lists_items_bottom_to_top():
    stack = Stack()
    stack.push(1)
    stack.push(2)
    stack.push(3)

    assert stack.to_dict() == {"items": [1, 2, 3]}


def test_empty_stack_round_trips():
    restored = Stack.from_dict(Stack().to_dict())

    assert restored.is_empty
    assert restored.to_list() == []


def test_round_trip_preserves_order_and_behaviour():
    stack = Stack()

    for value in (10, 20, 30):
        stack.push(value)

    restored = Stack.from_dict(stack.to_dict())

    assert restored.to_list() == [10, 20, 30]
    assert restored.top == 30
    assert restored.pop() == 30


def test_round_trip_through_json_text():
    import json

    stack = Stack()
    for value in (1, "two", 3.5, None, True):
        stack.push(value)

    restored = Stack.from_dict(json.loads(json.dumps(stack.to_dict())))

    assert restored.to_list() == [1, "two", 3.5, None, True]


def test_from_dict_copies_the_list():
    source = {"items": [1, 2]}
    restored = Stack.from_dict(source)

    restored.push(3)

    assert source["items"] == [1, 2]


@pytest.mark.parametrize(
    "bad",
    [
        None,
        [],
        "items",
        {},
        {"items": "abc"},
        {"items": {"a": 1}},
        {"items": [1, [2]]},
        {"items": [1, {"x": 2}]},
        {"items": [float("nan")]},
        {"items": [float("inf")]},
    ],
)
def test_from_dict_rejects_malformed_data(bad):
    with pytest.raises(ValueError):
        Stack.from_dict(bad)


def test_from_dict_rejects_oversized_stacks():
    too_many = {"items": list(range(Stack.MAX_LOADED_ITEMS + 1))}

    with pytest.raises(ValueError, match="at most"):
        Stack.from_dict(too_many)

    assert Stack.from_dict({"items": list(range(Stack.MAX_LOADED_ITEMS))}).size == Stack.MAX_LOADED_ITEMS