from __future__ import annotations

from dataclasses import dataclass

from algolab.simulation.events import SimulationEvent
from algolab.simulation.state import SimulationState
from algolab.topics.hash_table.model import (
    CollisionStrategy,
    Entry,
    HashTable,
    HashTableMode,
)
from algolab.topics.hash_table.operations import (
    DeleteOperation,
    HashTableOperation,
    InsertOperation,
    SearchOperation,
)


@dataclass(frozen=True)
class ComputeHashEvent(SimulationEvent):
    """Indicates the hash of a key is being computed."""

    key: object
    index: int


@dataclass(frozen=True)
class ProbeSlotEvent(SimulationEvent):
    """Indicates a slot is being examined during linear probing."""

    index: int
    status: str  # "empty" | "tombstone" | "match" | "occupied_other"


@dataclass(frozen=True)
class VisitBucketEntryEvent(SimulationEvent):
    """Indicates an entry in a chaining bucket is being examined."""

    bucket_index: int
    key: object


@dataclass(frozen=True)
class PlaceEntryEvent(SimulationEvent):
    """Indicates a new entry is being placed at an index."""

    index: int
    key: object


@dataclass(frozen=True)
class UpdateEntryEvent(SimulationEvent):
    """Indicates an existing entry's value is being updated (map mode)."""

    index: int
    key: object


@dataclass(frozen=True)
class RemoveEntryEvent(SimulationEvent):
    """Indicates an entry is being removed."""

    index: int
    key: object


@dataclass(frozen=True)
class CompleteHashOperationEvent(SimulationEvent):
    """Indicates the operation has finished."""

    operation: str
    found: bool | None


@dataclass(frozen=True)
class HashTableSimulationState:
    """
    Represents the visual state of a hash table operation.

    Shared across insert, search, and delete for the same reason
    GraphAlgorithmState is shared across graph algorithms: the screen
    only needs "what does the table look like, what index is active,
    what path did probing take" regardless of which operation produced
    it.
    """

    description: str

    buckets: tuple[tuple[Entry, ...], ...]
    tombstones: tuple[bool, ...]

    highlighted_index: int | None = None
    probe_trail: tuple[int, ...] = ()
    result: object = None


@dataclass(frozen=True)
class HashTableSimulation:
    """Represents a complete hash table operation run."""

    states: tuple[SimulationState, ...]
    operation: HashTableOperation

    def commit(self, table: HashTable) -> object | None:
        """Commit the simulated operation to the real table."""
        return self.operation.commit(table)


