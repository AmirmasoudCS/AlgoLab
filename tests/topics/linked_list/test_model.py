import pytest

from algolab.topics.linked_list.model import (
    LinkedListModel,
    Node,
)


def test_new_linked_list_is_empty():
    model = LinkedListModel()

    assert model.head is None
    assert model.size == 0
    assert model.is_empty
    assert model.to_list() == []


def test_node_stores_data_and_next_reference():
    second_node = Node(data=20)
    first_node = Node(
        data=10,
        next=second_node,
    )

    assert first_node.data == 10
    assert first_node.next is second_node
    assert second_node.data == 20
    assert second_node.next is None


def test_insert_at_beginning():
    model = LinkedListModel()

    model.insert_at_beginning(10)
    model.insert_at_beginning(20)
    model.insert_at_beginning(30)

    assert model.to_list() == [30, 20, 10]
    assert model.size == 3
    assert model.head.data == 30


def test_insert_at_beginning_updates_links():
    model = LinkedListModel()

    model.insert_at_beginning(10)
    model.insert_at_beginning(20)

    assert model.head.data == 20
    assert model.head.next.data == 10
    assert model.head.next.next is None


def test_insert_at_end_on_empty_list():
    model = LinkedListModel()

    model.insert_at_end(10)

    assert model.to_list() == [10]
    assert model.size == 1
    assert model.head.data == 10
    assert model.head.next is None


def test_insert_at_end():
    model = LinkedListModel()

    model.insert_at_end(10)
    model.insert_at_end(20)
    model.insert_at_end(30)

    assert model.to_list() == [10, 20, 30]
    assert model.size == 3


def test_insert_at_end_updates_links():
    model = LinkedListModel()

    model.insert_at_end(10)
    model.insert_at_end(20)
    model.insert_at_end(30)

    assert model.head.data == 10
    assert model.head.next.data == 20
    assert model.head.next.next.data == 30
    assert model.head.next.next.next is None


def test_insert_at_index_zero():
    model = LinkedListModel()

    model.insert_at_end(10)
    model.insert_at_end(20)

    model.insert_at(0, 5)

    assert model.to_list() == [5, 10, 20]
    assert model.size == 3


def test_insert_at_middle():
    model = LinkedListModel()

    model.insert_at_end(10)
    model.insert_at_end(20)
    model.insert_at_end(30)

    model.insert_at(1, 15)

    assert model.to_list() == [10, 15, 20, 30]
    assert model.size == 4


def test_insert_at_end_index():
    model = LinkedListModel()

    model.insert_at_end(10)
    model.insert_at_end(20)

    model.insert_at(2, 30)

    assert model.to_list() == [10, 20, 30]
    assert model.size == 3


def test_insert_at_invalid_negative_index():
    model = LinkedListModel()

    with pytest.raises(IndexError):
        model.insert_at(-1, 10)


def test_insert_at_invalid_index_too_large():
    model = LinkedListModel()

    model.insert_at_end(10)

    with pytest.raises(IndexError):
        model.insert_at(2, 20)


def test_delete_at_beginning():
    model = LinkedListModel()

    model.insert_at_end(10)
    model.insert_at_end(20)
    model.insert_at_end(30)

    deleted = model.delete_at(0)

    assert deleted == 10
    assert model.to_list() == [20, 30]
    assert model.size == 2
    assert model.head.data == 20


def test_delete_at_middle():
    model = LinkedListModel()

    model.insert_at_end(10)
    model.insert_at_end(20)
    model.insert_at_end(30)

    deleted = model.delete_at(1)

    assert deleted == 20
    assert model.to_list() == [10, 30]
    assert model.size == 2


def test_delete_at_end():
    model = LinkedListModel()

    model.insert_at_end(10)
    model.insert_at_end(20)
    model.insert_at_end(30)

    deleted = model.delete_at(2)

    assert deleted == 30
    assert model.to_list() == [10, 20]
    assert model.size == 2


def test_delete_only_node():
    model = LinkedListModel()

    model.insert_at_end(10)

    deleted = model.delete_at(0)

    assert deleted == 10
    assert model.is_empty
    assert model.head is None
    assert model.size == 0


def test_delete_at_invalid_negative_index():
    model = LinkedListModel()

    model.insert_at_end(10)

    with pytest.raises(IndexError):
        model.delete_at(-1)


def test_delete_at_invalid_index_too_large():
    model = LinkedListModel()

    model.insert_at_end(10)

    with pytest.raises(IndexError):
        model.delete_at(1)


def test_search_existing_value():
    model = LinkedListModel()

    model.insert_at_end(10)
    model.insert_at_end(20)
    model.insert_at_end(30)

    assert model.search(20) == 1


def test_search_returns_first_matching_index():
    model = LinkedListModel()

    model.insert_at_end(10)
    model.insert_at_end(20)
    model.insert_at_end(20)

    assert model.search(20) == 1


def test_search_missing_value():
    model = LinkedListModel()

    model.insert_at_end(10)
    model.insert_at_end(20)

    assert model.search(50) == -1


def test_search_empty_list():
    model = LinkedListModel()

    assert model.search(10) == -1


def test_get():
    model = LinkedListModel()

    model.insert_at_end(10)
    model.insert_at_end(20)
    model.insert_at_end(30)

    assert model.get(0) == 10
    assert model.get(1) == 20
    assert model.get(2) == 30


def test_get_invalid_negative_index():
    model = LinkedListModel()

    model.insert_at_end(10)

    with pytest.raises(IndexError):
        model.get(-1)


def test_get_invalid_index_too_large():
    model = LinkedListModel()

    model.insert_at_end(10)

    with pytest.raises(IndexError):
        model.get(1)


def test_clear():
    model = LinkedListModel()

    model.insert_at_end(10)
    model.insert_at_end(20)
    model.insert_at_end(30)

    model.clear()

    assert model.head is None
    assert model.size == 0
    assert model.is_empty
    assert model.to_list() == []


def test_to_list():
    model = LinkedListModel()

    model.insert_at_end(10)
    model.insert_at_end(20)
    model.insert_at_end(30)

    assert model.to_list() == [10, 20, 30]