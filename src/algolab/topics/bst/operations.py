from __future__ import annotations

from abc import ABC, abstractmethod

from .model import BinarySearchTree, TreeNode


class BSTOperation(ABC):
    """Base class for binary search tree operations."""

    @abstractmethod
    def commit(self, tree: BinarySearchTree) -> object | None:
        """Apply the operation to the given tree."""
        raise NotImplementedError


class InsertOperation(BSTOperation):
    """Insert a value into the binary search tree."""

    def __init__(self, value: object) -> None:
        self.value = value

    def commit(self, tree: BinarySearchTree) -> TreeNode:
        return tree.insert(self.value)


class SearchOperation(BSTOperation):
    """Search for a value in the binary search tree."""

    def __init__(self, value: object) -> None:
        self.value = value

    def commit(self, tree: BinarySearchTree) -> TreeNode | None:
        return tree.search(self.value)


class DeleteOperation(BSTOperation):
    """Delete a value from the binary search tree."""

    def __init__(self, value: object) -> None:
        self.value = value

    def commit(self, tree: BinarySearchTree) -> object | None:
        return tree.delete(self.value)


class FindMinOperation(BSTOperation):
    """Find the node containing the minimum value."""

    def commit(self, tree: BinarySearchTree) -> TreeNode:
        return tree.find_min()


class FindMaxOperation(BSTOperation):
    """Find the node containing the maximum value."""

    def commit(self, tree: BinarySearchTree) -> TreeNode:
        return tree.find_max()


class InOrderTraversalOperation(BSTOperation):
    """Perform an in-order traversal."""

    def commit(self, tree: BinarySearchTree) -> list[object]:
        return tree.in_order()


class PreOrderTraversalOperation(BSTOperation):
    """Perform a pre-order traversal."""

    def commit(self, tree: BinarySearchTree) -> list[object]:
        return tree.pre_order()


class PostOrderTraversalOperation(BSTOperation):
    """Perform a post-order traversal."""

    def commit(self, tree: BinarySearchTree) -> list[object]:
        return tree.post_order()