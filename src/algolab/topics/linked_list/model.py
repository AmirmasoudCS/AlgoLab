from dataclasses import dataclass


@dataclass
class Node:
    """Represents a node in a linked list."""

    data: object
    next: "Node | None" = None


class LinkedListModel:
    """Represents the state of a singly linked list lesson."""

    def __init__(self) -> None:
        self._head: Node | None = None
        self._size = 0

    @property
    def head(self) -> Node | None:
        return self._head

    @property
    def size(self) -> int:
        return self._size

    @property
    def is_empty(self) -> bool:
        return self._head is None

    def insert_at_beginning(self, data: object) -> None:
        """Insert a new node at the beginning of the list."""

        new_node = Node(
            data=data,
            next=self._head,
        )

        self._head = new_node
        self._size += 1

    def insert_at_end(self, data: object) -> None:
        """Insert a new node at the end of the list."""

        new_node = Node(data=data)

        if self._head is None:
            self._head = new_node
            self._size += 1
            return

        current = self._head

        while current.next is not None:
            current = current.next

        current.next = new_node
        self._size += 1

    def insert_at(self, index: int, data: object) -> None:
        """Insert a new node at the specified index."""

        if index < 0 or index > self._size:
            raise IndexError("Linked list index out of range.")

        if index == 0:
            self.insert_at_beginning(data)
            return

        new_node = Node(data=data)

        current = self._head

        for _ in range(index - 1):
            current = current.next

        new_node.next = current.next
        current.next = new_node

        self._size += 1

    def delete_at(self, index: int) -> object:
        """Delete and return the node at the specified index."""

        if index < 0 or index >= self._size:
            raise IndexError("Linked list index out of range.")

        if index == 0:
            deleted_node = self._head
            self._head = self._head.next
            self._size -= 1

            return deleted_node.data

        current = self._head

        for _ in range(index - 1):
            current = current.next

        deleted_node = current.next
        current.next = deleted_node.next

        self._size -= 1

        return deleted_node.data

    def search(self, data: object) -> int:
        """Return the index of the first matching node."""

        current = self._head
        index = 0

        while current is not None:
            if current.data == data:
                return index

            current = current.next
            index += 1

        return -1

    def get(self, index: int) -> object:
        """Return the data stored at the specified index."""

        if index < 0 or index >= self._size:
            raise IndexError("Linked list index out of range.")

        current = self._head

        for _ in range(index):
            current = current.next

        return current.data

    def clear(self) -> None:
        """Remove all nodes from the list."""

        self._head = None
        self._size = 0

    def to_list(self) -> list[object]:
        """Return the linked list contents as a regular list."""

        values = []

        current = self._head

        while current is not None:
            values.append(current.data)
            current = current.next

        return values