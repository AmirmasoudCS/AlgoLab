from __future__ import annotations

from dataclasses import dataclass

from algolab.simulation.events import SimulationEvent
from algolab.simulation.state import SimulationState
from algolab.topics.heap.model import Heap, HeapType
from algolab.topics.heap.operations import (
    BuildHeapOperation,
    ClearOperation,
    ExtractOperation,
    HeapOperation,
    InsertOperation,
    PeekOperation,
)


@dataclass(frozen=True)
class CompareHeapElementsEvent(SimulationEvent):
    """Indicates that two heap elements are being compared."""

    first_index: int
    second_index: int


@dataclass(frozen=True)
class SwapHeapElementsEvent(SimulationEvent):
    """Indicates that two heap elements are being swapped."""

    first_index: int
    second_index: int


@dataclass(frozen=True)
class CreateHeapElementEvent(SimulationEvent):
    """Indicates that a new heap element is being created."""

    index: int
    value: object


@dataclass(frozen=True)
class ExtractHeapElementEvent(SimulationEvent):
    """Indicates that the root element is being extracted."""

    index: int
    value: object


@dataclass(frozen=True)
class MoveLastElementEvent(SimulationEvent):
    """Indicates that the last element is moved to the root."""

    from_index: int
    to_index: int


@dataclass(frozen=True)
class CompleteHeapOperationEvent(SimulationEvent):
    """Indicates that a heap operation has completed."""

    operation: str


@dataclass(frozen=True)
class HeapSimulationState:
    """Represents the visual state of a heap simulation."""

    values: tuple[object, ...]
    description: str

    # Element currently being inspected.
    current_index: int | None = None

    # Parent/child pair currently being compared.
    compared_indices: tuple[int, int] | None = None

    # Pair of elements currently being swapped.
    swapped_indices: tuple[int, int] | None = None

    # Value currently being created.
    created_value: object | None = None

    # Value currently being extracted.
    extracted_value: object | None = None


@dataclass(frozen=True)
class HeapSimulation:
    """Represents a complete heap simulation."""

    states: tuple[SimulationState, ...]
    operation: HeapOperation

    def commit(self, model: Heap) -> object | None:
        """Commit the simulated operation to the heap model."""
        return self.operation.commit(model)


