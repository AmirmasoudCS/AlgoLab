from dataclasses import dataclass
from copy import deepcopy

from algolab.simulation.events import SimulationEvent
from algolab.simulation.state import SimulationState
from algolab.topics.linked_list.model import LinkedListModel, Node


@dataclass(frozen=True)
class VisitNodeEvent(SimulationEvent):
    """Indicates that a node is currently being visited."""

    index: int


@dataclass(frozen=True)
class CreateNodeEvent(SimulationEvent):
    """Indicates that a new node is being created."""

    index: int
    data: object


@dataclass(frozen=True)
class UpdateLinkEvent(SimulationEvent):
    """Indicates that a node's next reference is being updated."""

    index: int
    next_index: int | None


@dataclass(frozen=True)
class DeleteNodeEvent(SimulationEvent):
    """Indicates that a node is being deleted."""

    index: int
    data: object


@dataclass(frozen=True)
class CompleteOperationEvent(SimulationEvent):
    """Indicates that a linked-list operation has completed."""

    operation: str


@dataclass
class LinkedListSimulationState:
    """Represents the visual state of a linked-list simulation."""

    values: list[object]
    current_index: int | None = None
    created_index: int | None = None
    deleted_index: int | None = None


class LinkedListSimulator:
    """Creates step-by-step simulations for linked-list operations."""

    def __init__(self, model: LinkedListModel) -> None:
        self.model = model

    def insert_at_beginning(
        self,
        data: object,
    ) -> list[SimulationState]:
        """Create a simulation for inserting a node at the beginning."""

        states: list[SimulationState] = []

        values = self.model.to_list()

        states.append(
            self._create_state(
                values=values,
                events=[],
                step=0,
            )
        )

        new_values = [data, *values]

        states.append(
            self._create_state(
                values=values,
                events=[
                    CreateNodeEvent(
                        index=0,
                        data=data,
                    )
                ],
                step=1,
                created_index=0,
            )
        )

        states.append(
            self._create_state(
                values=new_values,
                events=[
                    UpdateLinkEvent(
                        index=0,
                        next_index=1 if values else None,
                    )
                ],
                step=2,
            )
        )

        states.append(
            self._create_state(
                values=new_values,
                events=[
                    CompleteOperationEvent(
                        operation="insert_at_beginning",
                    )
                ],
                step=3,
            )
        )

        return states

    def insert_at_end(
        self,
        data: object,
    ) -> list[SimulationState]:
        """Create a simulation for inserting a node at the end."""

        states: list[SimulationState] = []

        values = self.model.to_list()

        states.append(
            self._create_state(
                values=values,
                events=[],
                step=0,
            )
        )

        for index in range(len(values)):
            states.append(
                self._create_state(
                    values=values,
                    events=[
                        VisitNodeEvent(index=index),
                    ],
                    step=len(states),
                    current_index=index,
                )
            )

        new_index = len(values)
        new_values = [*values, data]

        states.append(
            self._create_state(
                values=values,
                events=[
                    CreateNodeEvent(
                        index=new_index,
                        data=data,
                    )
                ],
                step=len(states),
                created_index=new_index,
            )
        )

        states.append(
            self._create_state(
                values=new_values,
                events=[
                    UpdateLinkEvent(
                        index=new_index - 1 if values else 0,
                        next_index=new_index if values else None,
                    )
                ],
                step=len(states),
            )
        )

        states.append(
            self._create_state(
                values=new_values,
                events=[
                    CompleteOperationEvent(
                        operation="insert_at_end",
                    )
                ],
                step=len(states),
            )
        )

        return states

    def insert_at(
        self,
        index: int,
        data: object,
    ) -> list[SimulationState]:
        """Create a simulation for inserting a node at an index."""

        if index < 0 or index > self.model.size:
            raise IndexError("Linked list index out of range.")

        if index == 0:
            return self.insert_at_beginning(data)

        states: list[SimulationState] = []

        values = self.model.to_list()

        states.append(
            self._create_state(
                values=values,
                events=[],
                step=0,
            )
        )

        for current_index in range(index):
            states.append(
                self._create_state(
                    values=values,
                    events=[
                        VisitNodeEvent(
                            index=current_index,
                        )
                    ],
                    step=len(states),
                    current_index=current_index,
                )
            )

        states.append(
            self._create_state(
                values=values,
                events=[
                    CreateNodeEvent(
                        index=index,
                        data=data,
                    )
                ],
                step=len(states),
                created_index=index,
            )
        )

        new_values = [
            *values[:index],
            data,
            *values[index:],
        ]

        states.append(
            self._create_state(
                values=new_values,
                events=[
                    UpdateLinkEvent(
                        index=index - 1,
                        next_index=index,
                    )
                ],
                step=len(states),
            )
        )

        states.append(
            self._create_state(
                values=new_values,
                events=[
                    CompleteOperationEvent(
                        operation="insert_at",
                    )
                ],
                step=len(states),
            )
        )

        return states

    def delete_at(
        self,
        index: int,
    ) -> list[SimulationState]:
        """Create a simulation for deleting a node at an index."""

        if index < 0 or index >= self.model.size:
            raise IndexError("Linked list index out of range.")

        states: list[SimulationState] = []

        values = self.model.to_list()

        states.append(
            self._create_state(
                values=values,
                events=[],
                step=0,
            )
        )

        for current_index in range(index + 1):
            states.append(
                self._create_state(
                    values=values,
                    events=[
                        VisitNodeEvent(
                            index=current_index,
                        )
                    ],
                    step=len(states),
                    current_index=current_index,
                )
            )

        states.append(
            self._create_state(
                values=values,
                events=[
                    DeleteNodeEvent(
                        index=index,
                        data=values[index],
                    )
                ],
                step=len(states),
                deleted_index=index,
            )
        )

        new_values = values[:index] + values[index + 1:]

        states.append(
            self._create_state(
                values=new_values,
                events=[
                    UpdateLinkEvent(
                        index=index - 1 if index > 0 else 0,
                        next_index=index if index < len(new_values) else None,
                    )
                ],
                step=len(states),
            )
        )

        states.append(
            self._create_state(
                values=new_values,
                events=[
                    CompleteOperationEvent(
                        operation="delete_at",
                    )
                ],
                step=len(states),
            )
        )

        return states

    def search(
        self,
        data: object,
    ) -> list[SimulationState]:
        """Create a simulation for searching for a value."""

        states: list[SimulationState] = []

        values = self.model.to_list()

        states.append(
            self._create_state(
                values=values,
                events=[],
                step=0,
            )
        )

        for index, value in enumerate(values):
            states.append(
                self._create_state(
                    values=values,
                    events=[
                        VisitNodeEvent(index=index),
                    ],
                    step=len(states),
                    current_index=index,
                )
            )

            if value == data:
                states.append(
                    self._create_state(
                        values=values,
                        events=[
                            CompleteOperationEvent(
                                operation="search_found",
                            )
                        ],
                        step=len(states),
                        current_index=index,
                    )
                )

                return states

        states.append(
            self._create_state(
                values=values,
                events=[
                    CompleteOperationEvent(
                        operation="search_not_found",
                    )
                ],
                step=len(states),
            )
        )

        return states

    def _create_state(
        self,
        values: list[object],
        events: list[SimulationEvent],
        step: int,
        current_index: int | None = None,
        created_index: int | None = None,
        deleted_index: int | None = None,
    ) -> SimulationState:
        """Create an immutable snapshot of the current simulation state."""

        data = LinkedListSimulationState(
            values=deepcopy(values),
            current_index=current_index,
            created_index=created_index,
            deleted_index=deleted_index,
        )

        return SimulationState(
            data=data,
            events=events,
            step=step,
        )