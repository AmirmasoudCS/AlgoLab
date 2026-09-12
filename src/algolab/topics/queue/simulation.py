from __future__ import annotations

from dataclasses import dataclass

from algolab.simulation.events import SimulationEvent
from algolab.simulation.state import SimulationState
from algolab.topics.queue.model import Queue
from algolab.topics.queue.operations import (
    DequeueOperation,
    EnqueueOperation,
    PeekOperation,
    QueueOperation,
)


@dataclass(frozen=True)
class EnqueueItemEvent(SimulationEvent):
    """Indicates that a new item is being created for an enqueue."""

    value: object


@dataclass(frozen=True)
class DequeueItemEvent(SimulationEvent):
    """Indicates that the front item is being removed."""

    value: object


@dataclass(frozen=True)
class PeekItemEvent(SimulationEvent):
    """Indicates that the front item is being inspected."""

    value: object


@dataclass(frozen=True)
class UpdateFrontEvent(SimulationEvent):
    """Indicates that the FRONT pointer has moved."""

    index: int | None


@dataclass(frozen=True)
class UpdateRearEvent(SimulationEvent):
    """Indicates that the REAR pointer has moved."""

    index: int | None


@dataclass(frozen=True)
class CompleteQueueOperationEvent(SimulationEvent):
    """Indicates that a queue operation has completed."""

    operation: str


@dataclass(frozen=True)
class QueueSimulationState:
    """Represents the visual state of a queue simulation."""

    values: tuple[object, ...]
    description: str

    # Index of the item currently pointed to by FRONT.
    # None means the queue is empty.
    front_index: int | None = None

    # Index of the item currently pointed to by REAR.
    # None means the queue is empty.
    rear_index: int | None = None

    # Item currently being created during ENQUEUE.
    created_value: object | None = None

    # Item currently being removed during DEQUEUE.
    removed_value: object | None = None

    # Item currently being inspected during PEEK.
    peeked_value: object | None = None


@dataclass(frozen=True)
class QueueSimulation:
    """Represents a complete queue simulation."""

    states: tuple[SimulationState, ...]
    operation: QueueOperation

    def commit(self, model: Queue) -> object | None:
        """Commit the simulated operation to the queue model."""
        return self.operation.commit(model)


