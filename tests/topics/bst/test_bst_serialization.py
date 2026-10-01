import random

import pytest

from algolab.topics.bst.model import BinarySearchTree


def _shape(node):
    if node is None:
        return None

    return (node.value, _shape(node.left), _shape(node.right))


def _tree(*values):
    tree = BinarySearchTree()

    for value in values:
        tree.insert(value)

    return tree


def test_to_dict_is_the_pre_order_sequence():
    assert _tree(50, 30, 70, 20, 40).to_dict() == {"values": [50, 30, 20, 40, 70]}


def test_empty_tree_round_trips():
    restored = BinarySearchTree.from_dict(BinarySearchTree().to_dict())

    assert restored.is_empty and restored.size == 0


def test_round_trip_preserves_the_exact_shape_even_when_skewed():
    for values in ([1, 2, 3, 4, 5], [5, 4, 3, 2, 1], [50, 10, 90, 5, 15, 60, 95]):
        original = _tree(*values)
        restored = BinarySearchTree.from_dict(original.to_dict())

        assert _shape(restored.root) == _shape(original.root)
        assert restored.size == original.size


def test_round_trip_preserves_shape_for_random_trees():
    rng = random.Random(3)

    for _ in range(200):
        original = _tree(*rng.sample(range(1, 120), rng.randint(0, 50)))
        restored = BinarySearchTree.from_dict(original.to_dict())

        assert _shape(restored.root) == _shape(original.root)


def test_a_tree_shaped_by_deletes_still_round_trips():
    original = _tree(50, 30, 70, 20, 40, 60, 80)
    original.delete(30)
    original.delete(50)

    restored = BinarySearchTree.from_dict(original.to_dict())

    assert _shape(restored.root) == _shape(original.root)


@pytest.mark.parametrize(
    "bad",
    [
        None, [], "values", {},
        {"values": "abc"},
        {"values": [1, 1]},
        {"values": [1.5]},
        {"values": [True]},
        {"values": ["1"]},
        {"values": [None]},
    ],
)
def test_from_dict_rejects_malformed_data(bad):
    with pytest.raises(ValueError):
        BinarySearchTree.from_dict(bad)


def test_from_dict_rejects_oversized_trees():
    too_many = {"values": list(range(BinarySearchTree.MAX_LOADED_NODES + 1))}

    with pytest.raises(ValueError, match="at most"):
        BinarySearchTree.from_dict(too_many)


def test_a_maximum_size_chain_loads_without_hitting_the_recursion_limit():
    chain = {"values": list(range(BinarySearchTree.MAX_LOADED_NODES))}
    tree = BinarySearchTree.from_dict(chain)

    assert tree.size == BinarySearchTree.MAX_LOADED_NODES
    assert tree.in_order() == chain["values"]
    assert tree.pre_order() == chain["values"]


def test_replace_with_takes_over_the_other_tree():
    target = _tree(1, 2, 3)
    source = _tree(10, 5, 15)

    target.replace_with(source)

    assert target.in_order() == [5, 10, 15] and target.size == 3