from dataclasses import dataclass

from algolab.simulation.events import SimulationEvent
from algolab.simulation.state import SimulationState
from algolab.topics.linked_list.model import LinkedListModel
from algolab.topics.linked_list.operations import (
    DeleteAtOperation,
    InsertAtBeginningOperation,
    InsertAtEndOperation,
    InsertAtOperation,
    LinkedListOperation,
    SearchOperation,
)


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
class UpdateHeadEvent(SimulationEvent):
    """Indicates that the head reference is being updated."""

    index: int | None


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


@dataclass(frozen=True)
class LinkedListSimulationState:
    """Represents the visual state of a linked-list simulation."""

    values: tuple[object, ...]
    description: str
    current_index: int | None = None
    created_index: int | None = None
    deleted_index: int | None = None


@dataclass(frozen=True)
class LinkedListSimulation:
    """Represents a complete linked-list simulation."""

    states: tuple[SimulationState, ...]
    operation: LinkedListOperation

    def commit(self, model: LinkedListModel) -> object | None:
        """Commit the simulated operation to the linked-list model."""

        return self.operation.commit(model)


class LinkedListSimulator:
    """Creates step-by-step simulations for linked-list operations."""

    def __init__(self, model: LinkedListModel) -> None:
        self.model = model

    def insert_at_beginning(
        self,
        data: object,
    ) -> LinkedListSimulation:
        """Create a simulation for inserting a node at the beginning."""

        states: list[SimulationState] = []

        values = self.model.to_list()
        new_values = [data, *values]

        states.append(
            self._create_state(
                values=values,
                events=[],
                step=0,
                description="Initial state of the linked list.",
            )
        )

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
                description=f"Create a new node containing {data}.",
                created_index=0,
            )
        )

        states.append(
            self._create_state(
                values=new_values,
                events=[
                    UpdateHeadEvent(
                        index=0,
                    )
                ],
                step=2,
                description=(
                    "Update HEAD to point to the new node. "
                    "The new node becomes the first node."
                ),
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
                description="Insertion at the beginning is complete.",
            )
        )

        return LinkedListSimulation(
            states=tuple(states),
            operation=InsertAtBeginningOperation(
                data=data,
            ),
        )

    def insert_at_end(
        self,
        data: object,
    ) -> LinkedListSimulation:
        """Create a simulation for inserting a node at the end."""

        states: list[SimulationState] = []

        values = self.model.to_list()

        states.append(
            self._create_state(
                values=values,
                events=[],
                step=0,
                description="Initial state of the linked list.",
            )
        )

        if not values:
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
                    description=f"Create a new node containing {data}.",
                    created_index=0,
                )
            )

            new_values = [data]

            states.append(
                self._create_state(
                    values=new_values,
                    events=[
                        UpdateHeadEvent(
                            index=0,
                        )
                    ],
                    step=2,
                    description=(
                        "The list is empty, so HEAD must point "
                        "to the new node."
                    ),
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
                    step=3,
                    description="Insertion at the end is complete.",
                )
            )

            return LinkedListSimulation(
                states=tuple(states),
                operation=InsertAtEndOperation(
                    data=data,
                ),
            )

        for index in range(len(values)):
            states.append(
                self._create_state(
                    values=values,
                    events=[
                        VisitNodeEvent(
                            index=index,
                        )
                    ],
                    step=len(states),
                    description=(
                        f"Visit node {index} containing "
                        f"{values[index]} and follow its next pointer."
                    ),
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
                description=f"Create a new node containing {data}.",
                created_index=new_index,
            )
        )

        states.append(
            self._create_state(
                values=new_values,
                events=[
                    UpdateLinkEvent(
                        index=new_index - 1,
                        next_index=new_index,
                    )
                ],
                step=len(states),
                description=(
                    f"Update node {new_index - 1}'s next pointer "
                    f"to point to the new node."
                ),
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
                description="Insertion at the end is complete.",
            )
        )

        return LinkedListSimulation(
            states=tuple(states),
            operation=InsertAtEndOperation(
                data=data,
            ),
        )

    def insert_at(
        self,
        index: int,
        data: object,
    ) -> LinkedListSimulation:
        """Create a simulation for inserting a node at an index."""

        if index < 0 or index > self.model.size:
            raise IndexError("Linked list index out of range.")

        if index == 0:
            return self.insert_at_beginning(data)

        if index == self.model.size:
            return self.insert_at_end(data)

        states: list[SimulationState] = []

        values = self.model.to_list()

        states.append(
            self._create_state(
                values=values,
                events=[],
                step=0,
                description="Initial state of the linked list.",
            )
        )

        for current_index in range(index):
            states.append(
                self._create_state(
                    values=values,
                    events=[
                        VisitNodeEvent(
                            index=current_index
                        )
                    ],
                    step=len(states),
                    description=(
                        f"Visit node {current_index} containing "
                        f"{values[current_index]}."
                    ),
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
                description=(
                    f"Create a new node containing {data} "
                    f"at index {index}."
                ),
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
                description=(
                    f"Update node {index - 1}'s next pointer "
                    f"to point to the new node."
                ),
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
                description=(
                    f"Insertion at index {index} is complete."
                ),
            )
        )

        return LinkedListSimulation(
            states=tuple(states),
            operation=InsertAtOperation(
                index=index,
                data=data,
            ),
        )

    def delete_at(
        self,
        index: int,
    ) -> LinkedListSimulation:
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
                description="Initial state of the linked list.",
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
                    description=(
                        f"Visit node {current_index} containing "
                        f"{values[current_index]}."
                    ),
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
                description=(
                    f"Delete node {index} containing "
                    f"{values[index]}."
                ),
                deleted_index=index,
            )
        )

        new_values = values[:index] + values[index + 1:]

        if index == 0:
            states.append(
                self._create_state(
                    values=new_values,
                    events=[
                        UpdateHeadEvent(
                            index=0 if new_values else None,
                        )
                    ],
                    step=len(states),
                    description=(
                        "Update HEAD to point to the next node."
                        if new_values
                        else "The node was the only node, so HEAD is now NULL."
                    ),
                )
            )
        else:
            states.append(
                self._create_state(
                    values=new_values,
                    events=[
                        UpdateLinkEvent(
                            index=index - 1,
                            next_index=(
                                index
                                if index < len(new_values)
                                else None
                            ),
                        )
                    ],
                    step=len(states),
                    description=(
                        f"Update node {index - 1}'s next pointer "
                        "to skip the deleted node."
                    ),
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
                description=(
                    f"Deletion of node {index} is complete."
                ),
            )
        )

        return LinkedListSimulation(
            states=tuple(states),
            operation=DeleteAtOperation(
                index=index,
            ),
        )

    def search(
        self,
        data: object,
    ) -> LinkedListSimulation:
        """Create a simulation for searching for a value."""

        states: list[SimulationState] = []

        values = self.model.to_list()

        states.append(
            self._create_state(
                values=values,
                events=[],
                step=0,
                description=(
                    f"Start searching for {data} "
                    "from the HEAD node."
                ),
            )
        )

        for index, value in enumerate(values):
            states.append(
                self._create_state(
                    values=values,
                    events=[
                        VisitNodeEvent(
                            index=index
                        )
                    ],
                    step=len(states),
                    description=(
                        f"Check node {index}: "
                        f"{value} == {data}?"
                    ),
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
                        description=(
                            f"Found {data} at index {index}."
                        ),
                        current_index=index,
                    )
                )

                return LinkedListSimulation(
                    states=tuple(states),
                    operation=SearchOperation(
                        data=data,
                    ),
                )

        states.append(
            self._create_state(
                values=values,
                events=[
                    CompleteOperationEvent(
                        operation="search_not_found",
                    )
                ],
                step=len(states),
                description=(
                    f"{data} was not found in the linked list."
                ),
            )
        )

        return LinkedListSimulation(
            states=tuple(states),
            operation=SearchOperation(
                data=data,
            )
        )

    def _create_state(
        self,
        values: list[object],
        events: list[SimulationEvent],
        step: int,
        description: str,
        current_index: int | None = None,
        created_index: int | None = None,
        deleted_index: int | None = None,
    ) -> SimulationState:
        """Create a snapshot of the current simulation state."""

        data = LinkedListSimulationState(
            values=tuple(values),
            description=description,
            current_index=current_index,
            created_index=created_index,
            deleted_index=deleted_index,
        )

        return SimulationState(
            data=data,
            events=events,
            step=step,
        )