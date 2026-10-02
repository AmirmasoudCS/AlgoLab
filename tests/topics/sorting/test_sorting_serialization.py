import pytest

from algolab.topics.sorting.model import SortArray


def test_round_trip_preserves_order_including_duplicates():
    array = SortArray([5, 3, 3, 9, 0, 1])
    restored = SortArray.from_dict(array.to_dict())

    assert restored.values == [5, 3, 3, 9, 0, 1]
    assert restored.size == 6 and not restored.is_sorted


def test_empty_and_sorted_arrays_round_trip():
    assert SortArray.from_dict(SortArray().to_dict()).is_empty
    assert SortArray.from_dict(SortArray([1, 2, 3]).to_dict()).is_sorted


def test_randomized_arrays_round_trip():
    array = SortArray()
    array.randomize(size=40, minimum=0, maximum=99)

    assert SortArray.from_dict(array.to_dict()).values == array.values


def test_maximum_size_is_accepted_and_one_more_is_not():
    full = {"values": list(range(SortArray.MAX_LOADED_VALUES))}

    assert SortArray.from_dict(full).size == SortArray.MAX_LOADED_VALUES

    with pytest.raises(ValueError, match="at most"):
        SortArray.from_dict({"values": list(range(SortArray.MAX_LOADED_VALUES + 1))})


@pytest.mark.parametrize("bad", [
    None, [], "values", {},
    {"values": "abc"}, {"values": [1.5]}, {"values": [True]}, {"values": ["1"]},
    {"values": [None]}, {"values": [[1]]},
    {"values": [-1]}, {"values": [1, 2, -3]},
    {"values": [SortArray.MAX_LOADED_VALUE + 1]},
])
def test_from_dict_rejects_malformed_data(bad):
    with pytest.raises(ValueError):
        SortArray.from_dict(bad)


def test_the_boundary_values_are_valid():
    assert SortArray.from_dict({"values": [0, SortArray.MAX_LOADED_VALUE]}).size == 2


def test_to_dict_returns_a_copy():
    array = SortArray([1, 2])
    data = array.to_dict()
    data["values"].append(3)

    assert array.values == [1, 2]