class HashTableSimulator:
    """Creates step-by-step simulations for hash table operations."""

    def __init__(self, model: HashTable) -> None:
        self.model = model

    # ------------------------------------------------------------------
    # Insert
    # ------------------------------------------------------------------

    def insert(self, key: object, value: object = None) -> HashTableSimulation:
        clone = self.model.clone()
        states: list[SimulationState] = []

        def add_state(
            events: list[SimulationEvent],
            description: str,
            highlighted: int | None = None,
            probe_trail: tuple[int, ...] = (),
            result: object = None,
        ) -> None:
            states.append(
                SimulationState(
                    data=self._snapshot(
                        clone, description, highlighted, probe_trail, result
                    ),
                    events=events,
                    step=len(states),
                )
            )

        index = clone.hash_key(key)

        add_state(
            [ComputeHashEvent(key=key, index=index)],
            f"Compute the hash of {key!r}: {self._describe_hash(clone, key, index)}.",
            highlighted=index,
        )

        if clone.collision_strategy is CollisionStrategy.CHAINING:
            found_existing = False

            for entry in clone.bucket_at(index):
                add_state(
                    [VisitBucketEntryEvent(bucket_index=index, key=entry.key)],
                    (
                        f"Check bucket {index}: does it already contain "
                        f"{key!r}? Found {entry.key!r}."
                    ),
                    highlighted=index,
                )

                if entry.key == key:
                    found_existing = True
                    break

            clone.insert(key, value)

            if found_existing and clone.mode is HashTableMode.MAP:
                add_state(
                    [UpdateEntryEvent(index=index, key=key)],
                    f"{key!r} already exists in bucket {index}. Update its value.",
                    highlighted=index,
                )
            elif found_existing:
                add_state(
                    [CompleteHashOperationEvent("insert", found=True)],
                    f"{key!r} already exists in bucket {index}. No change needed.",
                    highlighted=index,
                    result=False,
                )

                return HashTableSimulation(
                    states=tuple(states),
                    operation=InsertOperation(key, value),
                )
            else:
                add_state(
                    [PlaceEntryEvent(index=index, key=key)],
                    f"{key!r} was not found in bucket {index}. Add it there.",
                    highlighted=index,
                )

        else:
            probe_trail: list[int] = []
            found_existing = False

            for offset in range(clone.capacity):
                probe = (index + offset) % clone.capacity
                probe_trail.append(probe)

                slot = clone.slot_at(probe)
                tombstoned = clone.is_tombstone(probe)

                if slot is not None and slot.key == key:
                    add_state(
                        [ProbeSlotEvent(index=probe, status="match")],
                        f"Slot {probe} already holds {key!r}.",
                        highlighted=probe,
                        probe_trail=tuple(probe_trail),
                    )
                    found_existing = True
                    break

                if slot is None:
                    status = "tombstone" if tombstoned else "empty"

                    add_state(
                        [ProbeSlotEvent(index=probe, status=status)],
                        (
                            f"Slot {probe} is a tombstone from a previous "
                            "deletion, keep probing."
                            if tombstoned
                            else f"Slot {probe} is empty. {key!r} isn't here."
                        ),
                        highlighted=probe,
                        probe_trail=tuple(probe_trail),
                    )

                    if not tombstoned:
                        break

                    continue

                add_state(
                    [ProbeSlotEvent(index=probe, status="occupied_other")],
                    (
                        f"Slot {probe} holds a different key "
                        f"({slot.key!r}). Keep probing."
                    ),
                    highlighted=probe,
                    probe_trail=tuple(probe_trail),
                )

            try:
                clone.insert(key, value)
            except IndexError:
                add_state(
                    [],
                    "The table is full. Cannot insert.",
                    result=None,
                )

                return HashTableSimulation(
                    states=tuple(states),
                    operation=InsertOperation(key, value),
                )

            if found_existing and clone.mode is HashTableMode.MAP:
                add_state(
                    [UpdateEntryEvent(index=probe_trail[-1], key=key)],
                    f"{key!r} already exists. Update its value.",
                    highlighted=probe_trail[-1],
                )
            elif found_existing:
                add_state(
                    [CompleteHashOperationEvent("insert", found=True)],
                    f"{key!r} already exists. No change needed.",
                    highlighted=probe_trail[-1],
                    result=False,
                )

                return HashTableSimulation(
                    states=tuple(states),
                    operation=InsertOperation(key, value),
                )
            else:
                placed_index = self._find_index_of(clone, key)

                add_state(
                    [PlaceEntryEvent(index=placed_index, key=key)],
                    f"Place {key!r} at slot {placed_index}.",
                    highlighted=placed_index,
                )

        add_state(
            [CompleteHashOperationEvent("insert", found=found_existing)],
            "Insert is complete.",
            result=True,
        )

        return HashTableSimulation(
            states=tuple(states),
            operation=InsertOperation(key, value),
        )

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    def search(self, key: object) -> HashTableSimulation:
        clone = self.model.clone()
        states: list[SimulationState] = []

        def add_state(
            events: list[SimulationEvent],
            description: str,
            highlighted: int | None = None,
            probe_trail: tuple[int, ...] = (),
            result: object = None,
        ) -> None:
            states.append(
                SimulationState(
                    data=self._snapshot(
                        clone, description, highlighted, probe_trail, result
                    ),
                    events=events,
                    step=len(states),
                )
            )

        index = clone.hash_key(key)

        add_state(
            [ComputeHashEvent(key=key, index=index)],
            f"Compute the hash of {key!r}: {self._describe_hash(clone, key, index)}.",
            highlighted=index,
        )

        if clone.collision_strategy is CollisionStrategy.CHAINING:
            for entry in clone.bucket_at(index):
                add_state(
                    [VisitBucketEntryEvent(bucket_index=index, key=entry.key)],
                    f"Check bucket {index}: is this {key!r}? Found {entry.key!r}.",
                    highlighted=index,
                )

                if entry.key == key:
                    add_state(
                        [CompleteHashOperationEvent("search", found=True)],
                        f"Found {key!r} in bucket {index}.",
                        highlighted=index,
                        result=entry,
                    )

                    return HashTableSimulation(
                        states=tuple(states), operation=SearchOperation(key)
                    )

            add_state(
                [CompleteHashOperationEvent("search", found=False)],
                f"{key!r} was not found in bucket {index}.",
                highlighted=index,
                result=None,
            )

            return HashTableSimulation(
                states=tuple(states), operation=SearchOperation(key)
            )

        probe_trail: list[int] = []

        for offset in range(clone.capacity):
            probe = (index + offset) % clone.capacity
            probe_trail.append(probe)

            slot = clone.slot_at(probe)
            tombstoned = clone.is_tombstone(probe)

            if slot is not None and slot.key == key:
                add_state(
                    [ProbeSlotEvent(index=probe, status="match")],
                    f"Found {key!r} at slot {probe}.",
                    highlighted=probe,
                    probe_trail=tuple(probe_trail),
                )

                add_state(
                    [CompleteHashOperationEvent("search", found=True)],
                    "Search is complete.",
                    highlighted=probe,
                    result=slot,
                )

                return HashTableSimulation(
                    states=tuple(states), operation=SearchOperation(key)
                )

            if slot is None:
                status = "tombstone" if tombstoned else "empty"

                add_state(
                    [ProbeSlotEvent(index=probe, status=status)],
                    (
                        f"Slot {probe} is a tombstone, keep probing."
                        if tombstoned
                        else f"Slot {probe} is empty. {key!r} isn't in the table."
                    ),
                    highlighted=probe,
                    probe_trail=tuple(probe_trail),
                )

                if not tombstoned:
                    break

                continue

            add_state(
                [ProbeSlotEvent(index=probe, status="occupied_other")],
                f"Slot {probe} holds a different key ({slot.key!r}). Keep probing.",
                highlighted=probe,
                probe_trail=tuple(probe_trail),
            )

        add_state(
            [CompleteHashOperationEvent("search", found=False)],
            f"{key!r} was not found.",
            result=None,
        )

        return HashTableSimulation(states=tuple(states), operation=SearchOperation(key))

    # ------------------------------------------------------------------
    # Delete
    # ------------------------------------------------------------------

    def delete(self, key: object) -> HashTableSimulation:
        clone = self.model.clone()
        states: list[SimulationState] = []

        def add_state(
            events: list[SimulationEvent],
            description: str,
            highlighted: int | None = None,
            probe_trail: tuple[int, ...] = (),
            result: object = None,
        ) -> None:
            states.append(
                SimulationState(
                    data=self._snapshot(
                        clone, description, highlighted, probe_trail, result
                    ),
                    events=events,
                    step=len(states),
                )
            )

        index = clone.hash_key(key)

        add_state(
            [ComputeHashEvent(key=key, index=index)],
            f"Compute the hash of {key!r}: {self._describe_hash(clone, key, index)}.",
            highlighted=index,
        )

        if clone.collision_strategy is CollisionStrategy.CHAINING:
            found = False

            for entry in clone.bucket_at(index):
                add_state(
                    [VisitBucketEntryEvent(bucket_index=index, key=entry.key)],
                    f"Check bucket {index}: is this {key!r}? Found {entry.key!r}.",
                    highlighted=index,
                )

                if entry.key == key:
                    found = True
                    break

            clone.delete(key)

            if found:
                add_state(
                    [RemoveEntryEvent(index=index, key=key)],
                    f"Remove {key!r} from bucket {index}.",
                    highlighted=index,
                    result=True,
                )
            else:
                add_state(
                    [CompleteHashOperationEvent("delete", found=False)],
                    f"{key!r} was not found in bucket {index}. Nothing to delete.",
                    highlighted=index,
                    result=False,
                )

                return HashTableSimulation(
                    states=tuple(states), operation=DeleteOperation(key)
                )

        else:
            probe_trail: list[int] = []
            found_index: int | None = None

            for offset in range(clone.capacity):
                probe = (index + offset) % clone.capacity
                probe_trail.append(probe)

                slot = clone.slot_at(probe)
                tombstoned = clone.is_tombstone(probe)

                if slot is not None and slot.key == key:
                    add_state(
                        [ProbeSlotEvent(index=probe, status="match")],
                        f"Found {key!r} at slot {probe}.",
                        highlighted=probe,
                        probe_trail=tuple(probe_trail),
                    )
                    found_index = probe
                    break

                if slot is None:
                    status = "tombstone" if tombstoned else "empty"

                    add_state(
                        [ProbeSlotEvent(index=probe, status=status)],
                        (
                            f"Slot {probe} is a tombstone, keep probing."
                            if tombstoned
                            else f"Slot {probe} is empty. {key!r} isn't in the table."
                        ),
                        highlighted=probe,
                        probe_trail=tuple(probe_trail),
                    )

                    if not tombstoned:
                        break

                    continue

                add_state(
                    [ProbeSlotEvent(index=probe, status="occupied_other")],
                    f"Slot {probe} holds a different key ({slot.key!r}). Keep probing.",
                    highlighted=probe,
                    probe_trail=tuple(probe_trail),
                )

            clone.delete(key)

            if found_index is not None:
                add_state(
                    [RemoveEntryEvent(index=found_index, key=key)],
                    (
                        f"Remove {key!r} from slot {found_index} and mark it "
                        "as a tombstone, so later searches can keep probing "
                        "past this point."
                    ),
                    highlighted=found_index,
                    result=True,
                )
            else:
                add_state(
                    [CompleteHashOperationEvent("delete", found=False)],
                    f"{key!r} was not found. Nothing to delete.",
                    result=False,
                )

                return HashTableSimulation(
                    states=tuple(states), operation=DeleteOperation(key)
                )

        add_state(
            [CompleteHashOperationEvent("delete", found=True)],
            "Delete is complete.",
            result=True,
        )

        return HashTableSimulation(states=tuple(states), operation=DeleteOperation(key))

    # ------------------------------------------------------------------
    # Shared helpers
    # ------------------------------------------------------------------

    def _find_index_of(self, table: HashTable, key: object) -> int:
        """Locate where a key actually landed, for describing the final placement."""

        index = table.hash_key(key)

        for offset in range(table.capacity):
            probe = (index + offset) % table.capacity
            slot = table.slot_at(probe)

            if slot is not None and slot.key == key:
                return probe

        raise KeyError(f"{key!r} not found after insertion; this is a bug.")

    def _describe_hash(self, table: HashTable, key: object, index: int) -> str:
        codes = [ord(character) for character in str(key)]
        breakdown = " + ".join(str(code) for code in codes)
        total = sum(codes)

        return f"({breakdown}) % {table.capacity} = {total} % {table.capacity} = {index}"

    def _snapshot(
        self,
        table: HashTable,
        description: str,
        highlighted: int | None,
        probe_trail: tuple[int, ...],
        result: object,
    ) -> HashTableSimulationState:
        return HashTableSimulationState(
            description=description,
            buckets=tuple(tuple(bucket) for bucket in table.snapshot()),
            tombstones=tuple(table.tombstones()),
            highlighted_index=highlighted,
            probe_trail=probe_trail,
            result=result,
        )