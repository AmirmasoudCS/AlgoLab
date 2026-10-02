import copy
import random

import pytest

from algolab.topics.hash_table.model import (
    CollisionStrategy,
    HashFunction,
    HashTable,
    HashTableMode,
)


def _random_table(strategy, mode, hash_function, seed, capacity=11):
    rng = random.Random(seed)
    table = HashTable(capacity, strategy, mode, hash_function)

    for _ in range(rng.randint(0, 40)):
        key = rng.randint(1, 60)

        try:
            if rng.random() < 0.65:
                table.insert(key, rng.randint(1, 99) if mode is HashTableMode.MAP else None)
            else:
                table.delete(key)
        except IndexError:
            pass                      # a full open-addressing table is fine here

    return table


def _layout(table):
    return (
        [[(e.key, e.value) for e in cell] for cell in table.snapshot()],
        table.tombstones(),
        table.size,
    )


@pytest.mark.parametrize("strategy", list(CollisionStrategy))
@pytest.mark.parametrize("mode", list(HashTableMode))
@pytest.mark.parametrize("hash_function", list(HashFunction))
def test_round_trip_preserves_settings_and_exact_layout(strategy, mode, hash_function):
    for seed in range(25):
        original = _random_table(strategy, mode, hash_function, seed)
        restored = HashTable.from_dict(original.to_dict())

        assert restored.collision_strategy is strategy
        assert restored.mode is mode
        assert restored.hash_function is hash_function
        assert restored.capacity == original.capacity
        assert _layout(restored) == _layout(original)
        assert restored.to_dict() == original.to_dict()


@pytest.mark.parametrize("strategy", list(CollisionStrategy))
def test_a_restored_table_behaves_exactly_like_the_original_afterwards(strategy):
    rng = random.Random(9)

    for seed in range(15):
        original = _random_table(strategy, HashTableMode.MAP, HashFunction.POLYNOMIAL, seed)
        restored = HashTable.from_dict(original.to_dict())

        for _ in range(40):
            key = rng.randint(1, 60)
            action = rng.choice(["insert", "search", "delete"])

            def run(table):
                try:
                    if action == "insert":
                        return table.insert(key, 7)
                    if action == "search":
                        found = table.search(key)
                        return None if found is None else (found.key, found.value)
                    return table.delete(key)
                except IndexError as error:
                    return ("error", str(error))

            assert run(original) == run(restored)

        assert _layout(restored) == _layout(original)


def test_tombstones_survive_and_still_guide_probing():
    table = HashTable(7, CollisionStrategy.LINEAR_PROBING)

    # Three keys that all collide, then delete the middle one.
    colliding = [k for k in range(1, 200) if table.hash_key(k) == 3][:3]

    for key in colliding:
        table.insert(key)

    table.delete(colliding[1])
    assert any(table.tombstones())

    restored = HashTable.from_dict(table.to_dict())

    assert restored.tombstones() == table.tombstones()
    assert restored.search(colliding[2]) is not None, "must probe past the tombstone"
    assert restored.search(colliding[1]) is None


def test_empty_tables_round_trip_for_every_strategy():
    for strategy in CollisionStrategy:
        original = HashTable(5, strategy)
        assert HashTable.from_dict(original.to_dict()).to_dict() == original.to_dict()


def test_string_keys_and_values_round_trip():
    table = HashTable(11, CollisionStrategy.CHAINING, HashTableMode.MAP)
    table.insert("apple", "red")
    table.insert("pear", 3.5)
    table.insert("fig", None)

    assert HashTable.from_dict(table.to_dict()).to_dict() == table.to_dict()


# ---------------------------------------------------------------- invalid data

def _good_open():
    table = HashTable(7, CollisionStrategy.LINEAR_PROBING)
    table.insert(10)
    table.insert(20)
    return table.to_dict()


def _good_chain():
    table = HashTable(5, CollisionStrategy.CHAINING)
    for key in (1, 2, 3, 4, 5, 6):
        table.insert(key)
    return table.to_dict()


@pytest.mark.parametrize("change", [
    {"capacity": 0}, {"capacity": 201}, {"capacity": "7"}, {"capacity": True}, {"capacity": 8},
    {"collision_strategy": "cuckoo"}, {"collision_strategy": None}, {"collision_strategy": ["x"]},
    {"mode": "bag"}, {"hash_function": "md5"},
    {"cells": "abc"}, {"cells": [[]] * 6},                      # wrong number of cells
    {"tombstones": [False] * 6},                                 # wrong number of flags
    {"tombstones": [0] * 7}, {"tombstones": "no"},
])
def test_from_dict_rejects_bad_settings_and_shapes(change):
    with pytest.raises(ValueError):
        HashTable.from_dict({**_good_open(), **change})


