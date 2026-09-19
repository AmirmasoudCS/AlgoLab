from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class CollisionStrategy(Enum):
    """How the table resolves two keys hashing to the same index."""

    CHAINING = "chaining"
    LINEAR_PROBING = "linear_probing"
    QUADRATIC_PROBING = "quadratic_probing"
    DOUBLE_HASHING = "double_hashing"


class HashTableMode(Enum):
    """Whether the table behaves as a set (keys only) or a map (key-value)."""

    SET = "set"
    MAP = "map"


class HashFunction(Enum):
    """
    Which formula turns a key into an index.

    Both are deliberately hand-verifiable rather than using Python's
    randomized built-in hash(), so a student can compute the same
    number themselves and check the table did the right thing.
    """

    SUM_OF_CODES = "sum_of_codes"
    POLYNOMIAL = "polynomial"


@dataclass
class Entry:
    """A single stored key, and its value when the table is in map mode."""

    key: object
    value: object = None


# Open-addressing strategies (everything except chaining) share the same
# slot-array storage shape; only the probe sequence formula differs.
_OPEN_ADDRESSING_STRATEGIES = (
    CollisionStrategy.LINEAR_PROBING,
    CollisionStrategy.QUADRATIC_PROBING,
    CollisionStrategy.DOUBLE_HASHING,
)


