from algolab.simulation.history import SimulationHistory
from algolab.simulation.state import SimulationState


class Simulator:
    """Controls execution and navigation through a simulation."""

    def __init__(self) -> None:
        self.history = SimulationHistory()
        self.running = False

    @property
    def state(self) -> SimulationState | None:
        return self.history.current

    def start(self, initial_state: SimulationState) -> None:
        """Start a new simulation."""

        self.history.clear()
        self.history.add(initial_state)
        self.running = True

    def pause(self) -> None:
        """Pause the simulation."""
        self.running = False

    def resume(self) -> None:
        """Resume the simulation."""
        self.running = True

    def previous(self) -> SimulationState | None:
        """Move one step backward."""

        return self.history.previous()

    def next(self) -> SimulationState | None:
        """Move one step forward."""

        return self.history.next()

    def reset(self) -> None:
        """Reset the simulation."""

        self.history.clear()
        self.running = False