class QueueSimulator:
    """Creates step-by-step simulations for queue operations."""

    def __init__(self, model: Queue) -> None:
        self.model = model

    def enqueue(self, value: object) -> QueueSimulation:
        """Create a simulation for enqueuing a value."""
        states: list[SimulationState] = []

        values = self.model.to_list()

        current_front_index = 0 if values else None
        current_rear_index = len(values) - 1 if values else None

        states.append(
            self._create_state(
                values=values,
                events=[],
                step=0,
                description="Initial state of the queue.",
                front_index=current_front_index,
                rear_index=current_rear_index,
            )
        )

        # The new item is created separately before entering the queue.
        states.append(
            self._create_state(
                values=values,
                events=[
                    EnqueueItemEvent(
                        value=value,
                    )
                ],
                step=1,
                description=(
                    f"Create a new item containing {value} "
                    "for the enqueue operation."
                ),
                front_index=current_front_index,
                rear_index=current_rear_index,
                created_value=value,
            )
        )

        new_values = values + [value]
        new_front_index = 0
        new_rear_index = len(new_values) - 1

        states.append(
            self._create_state(
                values=new_values,
                events=[],
                step=2,
                description=(
                    f"Add the new item containing {value} "
                    "to the rear of the queue."
                ),
                front_index=new_front_index,
                rear_index=current_rear_index,
            )
        )

        states.append(
            self._create_state(
                values=new_values,
                events=[
                    UpdateRearEvent(
                        index=new_rear_index,
                    )
                ],
                step=3,
                description="Move REAR to the newly enqueued item.",
                front_index=new_front_index,
                rear_index=new_rear_index,
            )
        )

        states.append(
            self._create_state(
                values=new_values,
                events=[
                    CompleteQueueOperationEvent(
                        operation="enqueue",
                    )
                ],
                step=4,
                description=(
                    f"Enqueue operation is complete. "
                    f"Added {value} to the rear."
                ),
                front_index=new_front_index,
                rear_index=new_rear_index,
            )
        )

        return QueueSimulation(
            states=tuple(states),
            operation=EnqueueOperation(value),
        )

    def dequeue(self) -> QueueSimulation:
        """Create a simulation for dequeuing the front value."""
        states: list[SimulationState] = []

        values = self.model.to_list()

        current_front_index = 0 if values else None
        current_rear_index = len(values) - 1 if values else None

        states.append(
            self._create_state(
                values=values,
                events=[],
                step=0,
                description="Initial state of the queue.",
                front_index=current_front_index,
                rear_index=current_rear_index,
            )
        )

        if not values:
            states.append(
                self._create_state(
                    values=values,
                    events=[
                        CompleteQueueOperationEvent(
                            operation="dequeue_empty",
                        )
                    ],
                    step=1,
                    description="The queue is empty. Nothing can be dequeued.",
                    front_index=None,
                    rear_index=None,
                )
            )

            return QueueSimulation(
                states=tuple(states),
                operation=DequeueOperation(),
            )

        removed_value = values[0]
        new_values = values[1:]

        new_front_index = 0 if new_values else None
        new_rear_index = len(new_values) - 1 if new_values else None

        # The removed item disappears from the queue immediately.
        states.append(
            self._create_state(
                values=new_values,
                events=[
                    DequeueItemEvent(
                        value=removed_value,
                    )
                ],
                step=1,
                description=(
                    f"Remove the front item containing {removed_value} "
                    "from the queue."
                ),
                front_index=new_front_index,
                rear_index=new_rear_index,
                removed_value=removed_value,
            )
        )

        states.append(
            self._create_state(
                values=new_values,
                events=[
                    UpdateFrontEvent(
                        index=new_front_index,
                    ),
                    UpdateRearEvent(
                        index=new_rear_index,
                    ),
                ],
                step=2,
                description=(
                    "Move FRONT to the next item after removing "
                    "the previous front."
                ),
                front_index=new_front_index,
                rear_index=new_rear_index,
            )
        )

        states.append(
            self._create_state(
                values=new_values,
                events=[
                    CompleteQueueOperationEvent(
                        operation="dequeue",
                    )
                ],
                step=3,
                description=(
                    f"Dequeue operation is complete. "
                    f"Removed {removed_value}."
                ),
                front_index=new_front_index,
                rear_index=new_rear_index,
            )
        )

        return QueueSimulation(
            states=tuple(states),
            operation=DequeueOperation(),
        )

    def peek(self) -> QueueSimulation:
        """Create a simulation for peeking at the front value."""
        states: list[SimulationState] = []

        values = self.model.to_list()

        current_front_index = 0 if values else None
        current_rear_index = len(values) - 1 if values else None

        states.append(
            self._create_state(
                values=values,
                events=[],
                step=0,
                description="Initial state of the queue.",
                front_index=current_front_index,
                rear_index=current_rear_index,
            )
        )

        if not values:
            states.append(
                self._create_state(
                    values=values,
                    events=[
                        CompleteQueueOperationEvent(
                            operation="peek_empty",
                        )
                    ],
                    step=1,
                    description="The queue is empty. Nothing can be peeked.",
                    front_index=None,
                    rear_index=None,
                )
            )

            return QueueSimulation(
                states=tuple(states),
                operation=PeekOperation(),
            )

        peeked_value = values[0]

        states.append(
            self._create_state(
                values=values,
                events=[
                    PeekItemEvent(
                        value=peeked_value,
                    )
                ],
                step=1,
                description=(
                    f"Inspect the front item containing "
                    f"{peeked_value} without removing it."
                ),
                front_index=current_front_index,
                rear_index=current_rear_index,
                peeked_value=peeked_value,
            )
        )

        states.append(
            self._create_state(
                values=values,
                events=[
                    CompleteQueueOperationEvent(
                        operation="peek",
                    )
                ],
                step=2,
                description=(
                    f"Peek operation is complete. "
                    f"The front value is {peeked_value}."
                ),
                front_index=current_front_index,
                rear_index=current_rear_index,
            )
        )

        return QueueSimulation(
            states=tuple(states),
            operation=PeekOperation(),
        )

    def _create_state(
        self,
        values: list[object],
        events: list[SimulationEvent],
        step: int,
        description: str,
        front_index: int | None,
        rear_index: int | None,
        created_value: object | None = None,
        removed_value: object | None = None,
        peeked_value: object | None = None,
    ) -> SimulationState:
        """Create a generic simulation state containing queue data."""
        data = QueueSimulationState(
            values=tuple(values),
            description=description,
            front_index=front_index,
            rear_index=rear_index,
            created_value=created_value,
            removed_value=removed_value,
            peeked_value=peeked_value,
        )

        return SimulationState(
            data=data,
            events=events,
            step=step,
        )