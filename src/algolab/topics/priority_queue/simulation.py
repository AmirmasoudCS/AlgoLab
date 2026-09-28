from __future__ import annotations

from dataclasses import dataclass

from algolab.simulation.events import SimulationEvent
from algolab.simulation.state import SimulationState
from algolab.topics.priority_queue.model import (
    PriorityBacking,
    PriorityEntry,
    PriorityQueue,
)
from algolab.topics.priority_queue.operations import (
    ExtractOperation,
    InsertOperation,
    PeekOperation,
    PriorityQueueOperation,
)


@dataclass(frozen=True)
class CreateEntryEvent(SimulationEvent):
    """Indicates a new entry is being created, before it enters the array."""

    index: int
    value: object
    priority: float


@dataclass(frozen=True)
class CompareEntriesEvent(SimulationEvent):
    """Indicates two existing entries (both already in the array) are
    being compared -- used by the heap backing's bubble up/down."""

    first_index: int
    second_index: int


@dataclass(frozen=True)
class CompareNewEntryEvent(SimulationEvent):
    """
    Indicates the not-yet-placed new entry is being compared against an
    existing entry at this index -- used by the sorted-list backing's
    scan for an insertion point, where one side of the comparison isn't
    in the array yet.
    """

    index: int


@dataclass(frozen=True)
class SwapEntriesEvent(SimulationEvent):
    """Indicates two entries are being swapped (heap backing only)."""

    first_index: int
    second_index: int


@dataclass(frozen=True)
class PlaceEntryEvent(SimulationEvent):
    """Indicates the new entry is being placed at this index."""

    index: int
    value: object
    priority: float


@dataclass(frozen=True)
class RemoveEntryEvent(SimulationEvent):
    """Indicates an entry is being removed."""

    index: int
    value: object
    priority: float


@dataclass(frozen=True)
class MoveLastEntryEvent(SimulationEvent):
    """Indicates the last entry is moved to the root (heap extract)."""

    from_index: int
    to_index: int


@dataclass(frozen=True)
class CompletePriorityQueueOperationEvent(SimulationEvent):
    """Indicates a priority queue operation has completed."""

    operation: str


@dataclass(frozen=True)
class PriorityQueueSimulationState:
    """Represents the visual state of a priority queue simulation."""

    entries: tuple[PriorityEntry, ...]
    backing: PriorityBacking
    min_priority_first: bool
    description: str

    current_index: int | None = None
    compared_indices: tuple[int, int] | None = None
    swapped_indices: tuple[int, int] | None = None
    created_index: int | None = None
    removed_index: int | None = None
    peeked_index: int | None = None


@dataclass(frozen=True)
class PriorityQueueSimulation:
    """Represents a complete priority queue simulation."""

    states: tuple[SimulationState, ...]
    operation: PriorityQueueOperation

    def commit(self, queue: PriorityQueue) -> object | None:
        """Commit the simulated operation to the real priority queue."""
        return self.operation.commit(queue)


