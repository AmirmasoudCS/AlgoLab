from __future__ import annotations

from dataclasses import dataclass

from algolab.simulation.events import SimulationEvent
from algolab.simulation.state import SimulationState
from algolab.topics.circular_queue.model import CircularQueue
from algolab.topics.circular_queue.operations import (
    CircularQueueOperation,
    DequeueOperation,
    EnqueueOperation,
    PeekOperation,
)


@dataclass(frozen=True)
class ActiveSlotEvent(SimulationEvent):
    """Indicates a slot is currently being inspected."""

    index: int


@dataclass(frozen=True)
class PlaceItemEvent(SimulationEvent):
    """Indicates a value is being written into a slot."""

    index: int
    value: object


@dataclass(frozen=True)
class RemoveItemEvent(SimulationEvent):
    """Indicates a slot's value is being removed."""

    index: int
    value: object


@dataclass(frozen=True)
class UpdateFrontEvent(SimulationEvent):
    """Indicates the FRONT pointer has moved to a new slot index."""

    index: int | None


@dataclass(frozen=True)
class UpdateRearEvent(SimulationEvent):
    """Indicates the REAR pointer has moved to a new slot index."""

    index: int | None


@dataclass(frozen=True)
class CompleteCircularQueueOperationEvent(SimulationEvent):
    """Indicates a circular queue operation has completed."""

    operation: str


@dataclass(frozen=True)
class CircularQueueSimulationState:
    """Represents the visual state of a circular queue simulation."""

    slots: tuple[object | None, ...]
    capacity: int
    description: str

    front_index: int | None = None
    rear_index: int | None = None

    # Slot currently being inspected (e.g. before placing/removing).
    active_index: int | None = None

    # Slot that just received a new value.
    created_index: int | None = None

    # Slot whose value was just removed.
    removed_index: int | None = None

    # Slot currently being inspected for PEEK.
    peeked_index: int | None = None


@dataclass(frozen=True)
class CircularQueueSimulation:
    """Represents a complete circular queue simulation."""

    states: tuple[SimulationState, ...]
    operation: CircularQueueOperation

    def commit(self, queue: CircularQueue) -> object | None:
        """Commit the simulated operation to the real circular queue."""
        return self.operation.commit(queue)


