import random

import pytest

from algolab.topics.priority_queue.model import PriorityBacking, PriorityQueue


def _filled(backing, min_first=True, count=12, seed=1):
    rng = random.Random(seed)
    queue = PriorityQueue(backing, min_first)

    for _ in range(count):
        queue.insert(rng.randint(1, 99), rng.randint(1, 20))

    return queue


def _as_pairs(queue):
    return [(entry.value, entry.priority) for entry in queue.entries]


@pytest.mark.parametrize("backing", list(PriorityBacking))
@pytest.mark.parametrize("min_first", [True, False])
def test_round_trip_preserves_backing_order_and_exact_layout(backing, min_first):
    for seed in range(20):
        original = _filled(backing, min_first, seed=seed)
        restored = PriorityQueue.from_dict(original.to_dict())

        assert restored.backing is backing
        assert restored.min_priority_first is min_first
        assert _as_pairs(restored) == _as_pairs(original)


@pytest.mark.parametrize("backing", list(PriorityBacking))
def test_a_loaded_queue_extracts_in_priority_order(backing):
    original = _filled(backing, seed=4)
    restored = PriorityQueue.from_dict(original.to_dict())

    extracted = []
    while not restored.is_empty:
        extracted.append(restored.extract().priority)

    assert extracted == sorted(extracted)


def test_floats_and_equal_priorities_round_trip():
    queue = PriorityQueue(PriorityBacking.SORTED_LIST, True)
    queue.insert("a", 1.5)
    queue.insert("b", 1.5)
    queue.insert("c", 1)

    assert _as_pairs(PriorityQueue.from_dict(queue.to_dict())) == _as_pairs(queue)


def test_empty_queue_round_trips_with_its_settings():
    restored = PriorityQueue.from_dict(
        PriorityQueue(PriorityBacking.SORTED_LIST, False).to_dict()
    )

    assert restored.is_empty
    assert restored.backing is PriorityBacking.SORTED_LIST
    assert restored.min_priority_first is False


def _data(backing="heap", min_first=True, entries=()):
    return {
        "backing": backing,
        "min_priority_first": min_first,
        "entries": [{"value": v, "priority": p} for v, p in entries],
    }


def test_from_dict_rejects_a_heap_that_violates_the_heap_property():
    # priority 1 sits below priority 5 in a min-first heap
    with pytest.raises(ValueError, match="valid heap"):
        PriorityQueue.from_dict(_data("heap", True, [(1, 5), (2, 1)]))

    with pytest.raises(ValueError, match="valid heap"):
        PriorityQueue.from_dict(_data("heap", False, [(1, 1), (2, 5)]))


def test_from_dict_rejects_an_unsorted_sorted_list():
    with pytest.raises(ValueError, match="sorted"):
        PriorityQueue.from_dict(_data("sorted_list", True, [(1, 5), (2, 1)]))

    with pytest.raises(ValueError, match="sorted"):
        PriorityQueue.from_dict(_data("sorted_list", False, [(1, 1), (2, 5)]))


@pytest.mark.parametrize(
    "bad",
    [
        None, [], "pq",
        {},
        {**_data(), "backing": "tree"},
        {**_data(), "backing": None},
        {**_data(), "min_priority_first": "yes"},
        {**_data(), "min_priority_first": 1},
        {**_data(), "entries": "abc"},
        {**_data(), "entries": [5]},
        {**_data(), "entries": [{"value": 1}]},
        {**_data(), "entries": [{"priority": 1}]},
        {**_data(), "entries": [{"value": [1], "priority": 1}]},
        {**_data(), "entries": [{"value": 1, "priority": "high"}]},
        {**_data(), "entries": [{"value": 1, "priority": True}]},
        {**_data(), "entries": [{"value": 1, "priority": float("nan")}]},
    ],
)
def test_from_dict_rejects_malformed_data(bad):
    with pytest.raises(ValueError):
        PriorityQueue.from_dict(bad)


def test_from_dict_rejects_oversized_queues():
    entries = [(n, n) for n in range(PriorityQueue.MAX_LOADED_ENTRIES + 1)]

    with pytest.raises(ValueError, match="at most"):
        PriorityQueue.from_dict(_data("sorted_list", True, entries))


def test_replace_with_takes_over_backing_order_and_entries():
    target = PriorityQueue(PriorityBacking.HEAP, True)
    target.insert(1, 1)

    source = _filled(PriorityBacking.SORTED_LIST, False, seed=2)
    expected = _as_pairs(source)

    target.replace_with(source)

    assert target.backing is PriorityBacking.SORTED_LIST
    assert target.min_priority_first is False
    assert _as_pairs(target) == expected