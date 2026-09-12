from __future__ import annotations

from dataclasses import dataclass

from algolab.simulation.events import SimulationEvent
from algolab.simulation.state import SimulationState
from algolab.topics.stack.model import Stack
from algolab.topics.stack.operations import (
    PeekOperation,
    PopOperation,
    PushOperation,
    StackOperation,
)


@dataclass(frozen=True)
class PushItemEvent(SimulationEvent):
    """Indicates that a new item is being created for a push."""

    value: object


@dataclass(frozen=True)
class PopItemEvent(SimulationEvent):
    """Indicates that the top item is being removed."""

    value: object


@dataclass(frozen=True)
class PeekItemEvent(SimulationEvent):
    """Indicates that the top item is being inspected."""

    value: object


@dataclass(frozen=True)
class UpdateTopEvent(SimulationEvent):
    """Indicates that the TOP pointer has moved."""

    index: int | None


@dataclass(frozen=True)
class CompleteStackOperationEvent(SimulationEvent):
    """Indicates that a stack operation has completed."""

    operation: str


@dataclass(frozen=True)
class StackSimulationState:
    """Represents the visual state of a stack simulation."""

    values: tuple[object, ...]
    description: str

    # Index of the item currently pointed to by TOP.
    # None means the stack is empty.
    top_index: int | None = None

    # Item currently being created during PUSH.
    created_value: object | None = None

    # Item currently being removed during POP.
    removed_value: object | None = None

    # Item currently being inspected during PEEK.
    peeked_value: object | None = None


@dataclass(frozen=True)
class StackSimulation:
    """Represents a complete stack simulation."""

    states: tuple[SimulationState, ...]
    operation: StackOperation

    def commit(self, model: Stack) -> object | None:
        """Commit the simulated operation to the stack model."""
        return self.operation.commit(model)


class StackSimulator:
    """Creates step-by-step simulations for stack operations."""

    def __init__(self, model: Stack) -> None:
        self.model = model

    def push(self, value: object) -> StackSimulation:
        """Create a simulation for pushing a value onto the stack."""

        states: list[SimulationState] = []

        values = self.model.to_list()

        current_top_index = len(values) - 1 if values else None

        states.append(
            self._create_state(
                values=values,
                events=[],
                step=0,
                description="Initial state of the stack.",
                top_index=current_top_index,
            )
        )

        states.append(
            self._create_state(
                values=values,
                events=[
                    PushItemEvent(
                        value=value,
                    )
                ],
                step=1,
                description=f"Create a new stack item containing {value}.",
                top_index=current_top_index,
                created_value=value,
            )
        )

        new_values = [*values, value]
        new_top_index = len(new_values) - 1

        states.append(
            self._create_state(
                values=new_values,
                events=[
                    UpdateTopEvent(
                        index=new_top_index,
                    )
                ],
                step=2,
                description=(
                    f"Push {value} onto the stack and move TOP "
                    "to the new top item."
                ),
                top_index=new_top_index,
            )
        )

        states.append(
            self._create_state(
                values=new_values,
                events=[
                    CompleteStackOperationEvent(
                        operation="push",
                    )
                ],
                step=3,
                description="Push operation is complete.",
                top_index=new_top_index,
            )
        )

        return StackSimulation(
            states=tuple(states),
            operation=PushOperation(value),
        )

    def pop(self) -> StackSimulation:
        """Create a simulation for popping the top value."""

        states: list[SimulationState] = []

        values = self.model.to_list()
        current_top_index = len(values) - 1 if values else None

        states.append(
            self._create_state(
                values=values,
                events=[],
                step=0,
                description="Initial state of the stack.",
                top_index=current_top_index,
            )
        )

        if not values:
            states.append(
                self._create_state(
                    values=values,
                    events=[
                        CompleteStackOperationEvent(
                            operation="pop_empty",
                        )
                    ],
                    step=1,
                    description="The stack is empty. Nothing can be popped.",
                    top_index=None,
                )
            )

            return StackSimulation(
                states=tuple(states),
                operation=PopOperation(),
            )

        removed_value = values[-1]

        states.append(
            self._create_state(
                values=values,
                events=[
                    PopItemEvent(
                        value=removed_value,
                    )
                ],
                step=1,
                description=(
                    f"Remove the top item containing {removed_value} "
                    "from the stack."
                ),
                top_index=current_top_index,
                removed_value=removed_value,
            )
        )

        new_values = values[:-1]
        new_top_index = len(new_values) - 1 if new_values else None

        states.append(
            self._create_state(
                values=new_values,
                events=[
                    UpdateTopEvent(
                        index=new_top_index,
                    )
                ],
                step=2,
                description=(
                    "Move TOP to the new top item after removing "
                    "the previous top."
                ),
                top_index=new_top_index,
            )
        )

        states.append(
            self._create_state(
                values=new_values,
                events=[
                    CompleteStackOperationEvent(
                        operation="pop",
                    )
                ],
                step=3,
                description=f"Pop operation is complete. Removed {removed_value}.",
                top_index=new_top_index,
            )
        )

        return StackSimulation(
            states=tuple(states),
            operation=PopOperation(),
        )

    def peek(self) -> StackSimulation:
        """Create a simulation for peeking at the top value."""

        states: list[SimulationState] = []

        values = self.model.to_list()
        current_top_index = len(values) - 1 if values else None

        states.append(
            self._create_state(
                values=values,
                events=[],
                step=0,
                description="Initial state of the stack.",
                top_index=current_top_index,
            )
        )

        if not values:
            states.append(
                self._create_state(
                    values=values,
                    events=[
                        CompleteStackOperationEvent(
                            operation="peek_empty",
                        )
                    ],
                    step=1,
                    description="The stack is empty. Nothing can be peeked.",
                    top_index=None,
                )
            )

            return StackSimulation(
                states=tuple(states),
                operation=PeekOperation(),
            )

        top_value = values[-1]

        states.append(
            self._create_state(
                values=values,
                events=[
                    PeekItemEvent(
                        value=top_value,
                    )
                ],
                step=1,
                description=(
                    f"TOP points to {top_value}. Inspect the top item "
                    "without removing it."
                ),
                top_index=current_top_index,
                peeked_value=top_value,
            )
        )

        states.append(
            self._create_state(
                values=values,
                events=[
                    CompleteStackOperationEvent(
                        operation="peek",
                    )
                ],
                step=2,
                description=f"Peek operation is complete. Top value is {top_value}.",
                top_index=current_top_index,
            )
        )

        return StackSimulation(
            states=tuple(states),
            operation=PeekOperation(),
        )

    def _create_state(
        self,
        values: list[object],
        events: list[SimulationEvent],
        step: int,
        description: str,
        top_index: int | None = None,
        created_value: object | None = None,
        removed_value: object | None = None,
        peeked_value: object | None = None,
    ) -> SimulationState:
        """Create a snapshot of the current simulation state."""

        data = StackSimulationState(
            values=tuple(values),
            description=description,
            top_index=top_index,
            created_value=created_value,
            removed_value=removed_value,
            peeked_value=peeked_value,
        )

        return SimulationState(
            data=data,
            events=events,
            step=step,
        )