class CircularQueueSimulator:
    """Creates step-by-step simulations for circular queue operations."""

    def __init__(self, model: CircularQueue) -> None:
        self.model = model

    def enqueue(self, value: object) -> CircularQueueSimulation:
        """Create a simulation for enqueuing a value."""

        states: list[SimulationState] = []

        slots = self.model.slots_snapshot()
        capacity = self.model.capacity
        front_index = self.model.front_index
        rear_index = self.model.rear_index

        states.append(
            self._create_state(
                slots=slots,
                capacity=capacity,
                events=[],
                step=len(states),
                description="Initial state of the circular queue.",
                front_index=front_index,
                rear_index=rear_index,
            )
        )

        if self.model.is_full:
            states.append(
                self._create_state(
                    slots=slots,
                    capacity=capacity,
                    events=[
                        CompleteCircularQueueOperationEvent(
                            operation="enqueue_full",
                        )
                    ],
                    step=len(states),
                    description=(
                        f"The queue is full (capacity {capacity}). "
                        "Nothing can be enqueued until a slot is freed."
                    ),
                    front_index=front_index,
                    rear_index=rear_index,
                )
            )

            return CircularQueueSimulation(
                states=tuple(states),
                operation=EnqueueOperation(value),
            )

        insert_index = (
            (front_index + self.model.size) % capacity
            if front_index is not None
            else 0
        )

        states.append(
            self._create_state(
                slots=slots,
                capacity=capacity,
                events=[ActiveSlotEvent(index=insert_index)],
                step=len(states),
                description=(
                    f"Compute the next open slot: "
                    f"(front + size) % capacity = slot {insert_index}."
                ),
                front_index=front_index,
                rear_index=rear_index,
                active_index=insert_index,
            )
        )

        new_slots = list(slots)
        new_slots[insert_index] = value
        new_slots = tuple(new_slots)

        new_rear_index = insert_index
        new_front_index = front_index if front_index is not None else insert_index

        states.append(
            self._create_state(
                slots=new_slots,
                capacity=capacity,
                events=[PlaceItemEvent(index=insert_index, value=value)],
                step=len(states),
                description=f"Place {value} into slot {insert_index}.",
                front_index=new_front_index,
                rear_index=rear_index,
                created_index=insert_index,
            )
        )

        states.append(
            self._create_state(
                slots=new_slots,
                capacity=capacity,
                events=[UpdateRearEvent(index=new_rear_index)],
                step=len(states),
                description=f"Move REAR to slot {new_rear_index}.",
                front_index=new_front_index,
                rear_index=new_rear_index,
            )
        )

        states.append(
            self._create_state(
                slots=new_slots,
                capacity=capacity,
                events=[
                    CompleteCircularQueueOperationEvent(operation="enqueue")
                ],
                step=len(states),
                description=(
                    f"Enqueue operation is complete. Added {value} "
                    f"to slot {insert_index}."
                ),
                front_index=new_front_index,
                rear_index=new_rear_index,
            )
        )

        return CircularQueueSimulation(
            states=tuple(states),
            operation=EnqueueOperation(value),
        )

    def dequeue(self) -> CircularQueueSimulation:
        """Create a simulation for dequeuing the front value."""

        states: list[SimulationState] = []

        slots = self.model.slots_snapshot()
        capacity = self.model.capacity
        front_index = self.model.front_index
        rear_index = self.model.rear_index

        states.append(
            self._create_state(
                slots=slots,
                capacity=capacity,
                events=[],
                step=len(states),
                description="Initial state of the circular queue.",
                front_index=front_index,
                rear_index=rear_index,
            )
        )

        if self.model.is_empty:
            states.append(
                self._create_state(
                    slots=slots,
                    capacity=capacity,
                    events=[
                        CompleteCircularQueueOperationEvent(
                            operation="dequeue_empty",
                        )
                    ],
                    step=len(states),
                    description="The queue is empty. Nothing can be dequeued.",
                    front_index=None,
                    rear_index=None,
                )
            )

            return CircularQueueSimulation(
                states=tuple(states),
                operation=DequeueOperation(),
            )

        removed_value = slots[front_index]

        states.append(
            self._create_state(
                slots=slots,
                capacity=capacity,
                events=[ActiveSlotEvent(index=front_index)],
                step=len(states),
                description=f"Inspect the FRONT slot at index {front_index}.",
                front_index=front_index,
                rear_index=rear_index,
                active_index=front_index,
            )
        )

        cleared_slots = list(slots)
        cleared_slots[front_index] = None
        cleared_slots = tuple(cleared_slots)

        states.append(
            self._create_state(
                slots=cleared_slots,
                capacity=capacity,
                events=[
                    RemoveItemEvent(index=front_index, value=removed_value)
                ],
                step=len(states),
                description=f"Remove {removed_value} from slot {front_index}.",
                front_index=front_index,
                rear_index=rear_index,
                removed_index=front_index,
            )
        )

        new_size = self.model.size - 1
        new_front_index = (front_index + 1) % capacity if new_size > 0 else None
        new_rear_index = rear_index if new_size > 0 else None

        wrapped = new_front_index == 0 and front_index == capacity - 1

        if new_front_index is None:
            front_description = (
                "The queue is now empty, so FRONT and REAR are cleared."
            )
        elif wrapped:
            front_description = (
                f"Move FRONT to slot {new_front_index}, wrapping around "
                "from the end of the array back to the beginning -- this "
                "wraparound is the whole point of a circular queue."
            )
        else:
            front_description = f"Move FRONT to slot {new_front_index}."

        states.append(
            self._create_state(
                slots=cleared_slots,
                capacity=capacity,
                events=[UpdateFrontEvent(index=new_front_index)],
                step=len(states),
                description=front_description,
                front_index=new_front_index,
                rear_index=new_rear_index,
            )
        )

        states.append(
            self._create_state(
                slots=cleared_slots,
                capacity=capacity,
                events=[
                    CompleteCircularQueueOperationEvent(operation="dequeue")
                ],
                step=len(states),
                description=(
                    f"Dequeue operation is complete. Removed {removed_value}."
                ),
                front_index=new_front_index,
                rear_index=new_rear_index,
            )
        )

        return CircularQueueSimulation(
            states=tuple(states),
            operation=DequeueOperation(),
        )

    def peek(self) -> CircularQueueSimulation:
        """Create a simulation for peeking at the front value."""

        states: list[SimulationState] = []

        slots = self.model.slots_snapshot()
        capacity = self.model.capacity
        front_index = self.model.front_index
        rear_index = self.model.rear_index

        states.append(
            self._create_state(
                slots=slots,
                capacity=capacity,
                events=[],
                step=len(states),
                description="Initial state of the circular queue.",
                front_index=front_index,
                rear_index=rear_index,
            )
        )

        if self.model.is_empty:
            states.append(
                self._create_state(
                    slots=slots,
                    capacity=capacity,
                    events=[
                        CompleteCircularQueueOperationEvent(
                            operation="peek_empty",
                        )
                    ],
                    step=len(states),
                    description="The queue is empty. Nothing can be peeked.",
                    front_index=None,
                    rear_index=None,
                )
            )

            return CircularQueueSimulation(
                states=tuple(states),
                operation=PeekOperation(),
            )

        peeked_value = slots[front_index]

        states.append(
            self._create_state(
                slots=slots,
                capacity=capacity,
                events=[ActiveSlotEvent(index=front_index)],
                step=len(states),
                description=(
                    f"Inspect the FRONT slot at index {front_index} "
                    f"without removing it: {peeked_value}."
                ),
                front_index=front_index,
                rear_index=rear_index,
                peeked_index=front_index,
            )
        )

        states.append(
            self._create_state(
                slots=slots,
                capacity=capacity,
                events=[
                    CompleteCircularQueueOperationEvent(operation="peek")
                ],
                step=len(states),
                description=(
                    f"Peek operation is complete. "
                    f"The front value is {peeked_value}."
                ),
                front_index=front_index,
                rear_index=rear_index,
            )
        )

        return CircularQueueSimulation(
            states=tuple(states),
            operation=PeekOperation(),
        )

    def _create_state(
        self,
        slots: tuple[object | None, ...],
        capacity: int,
        events: list[SimulationEvent],
        step: int,
        description: str,
        front_index: int | None,
        rear_index: int | None,
        active_index: int | None = None,
        created_index: int | None = None,
        removed_index: int | None = None,
        peeked_index: int | None = None,
    ) -> SimulationState:
        """Create a generic simulation state containing circular queue data."""

        data = CircularQueueSimulationState(
            slots=slots,
            capacity=capacity,
            description=description,
            front_index=front_index,
            rear_index=rear_index,
            active_index=active_index,
            created_index=created_index,
            removed_index=removed_index,
            peeked_index=peeked_index,
        )

        return SimulationState(
            data=data,
            events=events,
            step=step,
        )