from algolab.simulation.state import SimulationState
from algolab.simulation.history import SimulationHistory


def make_state(value, step):
    return SimulationState(
        data=value,
        step=step,
    )


def test_history_starts_empty():
    history = SimulationHistory()

    assert history.current is None
    assert history.can_go_backward is False
    assert history.can_go_forward is False


def test_add_state():
    history = SimulationHistory()
    state = make_state([1, 2, 3], 0)

    history.add(state)

    assert history.current is state
    assert history.can_go_backward is False
    assert history.can_go_forward is False


def test_previous_and_next():
    history = SimulationHistory()

    state_0 = make_state([1, 2, 3], 0)
    state_1 = make_state([2, 1, 3], 1)
    state_2 = make_state([2, 3, 1], 2)

    history.add(state_0)
    history.add(state_1)
    history.add(state_2)

    assert history.current is state_2
    assert history.can_go_backward is True
    assert history.can_go_forward is False

    assert history.previous() is state_1
    assert history.previous() is state_0

    assert history.can_go_backward is False

    assert history.next() is state_1
    assert history.next() is state_2

    assert history.can_go_forward is False


def test_previous_at_beginning_does_not_move():
    history = SimulationHistory()

    state = make_state([1], 0)
    history.add(state)

    assert history.previous() is state
    assert history.current is state


def test_next_at_end_does_not_move():
    history = SimulationHistory()

    state = make_state([1], 0)
    history.add(state)

    assert history.next() is state
    assert history.current is state


def test_adding_after_going_backward_discards_future_states():
    history = SimulationHistory()

    state_0 = make_state([1], 0)
    state_1 = make_state([2], 1)
    state_2 = make_state([3], 2)
    new_state = make_state([4], 2)

    history.add(state_0)
    history.add(state_1)
    history.add(state_2)

    history.previous()

    history.add(new_state)

    assert history.current is new_state
    assert history.can_go_forward is False

    assert history.previous() is state_1


def test_clear():
    history = SimulationHistory()

    history.add(make_state([1], 0))
    history.add(make_state([2], 1))

    history.clear()

    assert history.current is None
    assert history.can_go_backward is False
    assert history.can_go_forward is False