class HeapSimulator:
    """Creates step-by-step simulations for heap operations."""

    def __init__(self, model: Heap) -> None:
        self.model = model

    def insert(
        self,
        value: object,
    ) -> HeapSimulation:
        """Create a simulation for inserting a value."""

        states: list[SimulationState] = []

        values = self.model.values

        states.append(
            self._create_state(
                values=values,
                events=[],
                step=0,
                description="Initial state of the heap.",
            )
        )

        insertion_index = len(values)

        states.append(
            self._create_state(
                values=values,
                events=[
                    CreateHeapElementEvent(
                        index=insertion_index,
                        value=value,
                    )
                ],
                step=1,
                description=(
                    f"Create a new heap element containing {value}."
                ),
                current_index=insertion_index,
                created_value=value,
            )
        )

        values = [
            *values,
            value,
        ]

        states.append(
            self._create_state(
                values=values,
                events=[],
                step=2,
                description=(
                    f"Add {value} to the end of the heap array."
                ),
                current_index=insertion_index,
                created_value=value,
            )
        )

        current_index = insertion_index

        while current_index > 0:
            parent_index = (current_index - 1) // 2

            states.append(
                self._create_state(
                    values=values,
                    events=[
                        CompareHeapElementsEvent(
                            first_index=current_index,
                            second_index=parent_index,
                        )
                    ],
                    step=len(states),
                    description=(
                        f"Compare {values[current_index]} at index "
                        f"{current_index} with its parent "
                        f"{values[parent_index]} at index "
                        f"{parent_index}."
                    ),
                    current_index=current_index,
                    compared_indices=(
                        current_index,
                        parent_index,
                    ),
                )
            )

            if not self._has_priority(
                values[current_index],
                values[parent_index],
            ):
                states.append(
                    self._create_state(
                        values=values,
                        events=[
                            CompleteHeapOperationEvent(
                                operation="insert",
                            )
                        ],
                        step=len(states),
                        description=(
                            f"{values[current_index]} already satisfies "
                            "the heap property with its parent. "
                            "Insertion is complete."
                        ),
                    )
                )

                return HeapSimulation(
                    states=tuple(states),
                    operation=InsertOperation(value),
                )

            states.append(
                self._create_state(
                    values=values,
                    events=[
                        SwapHeapElementsEvent(
                            first_index=current_index,
                            second_index=parent_index,
                        )
                    ],
                    step=len(states),
                    description=(
                        f"Swap {values[current_index]} and "
                        f"{values[parent_index]} because the child "
                        "has higher priority."
                    ),
                    swapped_indices=(
                        current_index,
                        parent_index,
                    ),
                )
            )

            values[current_index], values[parent_index] = (
                values[parent_index],
                values[current_index],
            )

            states.append(
                self._create_state(
                    values=values,
                    events=[],
                    step=len(states),
                    description=(
                        f"After the swap, {values[parent_index]} "
                        f"moves to index {parent_index}."
                    ),
                    current_index=parent_index,
                )
            )

            current_index = parent_index

        states.append(
            self._create_state(
                values=values,
                events=[
                    CompleteHeapOperationEvent(
                        operation="insert",
                    )
                ],
                step=len(states),
                description=(
                    f"Insert operation is complete. "
                    f"Added {value} to the heap."
                ),
            )
        )

        return HeapSimulation(
            states=tuple(states),
            operation=InsertOperation(value),
        )

    def peek(self) -> HeapSimulation:
        """Create a simulation for peeking at the root."""

        states: list[SimulationState] = []

        values = self.model.values

        states.append(
            self._create_state(
                values=values,
                events=[],
                step=0,
                description="Initial state of the heap.",
                current_index=0 if values else None,
            )
        )

        if not values:
            states.append(
                self._create_state(
                    values=values,
                    events=[
                        CompleteHeapOperationEvent(
                            operation="peek_empty",
                        )
                    ],
                    step=1,
                    description=(
                        "The heap is empty. Nothing can be peeked."
                    ),
                )
            )

            return HeapSimulation(
                states=tuple(states),
                operation=PeekOperation(),
            )

        root_value = values[0]

        states.append(
            self._create_state(
                values=values,
                events=[
                    CompareHeapElementsEvent(
                        first_index=0,
                        second_index=0,
                    )
                ],
                step=1,
                description=(
                    f"Inspect the root element {root_value}. "
                    "The root has the highest priority in the heap."
                ),
                current_index=0,
                compared_indices=(0, 0),
            )
        )

        states.append(
            self._create_state(
                values=values,
                events=[
                    CompleteHeapOperationEvent(
                        operation="peek",
                    )
                ],
                step=2,
                description=(
                    f"Peek operation is complete. "
                    f"Root value is {root_value}."
                ),
                current_index=0,
            )
        )

        return HeapSimulation(
            states=tuple(states),
            operation=PeekOperation(),
        )

    def extract(self) -> HeapSimulation:
        """Create a simulation for extracting the root."""

        states: list[SimulationState] = []

        values = self.model.values

        states.append(
            self._create_state(
                values=values,
                events=[],
                step=0,
                description="Initial state of the heap.",
                current_index=0 if values else None,
            )
        )

        if not values:
            states.append(
                self._create_state(
                    values=values,
                    events=[
                        CompleteHeapOperationEvent(
                            operation="extract_empty",
                        )
                    ],
                    step=1,
                    description=(
                        "The heap is empty. Nothing can be extracted."
                    ),
                )
            )

            return HeapSimulation(
                states=tuple(states),
                operation=ExtractOperation(),
            )

        root_value = values[0]

        states.append(
            self._create_state(
                values=values,
                events=[
                    ExtractHeapElementEvent(
                        index=0,
                        value=root_value,
                    )
                ],
                step=1,
                description=(
                    f"Extract the root element containing "
                    f"{root_value}."
                ),
                current_index=0,
                extracted_value=root_value,
            )
        )

        if len(values) == 1:
            values = []

            states.append(
                self._create_state(
                    values=values,
                    events=[],
                    step=2,
                    description=(
                        "The heap contained only one element, "
                        "so the heap is now empty."
                    ),
                )
            )

            states.append(
                self._create_state(
                    values=values,
                    events=[
                        CompleteHeapOperationEvent(
                            operation="extract",
                        )
                    ],
                    step=3,
                    description=(
                        f"Extract operation is complete. "
                        f"Removed {root_value}."
                    ),
                )
            )

            return HeapSimulation(
                states=tuple(states),
                operation=ExtractOperation(),
            )

        last_index = len(values) - 1
        last_value = values[last_index]

        states.append(
            self._create_state(
                values=values,
                events=[
                    MoveLastElementEvent(
                        from_index=last_index,
                        to_index=0,
                    )
                ],
                step=2,
                description=(
                    f"Move the last element {last_value} "
                    "to the root position."
                ),
                current_index=0,
            )
        )

        values = [
            last_value,
            *values[1:-1],
        ]

        states.append(
            self._create_state(
                values=values,
                events=[],
                step=3,
                description=(
                    f"Place {last_value} at the root. "
                    "The heap property may now be violated."
                ),
                current_index=0,
            )
        )

        current_index = 0

        while True:
            left_index = 2 * current_index + 1
            right_index = 2 * current_index + 2

            if left_index >= len(values):
                break

            priority_index = left_index

            if (
                right_index < len(values)
                and self._has_priority(
                    values[right_index],
                    values[left_index],
                )
            ):
                priority_index = right_index

            states.append(
                self._create_state(
                    values=values,
                    events=[
                        CompareHeapElementsEvent(
                            first_index=current_index,
                            second_index=priority_index,
                        )
                    ],
                    step=len(states),
                    description=(
                        f"Compare {values[current_index]} at index "
                        f"{current_index} with the higher-priority "
                        f"child {values[priority_index]} at index "
                        f"{priority_index}."
                    ),
                    current_index=current_index,
                    compared_indices=(
                        current_index,
                        priority_index,
                    ),
                )
            )

            if not self._has_priority(
                values[priority_index],
                values[current_index],
            ):
                break

            states.append(
                self._create_state(
                    values=values,
                    events=[
                        SwapHeapElementsEvent(
                            first_index=current_index,
                            second_index=priority_index,
                        )
                    ],
                    step=len(states),
                    description=(
                        f"Swap {values[current_index]} and "
                        f"{values[priority_index]} to restore "
                        "the heap property."
                    ),
                    swapped_indices=(
                        current_index,
                        priority_index,
                    ),
                )
            )

            values[current_index], values[priority_index] = (
                values[priority_index],
                values[current_index],
            )

            states.append(
                self._create_state(
                    values=values,
                    events=[],
                    step=len(states),
                    description=(
                        f"After the swap, continue from index "
                        f"{priority_index}."
                    ),
                    current_index=priority_index,
                )
            )

            current_index = priority_index

        states.append(
            self._create_state(
                values=values,
                events=[
                    CompleteHeapOperationEvent(
                        operation="extract",
                    )
                ],
                step=len(states),
                description=(
                    f"Extract operation is complete. "
                    f"Removed {root_value}."
                ),
            )
        )

        return HeapSimulation(
            states=tuple(states),
            operation=ExtractOperation(),
        )

    def build_heap(
        self,
        values: list[object],
    ) -> HeapSimulation:
        """Create a simulation for building a heap."""

        states: list[SimulationState] = []

        current_values = values.copy()

        states.append(
            self._create_state(
                values=[],
                events=[],
                step=0,
                description="Initial state of the heap.",
            )
        )

        if not current_values:
            states.append(
                self._create_state(
                    values=[],
                    events=[
                        CompleteHeapOperationEvent(
                            operation="build_heap",
                        )
                    ],
                    step=1,
                    description=(
                        "Build heap operation is complete. "
                        "The heap is empty."
                    ),
                )
            )

            return HeapSimulation(
                states=tuple(states),
                operation=BuildHeapOperation(values),
            )

        states.append(
            self._create_state(
                values=current_values,
                events=[],
                step=1,
                description=(
                    "Place all input values into the heap array. "
                    "The array is not necessarily a valid heap yet."
                ),
            )
        )

        first_parent = len(current_values) // 2 - 1

        for start_index in range(
            first_parent,
            -1,
            -1,
        ):
            current_index = start_index

            states.append(
                self._create_state(
                    values=current_values,
                    events=[],
                    step=len(states),
                    description=(
                        f"Start heapifying the subtree rooted at "
                        f"index {start_index}, containing "
                        f"{current_values[start_index]}."
                    ),
                    current_index=start_index,
                )
            )

            while True:
                left_index = 2 * current_index + 1
                right_index = 2 * current_index + 2

                if left_index >= len(current_values):
                    break

                priority_index = left_index

                if (
                    right_index < len(current_values)
                    and self._has_priority(
                        current_values[right_index],
                        current_values[left_index],
                    )
                ):
                    priority_index = right_index

                states.append(
                    self._create_state(
                        values=current_values,
                        events=[
                            CompareHeapElementsEvent(
                                first_index=current_index,
                                second_index=priority_index,
                            )
                        ],
                        step=len(states),
                        description=(
                            f"Compare {current_values[current_index]} "
                            f"with its higher-priority child "
                            f"{current_values[priority_index]}."
                        ),
                        current_index=current_index,
                        compared_indices=(
                            current_index,
                            priority_index,
                        ),
                    )
                )

                if not self._has_priority(
                    current_values[priority_index],
                    current_values[current_index],
                ):
                    break

                states.append(
                    self._create_state(
                        values=current_values,
                        events=[
                            SwapHeapElementsEvent(
                                first_index=current_index,
                                second_index=priority_index,
                            )
                        ],
                        step=len(states),
                        description=(
                            f"Swap {current_values[current_index]} "
                            f"and {current_values[priority_index]} "
                            "to restore the heap property."
                        ),
                        swapped_indices=(
                            current_index,
                            priority_index,
                        ),
                    )
                )

                current_values[current_index], current_values[
                    priority_index
                ] = (
                    current_values[priority_index],
                    current_values[current_index],
                )

                states.append(
                    self._create_state(
                        values=current_values,
                        events=[],
                        step=len(states),
                        description=(
                            f"Continue heapifying from index "
                            f"{priority_index}."
                        ),
                        current_index=priority_index,
                    )
                )

                current_index = priority_index

        states.append(
            self._create_state(
                values=current_values,
                events=[
                    CompleteHeapOperationEvent(
                        operation="build_heap",
                    )
                ],
                step=len(states),
                description="Build heap operation is complete.",
            )
        )

        return HeapSimulation(
            states=tuple(states),
            operation=BuildHeapOperation(values),
        )

    def clear(self) -> HeapSimulation:
        """Create a simulation for clearing the heap."""

        states: list[SimulationState] = []

        values = self.model.values

        states.append(
            self._create_state(
                values=values,
                events=[],
                step=0,
                description="Initial state of the heap.",
            )
        )

        states.append(
            self._create_state(
                values=[],
                events=[
                    CompleteHeapOperationEvent(
                        operation="clear",
                    )
                ],
                step=1,
                description="Clear operation is complete. The heap is empty.",
            )
        )

        return HeapSimulation(
            states=tuple(states),
            operation=ClearOperation(),
        )

    def _create_state(
        self,
        values: list[object],
        events: list[SimulationEvent],
        step: int,
        description: str,
        current_index: int | None = None,
        compared_indices: tuple[int, int] | None = None,
        swapped_indices: tuple[int, int] | None = None,
        created_value: object | None = None,
        extracted_value: object | None = None,
    ) -> SimulationState:
        """Create a snapshot of the current simulation state."""

        data = HeapSimulationState(
            values=tuple(values),
            description=description,
            current_index=current_index,
            compared_indices=compared_indices,
            swapped_indices=swapped_indices,
            created_value=created_value,
            extracted_value=extracted_value,
        )

        return SimulationState(
            data=data,
            events=events,
            step=step,
        )

    def _has_priority(
        self,
        first: object,
        second: object,
    ) -> bool:
        """Return True when the first value has higher heap priority."""

        if self.model.heap_type is HeapType.MIN:
            return first < second

        return first > second