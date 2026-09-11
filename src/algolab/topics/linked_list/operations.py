from dataclasses import dataclass

from algolab.topics.linked_list.model import LinkedListModel


class LinkedListOperation:
    """Base class for an operation that can be committed to a linked list."""

    def commit(self, model: LinkedListModel) -> object | None:
        """Apply the operation to the linked-list model."""

        raise NotImplementedError


@dataclass(frozen=True)
class InsertAtBeginningOperation(LinkedListOperation):
    """Insert a value at the beginning of a linked list."""

    data: object

    def commit(self, model: LinkedListModel) -> None:
        model.insert_at_beginning(self.data)


@dataclass(frozen=True)
class InsertAtEndOperation(LinkedListOperation):
    """Insert a value at the end of a linked list."""

    data: object

    def commit(self, model: LinkedListModel) -> None:
        model.insert_at_end(self.data)


@dataclass(frozen=True)
class InsertAtOperation(LinkedListOperation):
    """Insert a value at a specific index."""

    index: int
    data: object

    def commit(self, model: LinkedListModel) -> None:
        model.insert_at(
            index=self.index,
            data=self.data,
        )


@dataclass(frozen=True)
class DeleteAtOperation(LinkedListOperation):
    """Delete the node at a specific index."""

    index: int

    def commit(self, model: LinkedListModel) -> object:
        return model.delete_at(self.index)


@dataclass(frozen=True)
class SearchOperation(LinkedListOperation):
    """Search for a value in a linked list."""

    data: object

    def commit(self, model: LinkedListModel) -> int:
        return model.search(self.data)