class PriorityQueueSimulator:
    """Creates step-by-step simulations for priority queue operations."""

    def __init__(self, model: PriorityQueue) -> None:
        self.model = model

    # ------------------------------------------------------------------
    # Insert
    # ------------------------------------------------------------------

    def insert(self, value: object, priority: float) -> PriorityQueueSimulation:
        backing = self.model.backing
        min_first = self.model.min_priority_first

        states: list[SimulationState] = []
        entries = tuple(self.model.entries)

        states.append(
            self._create_state(
                entries=entries,
                backing=backing,
                min_priority_first=min_first,
                events=[],
                step=len(states),
                description="Initial state of the priority queue.",
            )
        )

        if backing is PriorityBacking.HEAP:
            return self._insert_heap(states, entries, backing, min_first, value, priority)

        return self._insert_sorted_list(states, entries, backing, min_first, value, priority)

    def _insert_heap(
        self,
        states: list[SimulationState],
        entries: tuple[PriorityEntry, ...],
        backing: PriorityBacking,
        min_first: bool,
        value: object,
        priority: float,
    ) -> PriorityQueueSimulation:
        insertion_index = len(entries)

        states.append(
            self._create_state(
                entries=entries,
                backing=backing,
                min_priority_first=min_first,
                events=[
                    CreateEntryEvent(index=insertion_index, value=value, priority=priority)
                ],
                step=len(states),
                description=f"Create a new entry (value={value}, priority={priority}).",
                created_index=insertion_index,
            )
        )

        new_entry = PriorityEntry(value=value, priority=priority)
        entries = tuple(list(entries) + [new_entry])

        states.append(
            self._create_state(
                entries=entries,
                backing=backing,
                min_priority_first=min_first,
                events=[],
                step=len(states),
                description=(
                    f"Add the entry to the end of the heap array "
                    f"at index {insertion_index}."
                ),
                created_index=insertion_index,
            )
        )

        current_index = insertion_index

        while current_index > 0:
            parent_index = (current_index - 1) // 2

            states.append(
                self._create_state(
                    entries=entries,
                    backing=backing,
                    min_priority_first=min_first,
                    events=[
                        CompareEntriesEvent(
                            first_index=current_index, second_index=parent_index
                        )
                    ],
                    step=len(states),
                    description=(
                        f"Compare the entry at index {current_index} "
                        f"(priority={entries[current_index].priority}) with its "
                        f"parent at index {parent_index} "
                        f"(priority={entries[parent_index].priority})."
                    ),
                    current_index=current_index,
                    compared_indices=(current_index, parent_index),
                )
            )

            if not self._has_priority(
                min_first, entries[current_index], entries[parent_index]
            ):
                states.append(
                    self._create_state(
                        entries=entries,
                        backing=backing,
                        min_priority_first=min_first,
                        events=[
                            CompletePriorityQueueOperationEvent(operation="insert")
                        ],
                        step=len(states),
                        description=(
                            "The entry already satisfies the heap property "
                            "with its parent. Insert is complete."
                        ),
                    )
                )

                return PriorityQueueSimulation(
                    states=tuple(states),
                    operation=InsertOperation(value, priority),
                )

            states.append(
                self._create_state(
                    entries=entries,
                    backing=backing,
                    min_priority_first=min_first,
                    events=[
                        SwapEntriesEvent(
                            first_index=current_index, second_index=parent_index
                        )
                    ],
                    step=len(states),
                    description=(
                        f"Swap the entries at index {current_index} "
                        f"and {parent_index}."
                    ),
                    swapped_indices=(current_index, parent_index),
                )
            )

            entries_list = list(entries)
            entries_list[current_index], entries_list[parent_index] = (
                entries_list[parent_index],
                entries_list[current_index],
            )
            entries = tuple(entries_list)

            states.append(
                self._create_state(
                    entries=entries,
                    backing=backing,
                    min_priority_first=min_first,
                    events=[],
                    step=len(states),
                    description=(
                        f"After the swap, the entry is now at index {parent_index}."
                    ),
                    current_index=parent_index,
                )
            )

            current_index = parent_index

        states.append(
            self._create_state(
                entries=entries,
                backing=backing,
                min_priority_first=min_first,
                events=[CompletePriorityQueueOperationEvent(operation="insert")],
                step=len(states),
                description="Insert operation is complete.",
            )
        )

        return PriorityQueueSimulation(
            states=tuple(states),
            operation=InsertOperation(value, priority),
        )

    def _insert_sorted_list(
        self,
        states: list[SimulationState],
        entries: tuple[PriorityEntry, ...],
        backing: PriorityBacking,
        min_first: bool,
        value: object,
        priority: float,
    ) -> PriorityQueueSimulation:
        new_entry = PriorityEntry(value=value, priority=priority)

        states.append(
            self._create_state(
                entries=entries,
                backing=backing,
                min_priority_first=min_first,
                events=[
                    CreateEntryEvent(index=len(entries), value=value, priority=priority)
                ],
                step=len(states),
                description=f"Create a new entry (value={value}, priority={priority}).",
            )
        )

        scan_index = 0

        while scan_index < len(entries) and self._has_priority(
            min_first, entries[scan_index], new_entry
        ):
            states.append(
                self._create_state(
                    entries=entries,
                    backing=backing,
                    min_priority_first=min_first,
                    events=[CompareNewEntryEvent(index=scan_index)],
                    step=len(states),
                    description=(
                        f"Compare the new entry (priority={priority}) with the "
                        f"entry at index {scan_index} "
                        f"(priority={entries[scan_index].priority}); index "
                        f"{scan_index} outranks it, so keep scanning."
                    ),
                    current_index=scan_index,
                )
            )

            scan_index += 1

        states.append(
            self._create_state(
                entries=entries,
                backing=backing,
                min_priority_first=min_first,
                events=[
                    PlaceEntryEvent(index=scan_index, value=value, priority=priority)
                ],
                step=len(states),
                description=(
                    f"Insert the new entry at index {scan_index}; every entry "
                    "after it shifts one position to the right."
                ),
                current_index=scan_index,
            )
        )

        entries_list = list(entries)
        entries_list.insert(scan_index, new_entry)
        entries = tuple(entries_list)

        states.append(
            self._create_state(
                entries=entries,
                backing=backing,
                min_priority_first=min_first,
                events=[],
                step=len(states),
                description="The array remains fully sorted by priority.",
                created_index=scan_index,
            )
        )

        states.append(
            self._create_state(
                entries=entries,
                backing=backing,
                min_priority_first=min_first,
                events=[CompletePriorityQueueOperationEvent(operation="insert")],
                step=len(states),
                description="Insert operation is complete.",
            )
        )

        return PriorityQueueSimulation(
            states=tuple(states),
            operation=InsertOperation(value, priority),
        )

    # ------------------------------------------------------------------
    # Extract
    # ------------------------------------------------------------------

    def extract(self) -> PriorityQueueSimulation:
        backing = self.model.backing
        min_first = self.model.min_priority_first

        states: list[SimulationState] = []
        entries = tuple(self.model.entries)

        states.append(
            self._create_state(
                entries=entries,
                backing=backing,
                min_priority_first=min_first,
                events=[],
                step=len(states),
                description="Initial state of the priority queue.",
            )
        )

        if not entries:
            states.append(
                self._create_state(
                    entries=entries,
                    backing=backing,
                    min_priority_first=min_first,
                    events=[
                        CompletePriorityQueueOperationEvent(operation="extract_empty")
                    ],
                    step=len(states),
                    description="The queue is empty. Nothing can be extracted.",
                )
            )

            return PriorityQueueSimulation(
                states=tuple(states), operation=ExtractOperation()
            )

        top_entry = entries[0]

        if backing is PriorityBacking.HEAP:
            return self._extract_heap(states, entries, backing, min_first, top_entry)

        return self._extract_sorted_list(states, entries, backing, min_first, top_entry)

    def _extract_heap(
        self,
        states: list[SimulationState],
        entries: tuple[PriorityEntry, ...],
        backing: PriorityBacking,
        min_first: bool,
        top_entry: PriorityEntry,
    ) -> PriorityQueueSimulation:
        states.append(
            self._create_state(
                entries=entries,
                backing=backing,
                min_priority_first=min_first,
                events=[
                    RemoveEntryEvent(
                        index=0, value=top_entry.value, priority=top_entry.priority
                    )
                ],
                step=len(states),
                description=(
                    f"Extract the entry at index 0 "
                    f"(value={top_entry.value}, priority={top_entry.priority})."
                ),
                current_index=0,
                removed_index=0,
            )
        )

        if len(entries) == 1:
            entries = ()

            states.append(
                self._create_state(
                    entries=entries,
                    backing=backing,
                    min_priority_first=min_first,
                    events=[],
                    step=len(states),
                    description=(
                        "The heap contained only one entry, so it is now empty."
                    ),
                )
            )

            states.append(
                self._create_state(
                    entries=entries,
                    backing=backing,
                    min_priority_first=min_first,
                    events=[
                        CompletePriorityQueueOperationEvent(operation="extract")
                    ],
                    step=len(states),
                    description=(
                        f"Extract operation is complete. Removed "
                        f"value={top_entry.value}, priority={top_entry.priority}."
                    ),
                )
            )

            return PriorityQueueSimulation(
                states=tuple(states), operation=ExtractOperation()
            )

        last_index = len(entries) - 1
        last_entry = entries[last_index]

        states.append(
            self._create_state(
                entries=entries,
                backing=backing,
                min_priority_first=min_first,
                events=[MoveLastEntryEvent(from_index=last_index, to_index=0)],
                step=len(states),
                description=(
                    f"Move the last entry (index {last_index}) to the root position."
                ),
                current_index=0,
            )
        )

        entries = tuple([last_entry, *entries[1:-1]])

        states.append(
            self._create_state(
                entries=entries,
                backing=backing,
                min_priority_first=min_first,
                events=[],
                step=len(states),
                description=(
                    "Place the last entry at the root. The heap property "
                    "may now be violated."
                ),
                current_index=0,
            )
        )

        current_index = 0

        while True:
            left_index = 2 * current_index + 1
            right_index = 2 * current_index + 2

            if left_index >= len(entries):
                break

            priority_index = left_index

            if right_index < len(entries) and self._has_priority(
                min_first, entries[right_index], entries[left_index]
            ):
                priority_index = right_index

            states.append(
                self._create_state(
                    entries=entries,
                    backing=backing,
                    min_priority_first=min_first,
                    events=[
                        CompareEntriesEvent(
                            first_index=current_index, second_index=priority_index
                        )
                    ],
                    step=len(states),
                    description=(
                        f"Compare the entry at index {current_index} with the "
                        f"higher-priority child at index {priority_index}."
                    ),
                    current_index=current_index,
                    compared_indices=(current_index, priority_index),
                )
            )

            if not self._has_priority(
                min_first, entries[priority_index], entries[current_index]
            ):
                break

            states.append(
                self._create_state(
                    entries=entries,
                    backing=backing,
                    min_priority_first=min_first,
                    events=[
                        SwapEntriesEvent(
                            first_index=current_index, second_index=priority_index
                        )
                    ],
                    step=len(states),
                    description=(
                        f"Swap the entries at index {current_index} "
                        f"and {priority_index} to restore the heap property."
                    ),
                    swapped_indices=(current_index, priority_index),
                )
            )

            entries_list = list(entries)
            entries_list[current_index], entries_list[priority_index] = (
                entries_list[priority_index],
                entries_list[current_index],
            )
            entries = tuple(entries_list)

            states.append(
                self._create_state(
                    entries=entries,
                    backing=backing,
                    min_priority_first=min_first,
                    events=[],
                    step=len(states),
                    description=f"Continue from index {priority_index}.",
                    current_index=priority_index,
                )
            )

            current_index = priority_index

        states.append(
            self._create_state(
                entries=entries,
                backing=backing,
                min_priority_first=min_first,
                events=[CompletePriorityQueueOperationEvent(operation="extract")],
                step=len(states),
                description=(
                    f"Extract operation is complete. Removed "
                    f"value={top_entry.value}, priority={top_entry.priority}."
                ),
            )
        )

        return PriorityQueueSimulation(
            states=tuple(states), operation=ExtractOperation()
        )

    def _extract_sorted_list(
        self,
        states: list[SimulationState],
        entries: tuple[PriorityEntry, ...],
        backing: PriorityBacking,
        min_first: bool,
        top_entry: PriorityEntry,
    ) -> PriorityQueueSimulation:
        states.append(
            self._create_state(
                entries=entries,
                backing=backing,
                min_priority_first=min_first,
                events=[
                    RemoveEntryEvent(
                        index=0, value=top_entry.value, priority=top_entry.priority
                    )
                ],
                step=len(states),
                description=(
                    "The highest-priority entry is always at index 0 for a "
                    "sorted list. Remove it directly."
                ),
                removed_index=0,
            )
        )

        entries = tuple(entries[1:])

        states.append(
            self._create_state(
                entries=entries,
                backing=backing,
                min_priority_first=min_first,
                events=[CompletePriorityQueueOperationEvent(operation="extract")],
                step=len(states),
                description=(
                    f"Extract operation is complete. Removed "
                    f"value={top_entry.value}, priority={top_entry.priority}. "
                    "No reshuffling is needed -- the remaining entries are "
                    "already sorted."
                ),
            )
        )

        return PriorityQueueSimulation(
            states=tuple(states), operation=ExtractOperation()
        )

    # ------------------------------------------------------------------
    # Peek (identical animation for either backing)
    # ------------------------------------------------------------------

    def peek(self) -> PriorityQueueSimulation:
        backing = self.model.backing
        min_first = self.model.min_priority_first

        states: list[SimulationState] = []
        entries = tuple(self.model.entries)

        states.append(
            self._create_state(
                entries=entries,
                backing=backing,
                min_priority_first=min_first,
                events=[],
                step=len(states),
                description="Initial state of the priority queue.",
            )
        )

        if not entries:
            states.append(
                self._create_state(
                    entries=entries,
                    backing=backing,
                    min_priority_first=min_first,
                    events=[
                        CompletePriorityQueueOperationEvent(operation="peek_empty")
                    ],
                    step=len(states),
                    description="The queue is empty. Nothing can be peeked.",
                )
            )

            return PriorityQueueSimulation(
                states=tuple(states), operation=PeekOperation()
            )

        top_entry = entries[0]

        states.append(
            self._create_state(
                entries=entries,
                backing=backing,
                min_priority_first=min_first,
                events=[],
                step=len(states),
                description=(
                    "The highest-priority entry is always at index 0, "
                    f"regardless of backing: value={top_entry.value}, "
                    f"priority={top_entry.priority}."
                ),
                current_index=0,
                peeked_index=0,
            )
        )

        states.append(
            self._create_state(
                entries=entries,
                backing=backing,
                min_priority_first=min_first,
                events=[CompletePriorityQueueOperationEvent(operation="peek")],
                step=len(states),
                description=(
                    f"Peek operation is complete. Highest priority is "
                    f"{top_entry.priority} (value={top_entry.value})."
                ),
            )
        )

        return PriorityQueueSimulation(
            states=tuple(states), operation=PeekOperation()
        )

    # ------------------------------------------------------------------
    # Shared helpers
    # ------------------------------------------------------------------

    def _has_priority(
        self, min_first: bool, first: PriorityEntry, second: PriorityEntry
    ) -> bool:
        """Return True when `first` should be served before `second`."""

        if min_first:
            return first.priority < second.priority

        return first.priority > second.priority

    def _create_state(
        self,
        entries: tuple[PriorityEntry, ...],
        backing: PriorityBacking,
        min_priority_first: bool,
        events: list[SimulationEvent],
        step: int,
        description: str,
        current_index: int | None = None,
        compared_indices: tuple[int, int] | None = None,
        swapped_indices: tuple[int, int] | None = None,
        created_index: int | None = None,
        removed_index: int | None = None,
        peeked_index: int | None = None,
    ) -> SimulationState:
        """Create a generic simulation state containing priority queue data."""

        data = PriorityQueueSimulationState(
            entries=entries,
            backing=backing,
            min_priority_first=min_priority_first,
            description=description,
            current_index=current_index,
            compared_indices=compared_indices,
            swapped_indices=swapped_indices,
            created_index=created_index,
            removed_index=removed_index,
            peeked_index=peeked_index,
        )

        return SimulationState(
            data=data,
            events=events,
            step=step,
        )