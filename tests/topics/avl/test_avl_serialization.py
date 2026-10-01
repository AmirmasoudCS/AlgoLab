import random

import pytest

from algolab.topics.avl.model import AVLTree


def _shape(node):
    if node is None:
        return None

    return (node.value, node.height, _shape(node.left), _shape(node.right))


def test_to_dict_is_the_pre_order_sequence():
    tree = AVLTree()

    for value in (10, 20, 30):
        tree.insert(value)

    # The rotation made 20 the root.
    assert tree.to_dict() == {"values": [20, 10, 30]}


def test_round_trip_preserves_exact_shape_and_heights_for_random_trees():
    rng = random.Random(5)

    for _ in range(300):
        tree = AVLTree()
        present: set[int] = set()

        for _ in range(rng.randint(1, 60)):
            value = rng.randint(1, 80)

            if rng.random() < 0.6:
                if value not in present:
                    tree.insert(value)
                    present.add(value)
            elif value in present:
                tree.delete(value)
                present.discard(value)

        restored = AVLTree.from_dict(tree.to_dict())

        assert _shape(restored.root) == _shape(tree.root)
        assert restored.size == tree.size
        assert restored.is_balanced()


def test_loading_does_not_rebalance_a_valid_shape():
    # Pre-order of a perfectly valid, differently shaped AVL tree: the
    # loader must keep it exactly as saved rather than re-inserting.
    data = {"values": [30, 20, 10, 25, 40]}

    restored = AVLTree.from_dict(data)

    assert restored.to_dict() == data


@pytest.mark.parametrize(
    "values",
    [
        [1, 2, 3],           # right-leaning chain: valid BST, not AVL
        [3, 2, 1],           # left-leaning chain
        [1, 2, 3, 4, 5, 6],
    ],
)
def test_from_dict_rejects_a_valid_bst_that_is_not_balanced(values):
    with pytest.raises(ValueError, match="balanced AVL"):
        AVLTree.from_dict({"values": values})


def test_from_dict_rejects_duplicates_and_bad_types():
    for bad in ({"values": [2, 1, 1]}, {"values": [1.5]}, {"values": "x"}, None):
        with pytest.raises(ValueError):
            AVLTree.from_dict(bad)


def test_an_empty_tree_round_trips():
    restored = AVLTree.from_dict(AVLTree().to_dict())

    assert restored.root is None and restored.size == 0


def test_a_loaded_tree_keeps_working_as_an_avl_tree():
    tree = AVLTree.from_dict({"values": [20, 10, 30]})

    for value in (40, 50, 60, 70):
        tree.insert(value)

    assert tree.is_balanced()
    assert tree.in_order() == [10, 20, 30, 40, 50, 60, 70]


def test_replace_with_copies_the_balanced_tree_into_an_existing_one():
    target = AVLTree()
    target.insert(1)

    target.replace_with(AVLTree.from_dict({"values": [20, 10, 30]}))

    assert target.in_order() == [10, 20, 30] and target.is_balanced()