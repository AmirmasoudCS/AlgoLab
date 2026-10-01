import math

import pytest

from algolab.core.serialization import (
    check_dict,
    check_int,
    check_number,
    check_scalar,
    checked_int_items,
    checked_list,
    checked_scalar_items,
)


@pytest.mark.parametrize("value", [1, 2.5, "text", True, None])
def test_check_scalar_accepts_json_scalars(value):
    check_scalar(value, "x")


@pytest.mark.parametrize(
    "value", [[1], {"a": 1}, (1, 2), object(), math.nan, math.inf, -math.inf]
)
def test_check_scalar_rejects_everything_else(value):
    with pytest.raises(ValueError):
        check_scalar(value, "x")


def test_check_int_rejects_bools_floats_and_text():
    assert check_int(5, "x") == 5

    for bad in (True, False, 1.0, "1", None):
        with pytest.raises(ValueError):
            check_int(bad, "x")


def test_check_number_accepts_ints_and_floats_only():
    assert check_number(3, "x") == 3
    assert check_number(2.5, "x") == 2.5

    for bad in (True, "1", None, math.nan, math.inf):
        with pytest.raises(ValueError):
            check_number(bad, "x")


def test_check_dict():
    assert check_dict({"a": 1}, "Thing") == {"a": 1}

    with pytest.raises(ValueError, match="Thing data must be an object"):
        check_dict([1], "Thing")


def test_checked_list_validates_shape_and_size():
    assert checked_list({"items": [1, 2]}, "Stack", 5) == [1, 2]

    with pytest.raises(ValueError, match="'items' list"):
        checked_list({}, "Stack", 5)

    with pytest.raises(ValueError, match="must be a list"):
        checked_list({"items": "abc"}, "Stack", 5)

    with pytest.raises(ValueError, match="at most 2"):
        checked_list({"items": [1, 2, 3]}, "Stack", 2)

    assert checked_list({"slots": [1]}, "Ring", 5, key="slots") == [1]


def test_checked_scalar_items_returns_a_copy_and_checks_each_item():
    source = {"items": [1, "a", None]}
    result = checked_scalar_items(source, "Stack", 10)

    assert result == [1, "a", None] and result is not source["items"]

    with pytest.raises(ValueError, match="Item 1"):
        checked_scalar_items({"items": [1, [2]]}, "Stack", 10)


def test_checked_int_items_requires_whole_numbers():
    assert checked_int_items({"values": [1, 2]}, "Heap", 10) == [1, 2]

    for bad in ([1.5], [True], ["1"], [None]):
        with pytest.raises(ValueError):
            checked_int_items({"values": bad}, "Heap", 10)