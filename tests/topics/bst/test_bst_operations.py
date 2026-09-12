from algolab.topics.bst.model import BinarySearchTree
from algolab.topics.bst.operations import (
    DeleteOperation,
    FindMaxOperation,
    FindMinOperation,
    InOrderTraversalOperation,
    InsertOperation,
    PostOrderTraversalOperation,
    PreOrderTraversalOperation,
    SearchOperation,
)


def create_tree() -> BinarySearchTree:
    tree = BinarySearchTree()

    for value in [50, 30, 70, 20, 40, 60, 80]:
        tree.insert(value)

    return tree


def test_insert_operation():
    tree = BinarySearchTree()
    operation = InsertOperation(50)

    result = operation.commit(tree)

    assert result is tree.root
    assert tree.root is not None
    assert tree.root.value == 50


def test_search_operation_when_value_exists():
    tree = create_tree()
    operation = SearchOperation(40)

    result = operation.commit(tree)

    assert result is not None
    assert result.value == 40


def test_search_operation_when_value_does_not_exist():
    tree = create_tree()
    operation = SearchOperation(100)

    result = operation.commit(tree)

    assert result is None


def test_delete_operation():
    tree = create_tree()
    operation = DeleteOperation(40)

    result = operation.commit(tree)

    assert result == 40
    assert tree.search(40) is None


def test_find_min_operation():
    tree = create_tree()
    operation = FindMinOperation()

    result = operation.commit(tree)

    assert result.value == 20


def test_find_max_operation():
    tree = create_tree()
    operation = FindMaxOperation()

    result = operation.commit(tree)

    assert result.value == 80


def test_in_order_traversal_operation():
    tree = create_tree()
    operation = InOrderTraversalOperation()

    result = operation.commit(tree)

    assert result == [
        20,
        30,
        40,
        50,
        60,
        70,
        80,
    ]


def test_pre_order_traversal_operation():
    tree = create_tree()
    operation = PreOrderTraversalOperation()

    result = operation.commit(tree)

    assert result == [
        50,
        30,
        20,
        40,
        70,
        60,
        80,
    ]


def test_post_order_traversal_operation():
    tree = create_tree()
    operation = PostOrderTraversalOperation()

    result = operation.commit(tree)

    assert result == [
        20,
        40,
        30,
        60,
        80,
        70,
        50,
    ]