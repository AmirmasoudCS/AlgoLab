import random

import pytest

from algolab.topics.heap.model import Heap, HeapType


@pytest.mark.parametrize("heap_type", list(HeapType))
def test_round_trip_preserves_type_and_exact_array(heap_type):
    rng = random.Random(2)

    for _ in range(100):
        heap = Heap[int](heap_type)

        for _ in range(rng.randint(0, 30)):
            heap.insert(rng.randint(1, 99))

        restored = Heap.from_dict(heap.to_dict())

        assert restored.heap_type is heap_type
        assert restored.values == heap.values


def test_to_dict_does_not_reorder_the_array():
    heap = Heap[int](HeapType.MIN)
    heap.build_heap([9, 4, 7, 1, 8, 3])

    assert heap.to_dict() == {"heap_type": "min", "values": heap.values}


@pytest.mark.parametrize("heap_type", list(HeapType))
def test_a_loaded_heap_extracts_in_order(heap_type):
    heap = Heap[int](heap_type)
    heap.build_heap([5, 3, 9, 1, 7, 2, 8])

    restored = Heap.from_dict(heap.to_dict())

    extracted = []
    while not restored.is_empty:
        extracted.append(restored.extract())

    assert extracted == sorted(extracted, reverse=(heap_type is HeapType.MAX))


def test_empty_heap_round_trips_with_its_type():
    restored = Heap.from_dict(Heap[int](HeapType.MAX).to_dict())

    assert restored.is_empty and restored.heap_type is HeapType.MAX


@pytest.mark.parametrize(
    "data, message",
    [
        ({"heap_type": "min", "values": [5, 1]}, "min-heap"),
        ({"heap_type": "min", "values": [1, 5, 2, 9, 3, 0]}, "min-heap"),
        ({"heap_type": "max", "values": [1, 5]}, "max-heap"),
    ],
)
def test_from_dict_rejects_arrays_that_break_the_heap_property(data, message):
    with pytest.raises(ValueError, match=message):
        Heap.from_dict(data)


def test_equal_values_are_valid_in_either_heap():
    assert Heap.from_dict({"heap_type": "min", "values": [2, 2, 2]}).size == 3
    assert Heap.from_dict({"heap_type": "max", "values": [2, 2, 2]}).size == 3


@pytest.mark.parametrize(
    "bad",
    [
        None, [], "heap", {},
        {"heap_type": "min"},
        {"values": [1]},
        {"heap_type": "median", "values": [1]},
        {"heap_type": None, "values": [1]},
        {"heap_type": "min", "values": "abc"},
        {"heap_type": "min", "values": [1.5]},
        {"heap_type": "min", "values": [True]},
        {"heap_type": "min", "values": ["1"]},
        {"heap_type": "min", "values": [None]},
    ],
)
def test_from_dict_rejects_malformed_data(bad):
    with pytest.raises(ValueError):
        Heap.from_dict(bad)


def test_from_dict_rejects_oversized_heaps():
    values = list(range(Heap.MAX_LOADED_ITEMS + 1))

    with pytest.raises(ValueError, match="at most"):
        Heap.from_dict({"heap_type": "min", "values": values})