"""Operations for the AVL tree.

The BST operation classes only call the tree's public API (insert,
search, delete, find_min, find_max, and the traversals), and AVLTree
exposes exactly the same API, so they are reused as-is. Committing an
InsertOperation or DeleteOperation to an AVLTree performs the same
rebalancing the simulation animated.
"""

from __future__ import annotations

from algolab.topics.bst.operations import (
    BSTOperation as AVLOperation,
    DeleteOperation,
    FindMaxOperation,
    FindMinOperation,
    InOrderTraversalOperation,
    InsertOperation,
    PostOrderTraversalOperation,
    PreOrderTraversalOperation,
    SearchOperation,
)

__all__ = [
    "AVLOperation",
    "DeleteOperation",
    "FindMaxOperation",
    "FindMinOperation",
    "InOrderTraversalOperation",
    "InsertOperation",
    "PostOrderTraversalOperation",
    "PreOrderTraversalOperation",
    "SearchOperation",
]