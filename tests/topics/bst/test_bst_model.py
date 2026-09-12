import pytest

from algolab.topics.bst.model import BinarySearchTree, TreeNode


def create_tree() -> BinarySearchTree:
    tree = BinarySearchTree()

    for value in [50, 30, 70, 20, 40, 60, 80]:
        tree.insert(value)

    return tree


def test_tree_starts_empty():
    tree = BinarySearchTree()

    assert tree.root is None
    assert tree.size == 0
    assert tree.is_empty is True


def test_insert_into_empty_tree_creates_root():
    tree = BinarySearchTree()

    node = tree.insert(50)

    assert isinstance(node, TreeNode)
    assert node.value == 50
    assert tree.root is node
    assert tree.size == 1
    assert tree.is_empty is False


def test_insert_places_smaller_value_on_left():
    tree = BinarySearchTree()

    tree.insert(50)
    tree.insert(30)

    assert tree.root is not None
    assert tree.root.left is not None
    assert tree.root.left.value == 30
    assert tree.root.right is None


def test_insert_places_larger_value_on_right():
    tree = BinarySearchTree()

    tree.insert(50)
    tree.insert(70)

    assert tree.root is not None
    assert tree.root.right is not None
    assert tree.root.right.value == 70
    assert tree.root.left is None


def test_insert_builds_correct_tree():
    tree = create_tree()

    assert tree.root is not None
    assert tree.root.value == 50

    assert tree.root.left is not None
    assert tree.root.left.value == 30

    assert tree.root.right is not None
    assert tree.root.right.value == 70

    assert tree.root.left.left is not None
    assert tree.root.left.left.value == 20

    assert tree.root.left.right is not None
    assert tree.root.left.right.value == 40

    assert tree.root.right.left is not None
    assert tree.root.right.left.value == 60

    assert tree.root.right.right is not None
    assert tree.root.right.right.value == 80


def test_insert_increases_size():
    tree = BinarySearchTree()

    tree.insert(50)
    tree.insert(30)
    tree.insert(70)

    assert tree.size == 3


def test_insert_duplicate_raises_value_error():
    tree = BinarySearchTree()

    tree.insert(50)

    with pytest.raises(ValueError):
        tree.insert(50)

    assert tree.size == 1


def test_search_returns_matching_node():
    tree = create_tree()

    node = tree.search(40)

    assert node is not None
    assert node.value == 40


def test_search_returns_none_when_value_is_missing():
    tree = create_tree()

    assert tree.search(100) is None


def test_find_min_returns_smallest_node():
    tree = create_tree()

    node = tree.find_min()

    assert node.value == 20


def test_find_max_returns_largest_node():
    tree = create_tree()

    node = tree.find_max()

    assert node.value == 80


def test_find_min_on_empty_tree_raises():
    tree = BinarySearchTree()

    with pytest.raises(IndexError):
        tree.find_min()


def test_find_max_on_empty_tree_raises():
    tree = BinarySearchTree()

    with pytest.raises(IndexError):
        tree.find_max()


def test_in_order_traversal_returns_sorted_values():
    tree = create_tree()

    assert tree.in_order() == [
        20,
        30,
        40,
        50,
        60,
        70,
        80,
    ]


def test_pre_order_traversal():
    tree = create_tree()

    assert tree.pre_order() == [
        50,
        30,
        20,
        40,
        70,
        60,
        80,
    ]


def test_post_order_traversal():
    tree = create_tree()

    assert tree.post_order() == [
        20,
        40,
        30,
        60,
        80,
        70,
        50,
    ]


def test_delete_leaf_node():
    tree = create_tree()

    deleted = tree.delete(20)

    assert deleted == 20
    assert tree.search(20) is None
    assert tree.in_order() == [
        30,
        40,
        50,
        60,
        70,
        80,
    ]
    assert tree.size == 6


def test_delete_node_with_one_child():
    tree = BinarySearchTree()

    for value in [50, 30, 20]:
        tree.insert(value)

    deleted = tree.delete(30)

    assert deleted == 30
    assert tree.root is not None
    assert tree.root.left is not None
    assert tree.root.left.value == 20
    assert tree.size == 2


def test_delete_node_with_two_children():
    tree = create_tree()

    deleted = tree.delete(30)

    assert deleted == 30
    assert tree.root is not None
    assert tree.root.left is not None
    assert tree.root.left.value == 40
    assert tree.in_order() == [
        20,
        40,
        50,
        60,
        70,
        80,
    ]
    assert tree.size == 6


def test_delete_root_with_two_children():
    tree = create_tree()

    deleted = tree.delete(50)

    assert deleted == 50
    assert tree.root is not None
    assert tree.root.value == 60
    assert tree.in_order() == [
        20,
        30,
        40,
        60,
        70,
        80,
    ]
    assert tree.size == 6


def test_delete_node_with_no_children():
    tree = BinarySearchTree()

    tree.insert(50)

    deleted = tree.delete(50)

    assert deleted == 50
    assert tree.root is None
    assert tree.size == 0
    assert tree.is_empty is True


def test_delete_missing_value_does_nothing():
    tree = create_tree()

    deleted = tree.delete(100)

    assert deleted is None
    assert tree.size == 7
    assert tree.in_order() == [
        20,
        30,
        40,
        50,
        60,
        70,
        80,
    ]


def test_clear_removes_all_nodes():
    tree = create_tree()

    tree.clear()

    assert tree.root is None
    assert tree.size == 0
    assert tree.is_empty is True
    assert tree.in_order() == []
    assert tree.pre_order() == []
    assert tree.post_order() == []