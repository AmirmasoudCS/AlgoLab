from __future__ import annotations

from typing import Generic, TypeVar

from algolab.core.serialization import checked_int_items


T = TypeVar("T")


class TreeNode(Generic[T]):
    """A node in a binary search tree."""

    def __init__(self, value: T) -> None:
        self.value = value
        self.left: TreeNode[T] | None = None
        self.right: TreeNode[T] | None = None


class BinarySearchTree(Generic[T]):
    """A simple binary search tree implementation."""

    # Upper bound on nodes accepted when loading a file. Kept modest
    # because several operations (traversals, simulation snapshots) are
    # recursive, and a hand-made file describing a long chain could
    # otherwise exceed Python's recursion limit.
    MAX_LOADED_NODES = 200

    def __init__(self) -> None:
        self._root: TreeNode[T] | None = None
        self._size = 0

    @property
    def root(self) -> TreeNode[T] | None:
        """Return the root node of the tree."""
        return self._root

    @property
    def size(self) -> int:
        """Return the number of nodes in the tree."""
        return self._size

    @property
    def is_empty(self) -> bool:
        """Return True when the tree contains no nodes."""
        return self._root is None

    def insert(self, value: T) -> TreeNode[T]:
        """Insert a value into the tree.

        Raises:
            ValueError: If the value already exists in the tree.
        """
        new_node = TreeNode(value)

        if self._root is None:
            self._root = new_node
            self._size += 1
            return new_node

        current = self._root

        while True:
            if value < current.value:
                if current.left is None:
                    current.left = new_node
                    self._size += 1
                    return new_node

                current = current.left

            elif value > current.value:
                if current.right is None:
                    current.right = new_node
                    self._size += 1
                    return new_node

                current = current.right

            else:
                raise ValueError(
                    f"Value {value!r} already exists in the tree."
                )

    def search(self, value: T) -> TreeNode[T] | None:
        """Search for a value and return its node if found."""
        current = self._root

        while current is not None:
            if value == current.value:
                return current

            if value < current.value:
                current = current.left
            else:
                current = current.right

        return None

    def delete(self, value: T) -> T | None:
        """Delete a value from the tree.

        Returns:
            The deleted value, or None if the value was not found.
        """
        self._root, deleted_value = self._delete(
            self._root,
            value,
        )

        if deleted_value is not None:
            self._size -= 1

        return deleted_value

    def find_min(self) -> TreeNode[T]:
        """Return the node containing the minimum value.

        Raises:
            IndexError: If the tree is empty.
        """
        if self._root is None:
            raise IndexError(
                "Cannot find the minimum of an empty tree."
            )

        return self._find_min_node(self._root)

    def find_max(self) -> TreeNode[T]:
        """Return the node containing the maximum value.

        Raises:
            IndexError: If the tree is empty.
        """
        if self._root is None:
            raise IndexError(
                "Cannot find the maximum of an empty tree."
            )

        current = self._root

        while current.right is not None:
            current = current.right

        return current

    def in_order(self) -> list[T]:
        """Return the values using in-order traversal."""
        values: list[T] = []
        self._in_order(self._root, values)
        return values

    def pre_order(self) -> list[T]:
        """Return the values using pre-order traversal."""
        values: list[T] = []
        self._pre_order(self._root, values)
        return values

    def post_order(self) -> list[T]:
        """Return the values using post-order traversal."""
        values: list[T] = []
        self._post_order(self._root, values)
        return values

    def clear(self) -> None:
        """Remove all nodes from the tree."""
        self._root = None
        self._size = 0

    def to_dict(self) -> dict:
        """Return a JSON-serializable snapshot of the tree's exact shape.

        The values are saved in pre-order. Inserting a binary search
        tree's pre-order sequence into an empty tree reproduces the same
        shape, so nothing else needs to be stored. This is also stored
        flat (not as nested objects), which keeps even a long chain of
        nodes safe for the JSON encoder.
        """
        return {"values": self.pre_order()}

    @classmethod
    def from_dict(cls, data: object) -> BinarySearchTree:
        """Build a tree from a dict produced by to_dict().

        Raises:
            ValueError: If the data is malformed, has duplicate values,
                or is larger than MAX_LOADED_NODES.
        """
        tree = cls()

        for value in cls._validated_values(data):
            tree.insert(value)

        return tree

    @classmethod
    def _validated_values(cls, data: object) -> list[int]:
        """Shared by BST and AVL loading: whole numbers, no duplicates."""
        values = checked_int_items(
            data, "Tree", cls.MAX_LOADED_NODES, key="values"
        )

        if len(set(values)) != len(values):
            raise ValueError("A tree cannot contain duplicate values.")

        return values

    def replace_with(self, other: BinarySearchTree) -> None:
        """Take over another tree's nodes (it should not be reused)."""
        self._root = other._root
        self._size = other._size

    def _delete(
        self,
        node: TreeNode[T] | None,
        value: T,
    ) -> tuple[TreeNode[T] | None, T | None]:
        if node is None:
            return None, None

        if value < node.value:
            node.left, deleted_value = self._delete(
                node.left,
                value,
            )
            return node, deleted_value

        if value > node.value:
            node.right, deleted_value = self._delete(
                node.right,
                value,
            )
            return node, deleted_value

        deleted_value = node.value

        if node.left is None:
            return node.right, deleted_value

        if node.right is None:
            return node.left, deleted_value

        successor = self._find_min_node(node.right)
        node.value = successor.value

        node.right, _ = self._delete(
            node.right,
            successor.value,
        )

        return node, deleted_value

    def _find_min_node(self, node: TreeNode[T]) -> TreeNode[T]:
        current = node

        while current.left is not None:
            current = current.left

        return current

    def _in_order(
        self,
        node: TreeNode[T] | None,
        values: list[T],
    ) -> None:
        if node is None:
            return

        self._in_order(node.left, values)
        values.append(node.value)
        self._in_order(node.right, values)

    def _pre_order(
        self,
        node: TreeNode[T] | None,
        values: list[T],
    ) -> None:
        if node is None:
            return

        values.append(node.value)
        self._pre_order(node.left, values)
        self._pre_order(node.right, values)

    def _post_order(
        self,
        node: TreeNode[T] | None,
        values: list[T],
    ) -> None:
        if node is None:
            return

        self._post_order(node.left, values)
        self._post_order(node.right, values)
        values.append(node.value)