def test_from_dict_rejects_non_objects_and_missing_fields():
    for bad in (None, [], "table"):
        with pytest.raises(ValueError):
            HashTable.from_dict(bad)

    for field in ("capacity", "collision_strategy", "mode", "hash_function", "cells", "tombstones"):
        data = _good_open()
        del data[field]

        with pytest.raises(ValueError):
            HashTable.from_dict(data)


def test_from_dict_rejects_a_chained_key_in_the_wrong_bucket():
    data = _good_chain()
    cells = data["cells"]
    source = next(i for i, c in enumerate(cells) if c)
    target = (source + 1) % len(cells)
    cells[target].append(cells[source].pop())          # now in a bucket it does not hash to

    with pytest.raises(ValueError, match="not where"):
        HashTable.from_dict(data)


def test_from_dict_rejects_a_probed_key_unreachable_behind_an_unused_slot():
    table = HashTable(7, CollisionStrategy.LINEAR_PROBING)
    home = table.hash_key(5)
    far = (home + 3) % 7                                # two never-used slots in between

    data = _good_open()
    data["cells"] = [[] for _ in range(7)]
    data["cells"][far] = [{"key": 5, "value": None}]
    data["tombstones"] = [False] * 7

    with pytest.raises(ValueError, match="not where"):
        HashTable.from_dict(data)


def test_a_key_behind_a_tombstone_IS_reachable_and_accepted():
    table = HashTable(7, CollisionStrategy.LINEAR_PROBING)
    home = table.hash_key(5)
    far = (home + 1) % 7

    data = _good_open()
    data["cells"] = [[] for _ in range(7)]
    data["cells"][far] = [{"key": 5, "value": None}]
    data["tombstones"] = [False] * 7
    data["tombstones"][home] = True                     # a deleted slot in front of it

    assert HashTable.from_dict(data).search(5) is not None


def test_from_dict_rejects_duplicate_keys():
    data = _good_chain()
    cells = data["cells"]
    index = next(i for i, c in enumerate(cells) if c)
    cells[index].append(copy.deepcopy(cells[index][0]))

    with pytest.raises(ValueError, match="twice|not where"):
        HashTable.from_dict(data)


def test_from_dict_rejects_tombstone_inconsistencies():
    data = _good_open()
    occupied = next(i for i, c in enumerate(data["cells"]) if c)
    data["tombstones"][occupied] = True

    with pytest.raises(ValueError, match="occupied and marked deleted"):
        HashTable.from_dict(data)

    chain = _good_chain()
    chain["tombstones"][0] = True

    with pytest.raises(ValueError, match="no tombstones"):
        HashTable.from_dict(chain)


def test_from_dict_rejects_two_entries_in_one_open_addressing_slot():
    data = _good_open()
    index = next(i for i, c in enumerate(data["cells"]) if c)
    data["cells"][index].append({"key": 99, "value": None})

    with pytest.raises(ValueError, match="more than one"):
        HashTable.from_dict(data)


@pytest.mark.parametrize("entry", [
    {"key": True, "value": None},
    {"key": 1.5, "value": None},
    {"key": None, "value": None},
    {"key": [1], "value": None},
    {"key": 1, "value": [1]},
    {"key": 1, "value": {"a": 1}},
    {"key": 1},
    {"value": 1},
    5,
])
def test_from_dict_rejects_bad_entries(entry):
    data = _good_chain()
    data["cells"][0] = [entry]

    with pytest.raises(ValueError):
        HashTable.from_dict(data)


def test_from_dict_rejects_oversized_tables():
    capacity = HashTable.MAX_LOADED_CAPACITY
    table = HashTable(capacity, CollisionStrategy.CHAINING)
    data = table.to_dict()

    assert HashTable.from_dict(data).capacity == capacity     # the maximum itself is fine

    data["cells"] = [[] for _ in range(capacity + 1)]
    data["capacity"] = capacity + 1

    with pytest.raises(ValueError):
        HashTable.from_dict(data)

    crowded = HashTable(10, CollisionStrategy.CHAINING).to_dict()
    crowded["cells"][0] = [{"key": n, "value": None} for n in range(HashTable.MAX_LOADED_ENTRIES + 1)]

    with pytest.raises(ValueError):
        HashTable.from_dict(crowded)


def test_replace_with_takes_over_everything():
    target = HashTable(3, CollisionStrategy.CHAINING)
    source = _random_table(CollisionStrategy.QUADRATIC_PROBING, HashTableMode.MAP, HashFunction.POLYNOMIAL, 4)
    expected = source.to_dict()

    target.replace_with(source)

    assert target.to_dict() == expected
    assert target.collision_strategy is CollisionStrategy.QUADRATIC_PROBING