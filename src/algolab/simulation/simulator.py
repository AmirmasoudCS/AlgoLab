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

    @property
    def can_go_backward(self) -> bool:
        return self.history.can_go_backward

    @property
    def can_go_forward(self) -> bool:
        return self.history.can_go_forward

    @property
    def is_at_end(self) -> bool:
        """Return whether the simulation is at its final state."""

        return (
            self.state is not None
            and not self.history.can_go_forward
        )

    def start(self, initial_state: SimulationState) -> None:
        """Start a simulation from an initial state."""

        self.history.clear()
        self.history.add(initial_state)
        self.running = True

    def load_states(self, states: list[SimulationState]) -> None:
        """Load a complete sequence of simulation states."""

        if not states:
            raise ValueError("At least one simulation state is required.")

        self.history.clear()

        for state in states:
            self.history.add(state)

        self.history.previous_to_start()
        self.running = True

    def pause(self) -> None:
        self.running = False

    def resume(self) -> None:
        self.running = True

    def previous(self) -> SimulationState | None:
        return self.history.previous()

    def next(self) -> SimulationState | None:
        return self.history.next()

    def reset(self) -> None:
        self.history.clear()
        self.running = False