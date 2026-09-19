from __future__ import annotations

from abc import ABC, abstractmethod

from .model import HashTable


class HashTableOperation(ABC):
    """Base class for operations performed on a hash table."""

    @abstractmethod
    def commit(self, table: HashTable) -> object | None:
        """Apply the operation to the hash table."""
        raise NotImplementedError


class InsertOperation(HashTableOperation):
    """Insert a key (and value, in map mode) into the table."""

    def __init__(self, key: object, value: object = None) -> None:
        self.key = key
        self.value = value

    def commit(self, table: HashTable) -> bool:
        return table.insert(self.key, self.value)


class SearchOperation(HashTableOperation):
    """Search for a key without modifying the table."""

    def __init__(self, key: object) -> None:
        self.key = key

    def commit(self, table: HashTable):
        return table.search(self.key)


class DeleteOperation(HashTableOperation):
    """Delete a key from the table."""

    def __init__(self, key: object) -> None:
        self.key = key

    def commit(self, table: HashTable) -> bool:
        return table.delete(self.key)


class ClearOperation(HashTableOperation):
    """Remove every entry from the table."""

    def commit(self, table: HashTable) -> None:
        table.clear()


class NoOpOperation(HashTableOperation):
    """
    Commit nothing.

    Used when the simulation already determined nothing should happen
    to the real table, such as an insert that failed because the
    table was full. Returning a normal InsertOperation in that case
    would just raise the same error again when committed against the
    live table; NoOpOperation guarantees commit() is always safe to
    call once a simulation has finished, regardless of how it ended.
    """

    def commit(self, table: HashTable) -> None:
        return None