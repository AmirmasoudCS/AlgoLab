from dataclasses import dataclass


@dataclass(frozen=True)
class SimulationEvent:
    """Base class for events produced during a simulation."""

    pass


@dataclass(frozen=True)
class CompareEvent(SimulationEvent):
    """Indicates that two elements are being compared."""

    first_index: int
    second_index: int


@dataclass(frozen=True)
class SwapEvent(SimulationEvent):
    """Indicates that two elements should be swapped."""

    first_index: int
    second_index: int


@dataclass(frozen=True)
class MarkSortedEvent(SimulationEvent):
    """Indicates that an element has reached its final position."""

    index: int


@dataclass(frozen=True)
class UpdatePointerEvent(SimulationEvent):
    """Indicates that an algorithmic pointer moved to a node."""

    name: str
    index: int | None


@dataclass(frozen=True)
class VisitNodeEvent(SimulationEvent):
    """Indicates that a linked-list node is being visited."""

    index: int


@dataclass(frozen=True)
class CreateNodeEvent(SimulationEvent):
    """Indicates that a new linked-list node is being created."""

    index: int
    data: object


@dataclass(frozen=True)
class UpdateHeadEvent(SimulationEvent):
    """Indicates that HEAD now points to a node."""

    index: int | None


@dataclass(frozen=True)
class UpdateLinkEvent(SimulationEvent):
    """Indicates that a node's NEXT link was updated."""

    index: int
    next_index: int | None


@dataclass(frozen=True)
class DeleteNodeEvent(SimulationEvent):
    """Indicates that a linked-list node is being deleted."""

    index: int
    data: object


@dataclass(frozen=True)
class CompleteOperationEvent(SimulationEvent):
    """Indicates that an operation has completed."""

    operation: str