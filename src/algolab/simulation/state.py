from dataclasses import dataclass, field
from typing import Any

from algolab.simulation.events import SimulationEvent


@dataclass
class SimulationState:
    """Represents the state of a simulation at a specific step."""

    data: Any
    events: list[SimulationEvent] = field(default_factory=list)
    step: int = 0