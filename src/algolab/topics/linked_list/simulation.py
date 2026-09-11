from dataclasses import dataclass

from algolab.simulation.events import (
    CompleteOperationEvent,
    CreateNodeEvent,
    DeleteNodeEvent,
    SimulationEvent,
    UpdateHeadEvent,
    UpdateLinkEvent,
    UpdatePointerEvent,
    VisitNodeEvent,
)
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
class LinkedListSimulationState:
    """State used to visualize a linked-list simulation."""

    values: tuple[object, ...]
    description: str
    current_index: int | None = None
    created_index: int | None = None
    created_data: object | None = None
    deleted_index: int | None = None


@dataclass(frozen=True)
class LinkedListSimulation:
    """Collection of states representing one linked-list operation."""

    states: tuple[SimulationState, ...]
    operation: LinkedListOperation

    def commit(self, model: LinkedListModel) -> object | None:
        """Apply the simulated operation to the real model."""

        return self.operation.commit(model)


class LinkedListSimulator:
    """Creates step-by-step simulations for linked-list operations."""

    def __init__(self, model: LinkedListModel) -> None:
        self.model = model

    def insert_at_beginning(self, data: object) -> LinkedListSimulation:
        """Simulate inserting a new node at the beginning."""

        values = tuple(self.model.to_list())
        new_index = 0

        states: list[SimulationState] = []

        states.append(
            self._create_state(
                values=values,
                events=[],
                step=0,
                description="Start: prepare to insert a new node at the beginning.",
            )
        )

        states.append(
            self._create_state(
                values=values,
                events=[
                    CreateNodeEvent(
                        index=new_index,
                        data=data,
                    ),
                    UpdatePointerEvent(
                        name="new",
                        index=new_index,
                    ),
                ],
                step=1,
                description="Create the new node and let NEW point to it.",
                created_index=new_index,
                created_data=data,
            )
        )

        new_values = (data,) + values

        states.append(
            self._create_state(
                values=new_values,
                events=[
                    UpdatePointerEvent(
                        name="new",
                        index=0,
                    ),
                    UpdateHeadEvent(index=0),
                ],
                step=2,
                description="Set HEAD to the new node. The old chain remains connected.",
                current_index=0,
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
                description="Insertion complete.",
            )
        )

        return LinkedListSimulation(
            states=tuple(states),
            operation=InsertAtBeginningOperation(data=data),
        )

    def insert_at_end(self, data: object) -> LinkedListSimulation:
        """Simulate inserting a new node at the end."""

        values = tuple(self.model.to_list())
        states: list[SimulationState] = []

        if not values:
            states.append(
                self._create_state(
                    values=values,
                    events=[],
                    step=0,
                    description="Start: the linked list is empty.",
                )
            )

            states.append(
                self._create_state(
                    values=values,
                    events=[
                        CreateNodeEvent(
                            index=0,
                            data=data,
                        ),
                        UpdatePointerEvent(
                            name="new",
                            index=0,
                        ),
                    ],
                    step=1,
                    description="Create the new node and let NEW point to it.",
                    created_index=0,
                    created_data=data,
                )
            )

            new_values = (data,)

            states.append(
                self._create_state(
                    values=new_values,
                    events=[
                        UpdatePointerEvent(
                            name="new",
                            index=0,
                        ),
                        UpdateHeadEvent(index=0),
                    ],
                    step=2,
                    description="Because the list was empty, HEAD now points to NEW.",
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
                    description="Insertion complete.",
                )
            )

            return LinkedListSimulation(
                states=tuple(states),
                operation=InsertAtEndOperation(data=data),
            )

        # Start with both traversal pointers at the head.
        states.append(
            self._create_state(
                values=values,
                events=[
                    UpdatePointerEvent(
                        name="previous",
                        index=None,
                    ),
                    UpdatePointerEvent(
                        name="current",
                        index=0,
                    ),
                ],
                step=0,
                description="Start at HEAD. CURRENT points to the first node.",
                current_index=0,
            )
        )

        step = 1

        # Move CURRENT through the list.
        for index in range(len(values)):
            if index > 0:
                states.append(
                    self._create_state(
                        values=values,
                        events=[
                            UpdatePointerEvent(
                                name="previous",
                                index=index - 1,
                            ),
                            UpdatePointerEvent(
                                name="current",
                                index=index,
                            ),
                            VisitNodeEvent(index=index),
                        ],
                        step=step,
                        description=(
                            f"Move PREVIOUS to node {index - 1} "
                            f"and CURRENT to node {index}."
                        ),
                        current_index=index,
                    )
                )
                step += 1

        new_index = len(values)

        states.append(
            self._create_state(
                values=values,
                events=[
                    CreateNodeEvent(
                        index=new_index,
                        data=data,
                    ),
                    UpdatePointerEvent(
                        name="new",
                        index=new_index,
                    ),
                ],
                step=step,
                description="Create the new node. NEW points to the new node.",
                created_index=new_index,
                created_data=data,
            )
        )
        step += 1

        states.append(
            self._create_state(
                values=values,
                events=[
                    UpdatePointerEvent(
                        name="new",
                        index=new_index,
                    ),
                    UpdateLinkEvent(
                        index=len(values) - 1,
                        next_index=new_index,
                    ),
                ],
                step=step,
                description=(
                    f"Set node {len(values) - 1}.next to NEW. "
                    "The new node is now connected to the chain."
                ),
                created_index=new_index,
                created_data=data,
            )
        )
        step += 1

        new_values = values + (data,)

        states.append(
            self._create_state(
                values=new_values,
                events=[
                    CompleteOperationEvent(
                        operation="insert_at_end",
                    )
                ],
                step=step,
                description="Insertion complete.",
            )
        )

        return LinkedListSimulation(
            states=tuple(states),
            operation=InsertAtEndOperation(data=data),
        )

    def insert_at(
        self,
        index: int,
        data: object,
    ) -> LinkedListSimulation:
        """Simulate inserting a new node at a specific index."""

        values = tuple(self.model.to_list())

        if not 0 <= index <= len(values):
            raise IndexError("Linked-list insertion index out of range.")

        if index == 0:
            return self.insert_at_beginning(data)

        if index == len(values):
            return self.insert_at_end(data)

        states: list[SimulationState] = []

        states.append(
            self._create_state(
                values=values,
                events=[
                    UpdatePointerEvent(
                        name="previous",
                        index=None,
                    ),
                    UpdatePointerEvent(
                        name="current",
                        index=0,
                    ),
                ],
                step=0,
                description=(
                    f"Start traversal to insert at index {index}. "
                    "CURRENT begins at HEAD."
                ),
                current_index=0,
            )
        )

        step = 1

        # Traverse until:
        # previous -> node index - 1
        # current  -> node index
        for current_index in range(1, index + 1):
            previous_index = current_index - 1

            states.append(
                self._create_state(
                    values=values,
                    events=[
                        UpdatePointerEvent(
                            name="previous",
                            index=previous_index,
                        ),
                        UpdatePointerEvent(
                            name="current",
                            index=current_index,
                        ),
                        VisitNodeEvent(
                            index=current_index,
                        ),
                    ],
                    step=step,
                    description=(
                        f"Move PREVIOUS to node {previous_index} "
                        f"and CURRENT to node {current_index}."
                    ),
                    current_index=current_index,
                )
            )

            step += 1

        new_index = index

        states.append(
            self._create_state(
                values=values,
                events=[
                    CreateNodeEvent(
                        index=new_index,
                        data=data,
                    ),
                    UpdatePointerEvent(
                        name="new",
                        index=new_index,
                    ),
                ],
                step=step,
                description=(
                    f"Create the new node at index {new_index}. "
                    "NEW points to it."
                ),
                created_index=new_index,
                created_data=data,
            )
        )
        step += 1

        states.append(
            self._create_state(
                values=values,
                events=[
                    UpdatePointerEvent(
                        name="new",
                        index=new_index,
                    ),
                    UpdateLinkEvent(
                        index=new_index,
                        next_index=index,
                    ),
                ],
                step=step,
                description=(
                    f"Set NEW.next to CURRENT (node {index}). "
                    "The remainder of the chain is preserved."
                ),
                created_index=new_index,
                created_data=data,
                current_index=index,
            )
        )
        step += 1

        states.append(
            self._create_state(
                values=values,
                events=[
                    UpdatePointerEvent(
                        name="previous",
                        index=index - 1,
                    ),
                    UpdatePointerEvent(
                        name="new",
                        index=new_index,
                    ),
                    UpdateLinkEvent(
                        index=index - 1,
                        next_index=new_index,
                    ),
                ],
                step=step,
                description=(
                    f"Set node {index - 1}.next to NEW. "
                    "The new node is now inserted between PREVIOUS and CURRENT."
                ),
                created_index=new_index,
                created_data=data,
                current_index=index,
            )
        )
        step += 1

        new_values = (
            values[:index]
            + (data,)
            + values[index:]
        )

        states.append(
            self._create_state(
                values=new_values,
                events=[
                    CompleteOperationEvent(
                        operation="insert_at",
                    )
                ],
                step=step,
                description="Insertion complete.",
            )
        )

        return LinkedListSimulation(
            states=tuple(states),
            operation=InsertAtOperation(
                index=index,
                data=data,
            ),
        )

    def delete_at(self, index: int) -> LinkedListSimulation:
        """Simulate deleting a node at a specific index."""

        values = tuple(self.model.to_list())

        if not 0 <= index < len(values):
            raise IndexError("Linked-list deletion index out of range.")

        states: list[SimulationState] = []

        if index == 0:
            states.append(
                self._create_state(
                    values=values,
                    events=[
                        UpdatePointerEvent(
                            name="current",
                            index=0,
                        )
                    ],
                    step=0,
                    description="CURRENT points to HEAD, the node that will be deleted.",
                    current_index=0,
                )
            )

            states.append(
                self._create_state(
                    values=values,
                    events=[
                        DeleteNodeEvent(
                            index=0,
                            data=values[0],
                        )
                    ],
                    step=1,
                    description="Mark the HEAD node for deletion.",
                    deleted_index=0,
                )
            )

            new_values = values[1:]

            states.append(
                self._create_state(
                    values=new_values,
                    events=[
                        UpdateHeadEvent(
                            index=0 if new_values else None,
                        )
                    ],
                    step=2,
                    description=(
                        "Move HEAD to the next node. "
                        "The deleted node is no longer part of the chain."
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
                    step=3,
                    description="Deletion complete.",
                )
            )

            return LinkedListSimulation(
                states=tuple(states),
                operation=DeleteAtOperation(index=index),
            )

        states.append(
            self._create_state(
                values=values,
                events=[
                    UpdatePointerEvent(
                        name="previous",
                        index=None,
                    ),
                    UpdatePointerEvent(
                        name="current",
                        index=0,
                    ),
                ],
                step=0,
                description=(
                    f"Start traversal to delete node {index}. "
                    "CURRENT begins at HEAD."
                ),
                current_index=0,
            )
        )

        step = 1

        for current_index in range(1, index + 1):
            previous_index = current_index - 1

            states.append(
                self._create_state(
                    values=values,
                    events=[
                        UpdatePointerEvent(
                            name="previous",
                            index=previous_index,
                        ),
                        UpdatePointerEvent(
                            name="current",
                            index=current_index,
                        ),
                        VisitNodeEvent(
                            index=current_index,
                        ),
                    ],
                    step=step,
                    description=(
                        f"Move PREVIOUS to node {previous_index} "
                        f"and CURRENT to node {current_index}."
                    ),
                    current_index=current_index,
                )
            )

            step += 1

        states.append(
            self._create_state(
                values=values,
                events=[
                    DeleteNodeEvent(
                        index=index,
                        data=values[index],
                    )
                ],
                step=step,
                description=(
                    f"CURRENT points to node {index}. "
                    "This is the node that will be removed."
                ),
                current_index=index,
                deleted_index=index,
            )
        )
        step += 1

        new_values = (
            values[:index]
            + values[index + 1:]
        )

        next_index = index if index < len(new_values) else None

        states.append(
            self._create_state(
                values=new_values,
                events=[
                    UpdateLinkEvent(
                        index=index - 1,
                        next_index=next_index,
                    )
                ],
                step=step,
                description=(
                    f"Set PREVIOUS.next to "
                    f"{'CURRENT.next' if next_index is not None else 'NULL'}. "
                    "The deleted node is bypassed."
                ),
                deleted_index=index,
            )
        )
        step += 1

        states.append(
            self._create_state(
                values=new_values,
                events=[
                    CompleteOperationEvent(
                        operation="delete_at",
                    )
                ],
                step=step,
                description="Deletion complete.",
            )
        )

        return LinkedListSimulation(
            states=tuple(states),
            operation=DeleteAtOperation(index=index),
        )

    def search(self, data: object) -> LinkedListSimulation:
        """Simulate searching for a value in the linked list."""

        values = tuple(self.model.to_list())
        states: list[SimulationState] = []

        states.append(
            self._create_state(
                values=values,
                events=[
                    UpdatePointerEvent(
                        name="current",
                        index=None,
                    )
                ],
                step=0,
                description=f"Search for {data!r}. CURRENT starts before the list.",
            )
        )

        for index, value in enumerate(values):
            states.append(
                self._create_state(
                    values=values,
                    events=[
                        UpdatePointerEvent(
                            name="current",
                            index=index,
                        ),
                        VisitNodeEvent(
                            index=index,
                        ),
                    ],
                    step=index + 1,
                    description=(
                        f"CURRENT points to node {index}. "
                        f"Compare its value {value!r} with {data!r}."
                    ),
                    current_index=index,
                )
            )

            if value == data:
                states.append(
                    self._create_state(
                        values=values,
                        events=[
                            UpdatePointerEvent(
                                name="current",
                                index=index,
                            ),
                            CompleteOperationEvent(
                                operation="search_found",
                            ),
                        ],
                        step=index + 2,
                        description=(
                            f"Found {data!r} at node {index}."
                        ),
                        current_index=index,
                    )
                )

                return LinkedListSimulation(
                    states=tuple(states),
                    operation=SearchOperation(data=data),
                )

        states.append(
            self._create_state(
                values=values,
                events=[
                    UpdatePointerEvent(
                        name="current",
                        index=None,
                    ),
                    CompleteOperationEvent(
                        operation="search_not_found",
                    ),
                ],
                step=len(values) + 1,
                description=f"{data!r} was not found in the linked list.",
            )
        )

        return LinkedListSimulation(
            states=tuple(states),
            operation=SearchOperation(data=data),
        )

    def _create_state(
        self,
        values: tuple[object, ...],
        events: list[SimulationEvent],
        step: int,
        description: str,
        current_index: int | None = None,
        created_index: int | None = None,
        created_data: object | None = None,
        deleted_index: int | None = None,
    ) -> SimulationState:
        """Create a generic simulation state."""

        return SimulationState(
            data=LinkedListSimulationState(
                values=values,
                description=description,
                current_index=current_index,
                created_index=created_index,
                created_data=created_data,
                deleted_index=deleted_index,
            ),
            events=events,
            step=step,
        )