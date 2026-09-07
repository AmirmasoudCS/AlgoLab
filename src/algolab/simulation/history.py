from algolab.simulation.state import SimulationState


class SimulationHistory:
    """Stores simulation states for forward and backward navigation."""

    def __init__(self) -> None:
        self._states: list[SimulationState] = []
        self._current_index = -1

    @property
    def current(self) -> SimulationState | None:
        if self._current_index < 0:
            return None

        return self._states[self._current_index]

    @property
    def can_go_backward(self) -> bool:
        return self._current_index > 0

    @property
    def can_go_forward(self) -> bool:
        return self._current_index < len(self._states) - 1

    def add(self, state: SimulationState) -> None:
        """Add a new state to the history."""

        if self._current_index < len(self._states) - 1:
            self._states = self._states[: self._current_index + 1]

        self._states.append(state)
        self._current_index += 1

    def previous(self) -> SimulationState | None:
        """Move to the previous state."""

        if not self.can_go_backward:
            return self.current

        self._current_index -= 1
        return self.current

    def next(self) -> SimulationState | None:
        """Move to the next state."""

        if not self.can_go_forward:
            return self.current

        self._current_index += 1
        return self.current

    def clear(self) -> None:
        self._states.clear()
        self._current_index = -1