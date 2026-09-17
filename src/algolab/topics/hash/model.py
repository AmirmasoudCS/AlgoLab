from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class CollisionStrategy(Enum):
    """How the table resolves two keys hashing to the same index."""

    CHAINING = "chaining"
    LINEAR_PROBING = "linear_probing"


class HashTableMode(Enum):
    """Whether the table behaves as a set (keys only) or a map (key-value)."""

    SET = "set"
    MAP = "map"


@dataclass
class Entry:
    """A single stored key, and its value when the table is in map mode."""

    key: object
    value: object = None


class HashTable:
    """
    A fixed-capacity hash table supporting chaining or linear probing.

    Capacity never grows automatically. This is a deliberate teaching
    simplification: auto-resizing is a real and useful feature, but it
    also means the bucket a student is looking at can suddenly move,
    which is a lot to take in at the same time as "here's how hashing
    and collisions work." A student who fills the table gets a clear
    error instead of a silent resize.
    """

    def __init__(
        self,
        capacity: int = 11,
        collision_strategy: CollisionStrategy = CollisionStrategy.CHAINING,
        mode: HashTableMode = HashTableMode.SET,
    ) -> None:
        self._capacity = capacity
        self._collision_strategy = collision_strategy
        self._mode = mode

        self._buckets: list[list[Entry]] | None = None
        self._slots: list[Entry | None] | None = None
        self._tombstones: list[bool] | None = None

        self._size = 0

        self._init_storage()

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def capacity(self) -> int:
        return self._capacity

    @property
    def collision_strategy(self) -> CollisionStrategy:
        return self._collision_strategy

    @property
    def mode(self) -> HashTableMode:
        return self._mode

    @property
    def size(self) -> int:
        return self._size

    @property
    def is_empty(self) -> bool:
        return self._size == 0

    @property
    def load_factor(self) -> float:
        return self._size / self._capacity

    # ------------------------------------------------------------------
    # Configuration
    # ------------------------------------------------------------------

    def _init_storage(self) -> None:
        if self._collision_strategy is CollisionStrategy.CHAINING:
            self._buckets = [[] for _ in range(self._capacity)]
            self._slots = None
            self._tombstones = None
        else:
            self._buckets = None
            self._slots = [None] * self._capacity
            self._tombstones = [False] * self._capacity

        self._size = 0

    def set_collision_strategy(self, strategy: CollisionStrategy) -> None:
        """
        Change how collisions are resolved.

        Switching strategies clears the table rather than trying to
        re-hash existing entries into the new layout, since a chained
        bucket and a probe sequence aren't really the same structure
        wearing different clothes, silently converting between them
        would be more confusing than a clean reset.
        """

        if strategy == self._collision_strategy:
            return

        self._collision_strategy = strategy
        self._init_storage()

    def set_mode(self, mode: HashTableMode) -> None:
        """Change between set and map mode, clearing the table."""

        if mode == self._mode:
            return

        self._mode = mode
        self._init_storage()

    def set_capacity(self, capacity: int) -> None:
        """Change the table's capacity, clearing the table."""

        if capacity < 1:
            raise ValueError("Capacity must be at least 1.")

        self._capacity = capacity
        self._init_storage()

    def clear(self) -> None:
        self._init_storage()

    # ------------------------------------------------------------------
    # Hashing
    # ------------------------------------------------------------------

    def hash_key(self, key: object) -> int:
        """
        Compute a bucket/slot index for a key.

        Deliberately simple (sum of character codes, modulo capacity)
        rather than Python's built-in hash(), which is randomized per
        process and can't be verified by hand. A student can compute
        this same number with a calculator and confirm the table did
        the right thing.
        """

        return sum(ord(character) for character in str(key)) % self._capacity

    # ------------------------------------------------------------------
    # Operations
    # ------------------------------------------------------------------

    def insert(self, key: object, value: object = None) -> bool:
        """
        Insert a key (and value, in map mode).

        Returns True if this created a new entry, False if the key
        already existed (in which case, in map mode, its value is
        updated).
        """

        if self._collision_strategy is CollisionStrategy.CHAINING:
            return self._insert_chaining(key, value)

        return self._insert_probing(key, value)

    def _insert_chaining(self, key: object, value: object) -> bool:
        index = self.hash_key(key)
        bucket = self._buckets[index]

        for position, entry in enumerate(bucket):
            if entry.key == key:
                if self._mode is HashTableMode.MAP:
                    bucket[position] = Entry(key, value)
                return False

        bucket.append(Entry(key, value))
        self._size += 1

        return True

    def _insert_probing(self, key: object, value: object) -> bool:
        if self._size >= self._capacity:
            raise IndexError("Hash table is full.")

        index = self.hash_key(key)
        first_tombstone: int | None = None

        for offset in range(self._capacity):
            probe = (index + offset) % self._capacity
            slot = self._slots[probe]

            if slot is not None and slot.key == key:
                if self._mode is HashTableMode.MAP:
                    self._slots[probe] = Entry(key, value)
                return False

            if slot is None:
                if self._tombstones[probe]:
                    if first_tombstone is None:
                        first_tombstone = probe
                    continue

                target = first_tombstone if first_tombstone is not None else probe

                self._slots[target] = Entry(key, value)
                self._tombstones[target] = False
                self._size += 1

                return True

        if first_tombstone is not None:
            self._slots[first_tombstone] = Entry(key, value)
            self._tombstones[first_tombstone] = False
            self._size += 1

            return True

        raise IndexError("Hash table is full.")

    def search(self, key: object) -> Entry | None:
        """Return the matching Entry, or None if the key isn't present."""

        if self._collision_strategy is CollisionStrategy.CHAINING:
            index = self.hash_key(key)

            for entry in self._buckets[index]:
                if entry.key == key:
                    return entry

            return None

        index = self.hash_key(key)

        for offset in range(self._capacity):
            probe = (index + offset) % self._capacity
            slot = self._slots[probe]

            if slot is None and not self._tombstones[probe]:
                return None

            if slot is not None and slot.key == key:
                return slot

        return None

    def delete(self, key: object) -> bool:
        """Remove a key. Returns True if it was present."""

        if self._collision_strategy is CollisionStrategy.CHAINING:
            index = self.hash_key(key)
            bucket = self._buckets[index]

            for position, entry in enumerate(bucket):
                if entry.key == key:
                    del bucket[position]
                    self._size -= 1
                    return True

            return False

        index = self.hash_key(key)

        for offset in range(self._capacity):
            probe = (index + offset) % self._capacity
            slot = self._slots[probe]

            if slot is None and not self._tombstones[probe]:
                return False

            if slot is not None and slot.key == key:
                self._slots[probe] = None
                self._tombstones[probe] = True
                self._size -= 1
                return True

        return False

    # ------------------------------------------------------------------
    # Rendering support
    # ------------------------------------------------------------------

    def bucket_at(self, index: int) -> list[Entry]:
        """Return the chaining bucket at an index (read-only use)."""

        if self._collision_strategy is not CollisionStrategy.CHAINING:
            raise ValueError("bucket_at is only valid when chaining.")

        return self._buckets[index]

    def slot_at(self, index: int) -> Entry | None:
        """Return the probing slot at an index (read-only use)."""

        if self._collision_strategy is not CollisionStrategy.LINEAR_PROBING:
            raise ValueError("slot_at is only valid when linear probing.")

        return self._slots[index]

    def is_tombstone(self, index: int) -> bool:
        """Whether an index holds a tombstone (always False when chaining)."""

        if self._collision_strategy is CollisionStrategy.LINEAR_PROBING:
            return self._tombstones[index]

        return False

    def snapshot(self) -> list[list[Entry]]:
        """
        Return the table's contents as one list per bucket/slot index,
        regardless of collision strategy, so the screen can render
        either strategy with the same code. A chaining bucket may
        contain several entries; a probing slot contains at most one.
        """

        if self._collision_strategy is CollisionStrategy.CHAINING:
            return [list(bucket) for bucket in self._buckets]

        return [[] if slot is None else [slot] for slot in self._slots]

    def tombstones(self) -> list[bool]:
        """Which indices are tombstoned (only meaningful for probing)."""

        if self._collision_strategy is CollisionStrategy.LINEAR_PROBING:
            return list(self._tombstones)

        return [False] * self._capacity

    def clone(self) -> "HashTable":
        """
        Return a deep-enough copy for the simulator to build a
        step-by-step animation against, without mutating the real
        table until the operation is committed.
        """

        new_table = HashTable(
            capacity=self._capacity,
            collision_strategy=self._collision_strategy,
            mode=self._mode,
        )

        if self._collision_strategy is CollisionStrategy.CHAINING:
            new_table._buckets = [list(bucket) for bucket in self._buckets]
        else:
            new_table._slots = list(self._slots)
            new_table._tombstones = list(self._tombstones)

        new_table._size = self._size

        return new_table