import pytest

from algolab.topics.linked_list.model import LinkedListModel
from algolab.topics.linked_list.operations import (
    DeleteAtOperation,
    InsertAtBeginningOperation,
    InsertAtEndOperation,
    InsertAtOperation,
    SearchOperation,
)


def test_insert_at_beginning_operation():
    model = LinkedListModel()
    operation = InsertAtBeginningOperation(data=10)

    result = operation.commit(model)

    assert result is None
    assert model.to_list() == [10]


def test_insert_at_end_operation():
    model = LinkedListModel()
    model.insert_at_end(10)

    operation = InsertAtEndOperation(data=20)

    result = operation.commit(model)

    assert result is None
    assert model.to_list() == [10, 20]


def test_insert_at_operation():
    model = LinkedListModel()
    model.insert_at_end(10)
    model.insert_at_end(30)

    operation = InsertAtOperation(
        index=1,
        data=20,
    )

    result = operation.commit(model)

    assert result is None
    assert model.to_list() == [10, 20, 30]


def test_delete_at_operation():
    model = LinkedListModel()
    model.insert_at_end(10)
    model.insert_at_end(20)
    model.insert_at_end(30)

    operation = DeleteAtOperation(index=1)

    result = operation.commit(model)

    assert result == 20
    assert model.to_list() == [10, 30]


def test_delete_at_operation_invalid_index():
    model = LinkedListModel()

    operation = DeleteAtOperation(index=0)

    with pytest.raises(IndexError):
        operation.commit(model)


def test_search_operation_found():
    model = LinkedListModel()
    model.insert_at_end(10)
    model.insert_at_end(20)
    model.insert_at_end(30)

    operation = SearchOperation(data=20)

    result = operation.commit(model)

    assert result == 1


def test_search_operation_not_found():
    model = LinkedListModel()
    model.insert_at_end(10)
    model.insert_at_end(20)

    operation = SearchOperation(data=50)

    result = operation.commit(model)

    assert result == -1