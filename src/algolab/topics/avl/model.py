from __future__ import annotations

from typing import Generic, TypeVar

from algolab.topics.bst.model import BinarySearchTree, TreeNode


T = TypeVar("T")


class AVLNode(TreeNode[T], Generic[T]):
    """A node in an AVL tree.

    Extends the plain BST node with a stored height. A leaf has height 1
    and a missing child counts as height 0, so the balance factor of a
    node is height(left) - height(right).
    """

    def __init__(self, value: T) -> None:
        super().__init__(value)
        self.left: AVLNode[T] | None = None
        self.right: AVLNode[T] | None = None
        self.height = 1


class AVLTree(BinarySearchTree[T], Generic[T]):
    """A self-balancing binary search tree (AVL tree).

    Reuses BinarySearchTree for search, find_min, find_max, the
    traversals, clear, and the size/root properties. Only insert and
    delete differ: both rebalance every node on the path back up to the
    root, using single or double rotations.
    """

    def __init__(self) -> None:
        super().__init__()
        self._last_inserted: AVLNode[T] | None = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def insert(self, value: T) -> AVLNode[T]:
        """Insert a value and rebalance.

        Raises:
            ValueError: If the value already exists in the tree.
                The tree is left unchanged in that case.
        """
        self._last_inserted = None
        self._root = self._insert(self._root, value)
        self._size += 1

        assert self._last_inserted is not None
        return self._last_inserted

    @classmethod
    def from_dict(cls, data: object) -> AVLTree:
        """Build a tree from a dict produced by to_dict().

        The saved pre-order values are placed with plain BST insertion
        and NO rebalancing, which reproduces the saved shape exactly
        (re-inserting through insert() could rotate and change it). The
        result is then checked: a file whose shape is a valid search
        tree but not a balanced AVL tree is rejected.

        Raises:
            ValueError: If the data is malformed, has duplicate values,
                is too large, or does not describe a balanced AVL tree.
        """
        tree = cls()

        for value in cls._validated_values(data):
            tree._insert_without_rebalancing(value)

        tree._recompute_heights(tree._root)

        if not tree.is_balanced():
            raise ValueError(
                "These values form a search tree, but not a balanced AVL "
                "tree (some node's subtrees differ in height by more "
                "than 1)."
            )

        return tree

    def _insert_without_rebalancing(self, value: T) -> None:
        node = AVLNode(value)
        self._size += 1

        if self._root is None:
            self._root = node
            return

        current = self._root

        while True:
            if value < current.value:
                if current.left is None:
                    current.left = node
                    return

                current = current.left
            else:
                if current.right is None:
                    current.right = node
                    return

                current = current.right

    def _recompute_heights(self, node: AVLNode[T] | None) -> int:
        if node is None:
            return 0

        node.height = 1 + max(
            self._recompute_heights(node.left),
            self._recompute_heights(node.right),
        )

        return node.height

    @staticmethod
    def height_of(node: AVLNode[T] | None) -> int:
        """Return the stored height of a node (0 for a missing node)."""
        return node.height if node is not None else 0

    @classmethod
    def balance_factor(cls, node: AVLNode[T] | None) -> int:
        """Return height(left) - height(right) for a node."""
        if node is None:
            return 0

        return cls.height_of(node.left) - cls.height_of(node.right)

    def is_balanced(self) -> bool:
        """Return True if every node has a balance factor in [-1, 1]
        and every stored height is correct."""

        def check(node: AVLNode[T] | None) -> int | None:
            if node is None:
                return 0

            left = check(node.left)
            right = check(node.right)

            if left is None or right is None:
                return None

            if abs(left - right) > 1:
                return None

            height = 1 + max(left, right)

            if node.height != height:
                return None

            return height

        return check(self._root) is not None

    # ------------------------------------------------------------------
    # Insert / delete (recursive, rebalancing on the way back up)
    # ------------------------------------------------------------------

    def _insert(
        self,
        node: AVLNode[T] | None,
        value: T,
    ) -> AVLNode[T]:
        if node is None:
            new_node = AVLNode(value)
            self._last_inserted = new_node
            return new_node

        if value < node.value:
            node.left = self._insert(node.left, value)
        elif value > node.value:
            node.right = self._insert(node.right, value)
        else:
            raise ValueError(
                f"Value {value!r} already exists in the tree."
            )

        return self._rebalance(node)

    def _delete(
        self,
        node: AVLNode[T] | None,
        value: T,
    ) -> tuple[AVLNode[T] | None, T | None]:
        if node is None:
            return None, None

        if value < node.value:
            node.left, deleted_value = self._delete(node.left, value)
        elif value > node.value:
            node.right, deleted_value = self._delete(node.right, value)
        else:
            deleted_value = node.value

            if node.left is None:
                return node.right, deleted_value

            if node.right is None:
                return node.left, deleted_value

            # Two children: copy the in-order successor's value here,
            # then delete the successor from the right subtree
            # (same approach as the plain BST).
            successor = self._find_min_node(node.right)
            node.value = successor.value
            node.right, _ = self._delete(node.right, successor.value)

        if deleted_value is None:
            return node, None

        return self._rebalance(node), deleted_value

    # ------------------------------------------------------------------
    # Balancing
    # ------------------------------------------------------------------

    def _update_height(self, node: AVLNode[T]) -> None:
        node.height = 1 + max(
            self.height_of(node.left),
            self.height_of(node.right),
        )

    def _rebalance(self, node: AVLNode[T]) -> AVLNode[T]:
        """Update a node's height and rotate if it is unbalanced.

        Returns the root of the (possibly rotated) subtree.
        """
        self._update_height(node)
        balance = self.balance_factor(node)

        if balance > 1:
            # Left-heavy. A right-heavy left child means Left-Right.
            if self.balance_factor(node.left) < 0:
                node.left = self._rotate_left(node.left)

            return self._rotate_right(node)

        if balance < -1:
            # Right-heavy. A left-heavy right child means Right-Left.
            if self.balance_factor(node.right) > 0:
                node.right = self._rotate_right(node.right)

            return self._rotate_left(node)

        return node

    def _rotate_right(self, node: AVLNode[T]) -> AVLNode[T]:
        pivot = node.left
        node.left = pivot.right
        pivot.right = node

        self._update_height(node)
        self._update_height(pivot)

        return pivot

    def _rotate_left(self, node: AVLNode[T]) -> AVLNode[T]:
        pivot = node.right
        node.right = pivot.left
        pivot.left = node

        self._update_height(node)
        self._update_height(pivot)

        return pivot