class HashTable:
    """
    A fixed-capacity hash table supporting chaining or one of several
    open-addressing probe sequences.

    Capacity never grows automatically. This is a deliberate teaching
    simplification: auto-resizing is a real and useful feature, but it
    also means the bucket a student is looking at can suddenly move,
    which is a lot to take in at the same time as "here's how hashing
    and collisions work." A student who fills the table gets a clear
    error instead of a silent resize.

    Quadratic probing and double hashing both behave best with a prime
    capacity; the default (11) is prime for exactly this reason.
    """

    def __init__(
        self,
        capacity: int = 11,
        collision_strategy: CollisionStrategy = CollisionStrategy.CHAINING,
        mode: HashTableMode = HashTableMode.SET,
        hash_function: HashFunction = HashFunction.SUM_OF_CODES,
    ) -> None:
        self._capacity = capacity
        self._collision_strategy = collision_strategy
        self._mode = mode
        self._hash_function = hash_function

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
    def hash_function(self) -> HashFunction:
        return self._hash_function

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
        re-hash existing entries into the new layout: a chained bucket
        and a probe sequence aren't the same structure wearing
        different clothes, silently converting between them would be
        more confusing than a clean reset.
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

    def set_hash_function(self, hash_function: HashFunction) -> None:
        """
        Change which formula computes a key's index, clearing the
        table since existing entries were placed according to the old
        formula and would no longer be where the new formula expects.
        """

        if hash_function == self._hash_function:
            return

        self._hash_function = hash_function
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
        """Compute a bucket/slot index for a key using the active formula."""

        if self._hash_function is HashFunction.POLYNOMIAL:
            return self._polynomial_hash(key)

        return self._sum_of_codes_hash(key)

    def _sum_of_codes_hash(self, key: object) -> int:
        return sum(ord(character) for character in str(key)) % self._capacity

    def _polynomial_hash(self, key: object) -> int:
        # Classic rolling hash (base 31, as in Java's String.hashCode):
        # h = c0*31^(n-1) + c1*31^(n-2) + ... + c(n-1), computed
        # incrementally as h = h*31 + c at each character.
        total = 0

        for character in str(key):
            total = total * 31 + ord(character)

        return total % self._capacity

    def describe_formula(self) -> str:
        """A general, key-independent description of the active hash formula."""

        if self._hash_function is HashFunction.POLYNOMIAL:
            return "hash(key) = (((c0*31 + c1)*31 + c2)*31 + ...) % capacity"

        return "hash(key) = (sum of character codes in key) % capacity"

    def describe_hash_for(self, key: object) -> str:
        """
        A worked example for a specific key, showing the exact
        arithmetic, so a student can verify the result by hand.

        Shared between the simulator (which narrates each step) and
        the screen (which shows a live preview as the student types a
        key), so both always describe the formula identically.
        """

        codes = [ord(character) for character in str(key)]

        if self._hash_function is HashFunction.POLYNOMIAL:
            total = 0
            for code in codes:
                total = total * 31 + code

            return (
                f"polynomial({codes}, base 31) % {self._capacity} "
                f"= {total} % {self._capacity} = {self.hash_key(key)}"
            )

        breakdown = " + ".join(str(code) for code in codes)
        total = sum(codes)

        return (
            f"({breakdown}) % {self._capacity} "
            f"= {total} % {self._capacity} = {self.hash_key(key)}"
        )

    # ------------------------------------------------------------------
    # Probe sequence (open addressing only)
    # ------------------------------------------------------------------

    def probe_offset(self, key: object, i: int) -> int:
        """
        The offset added to the home index on the i-th probe attempt
        (i starts at 0, meaning the home slot itself).

        This is the one piece of logic that actually differs between
        linear probing, quadratic probing, and double hashing; insert,
        search, and delete are otherwise identical for all three, so
        they all just ask "what's the offset for attempt i?" instead
        of each reimplementing their own arithmetic.
        """

        if self._collision_strategy is CollisionStrategy.LINEAR_PROBING:
            return i

        if self._collision_strategy is CollisionStrategy.QUADRATIC_PROBING:
            return i * i

        if self._collision_strategy is CollisionStrategy.DOUBLE_HASHING:
            return i * self._secondary_hash(key)

        raise ValueError("probe_offset is only defined for open addressing.")

    def _secondary_hash(self, key: object) -> int:
        """
        A second, differently-weighted hash used as the step size for
        double hashing. Positional weighting (character position times
        code) makes it behave differently from the primary hash even
        for the same key, and the result is kept in [1, capacity - 1]
        so the step is never zero (which would make probing stand
        still on one slot forever).
        """

        if self._capacity <= 1:
            return 1

        weighted = sum(
            (position + 1) * ord(character)
            for position, character in enumerate(str(key))
        )

        return 1 + (weighted % (self._capacity - 1))

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

        return self._insert_open_addressing(key, value)

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

    def _insert_open_addressing(self, key: object, value: object) -> bool:
        if self._size >= self._capacity:
            raise IndexError("Hash table is full.")

        index = self.hash_key(key)
        first_tombstone: int | None = None

        for i in range(self._capacity):
            probe = (index + self.probe_offset(key, i)) % self._capacity
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

        raise IndexError(
            "Hash table is full (or the probe sequence couldn't reach "
            "every slot for this capacity)."
        )

    def search(self, key: object) -> Entry | None:
        """Return the matching Entry, or None if the key isn't present."""

        if self._collision_strategy is CollisionStrategy.CHAINING:
            index = self.hash_key(key)

            for entry in self._buckets[index]:
                if entry.key == key:
                    return entry

            return None

        index = self.hash_key(key)

        for i in range(self._capacity):
            probe = (index + self.probe_offset(key, i)) % self._capacity
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

        for i in range(self._capacity):
            probe = (index + self.probe_offset(key, i)) % self._capacity
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
        """Return the open-addressing slot at an index (read-only use)."""

        if self._collision_strategy is CollisionStrategy.CHAINING:
            raise ValueError("slot_at is only valid for open addressing.")

        return self._slots[index]

    def is_tombstone(self, index: int) -> bool:
        """Whether an index holds a tombstone (always False when chaining)."""

        if self._collision_strategy is not CollisionStrategy.CHAINING:
            return self._tombstones[index]

        return False

    def snapshot(self) -> list[list[Entry]]:
        """
        Return the table's contents as one list per bucket/slot index,
        regardless of collision strategy, so the screen can render any
        strategy with the same code. A chaining bucket may contain
        several entries; an open-addressing slot contains at most one.
        """

        if self._collision_strategy is CollisionStrategy.CHAINING:
            return [list(bucket) for bucket in self._buckets]

        return [[] if slot is None else [slot] for slot in self._slots]

    def tombstones(self) -> list[bool]:
        """Which indices are tombstoned (only meaningful for open addressing)."""

        if self._collision_strategy is not CollisionStrategy.CHAINING:
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
            hash_function=self._hash_function,
        )

        if self._collision_strategy is CollisionStrategy.CHAINING:
            new_table._buckets = [list(bucket) for bucket in self._buckets]
        else:
            new_table._slots = list(self._slots)
            new_table._tombstones = list(self._tombstones)

        new_table._size = self._size

        return new_table