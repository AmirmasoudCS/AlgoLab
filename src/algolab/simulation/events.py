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
