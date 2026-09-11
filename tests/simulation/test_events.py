import pytest

from algolab.simulation.simulator import Simulator
from algolab.simulation.state import SimulationState


def make_state(value, step=0):
    return SimulationState(
        data=value,
        step=step,
    )


def create_states() -> list[SimulationState]:
    return [
        SimulationState(data="A", step=0),
        SimulationState(data="B", step=1),
        SimulationState(data="C", step=2),
    ]


def test_simulator_starts_not_running():
    simulator = Simulator()

    assert simulator.running is False
    assert simulator.state is None


def test_start():
    simulator = Simulator()
    state = make_state([1, 2, 3])

    simulator.start(state)

    assert simulator.running is True
    assert simulator.state is state


def test_pause():
    simulator = Simulator()
    simulator.start(make_state([1]))

    simulator.pause()

    assert simulator.running is False


def test_resume():
    simulator = Simulator()
    simulator.start(make_state([1]))
    simulator.pause()

    simulator.resume()

    assert simulator.running is True


def test_navigation():
    simulator = Simulator()

    state_0 = make_state([1], 0)
    state_1 = make_state([2], 1)
    state_2 = make_state([3], 2)

    simulator.start(state_0)
    simulator.history.add(state_1)
    simulator.history.add(state_2)

    assert simulator.state is state_2

    assert simulator.previous() is state_1
    assert simulator.previous() is state_0

    assert simulator.next() is state_1


def test_reset():
    simulator = Simulator()
    simulator.start(make_state([1]))

    simulator.reset()

    assert simulator.state is None
    assert simulator.running is False


def test_load_states_starts_at_first_state():
    simulator = Simulator()
    states = create_states()

    simulator.load_states(states)

    assert simulator.state is states[0]


def test_load_states_moves_forward():
    simulator = Simulator()
    states = create_states()

    simulator.load_states(states)

    assert simulator.next() is states[1]
    assert simulator.next() is states[2]


def test_load_states_moves_backward():
    simulator = Simulator()
    states = create_states()

    simulator.load_states(states)

    simulator.next()
    simulator.next()

    assert simulator.previous() is states[1]
    assert simulator.previous() is states[0]


def test_load_states_cannot_move_beyond_last_state():
    simulator = Simulator()
    states = create_states()

    simulator.load_states(states)

    simulator.next()
    simulator.next()

    assert simulator.next() is states[-1]
    assert simulator.state is states[-1]


def test_load_states_cannot_move_before_first_state():
    simulator = Simulator()
    states = create_states()

    simulator.load_states(states)

    assert simulator.previous() is states[0]
    assert simulator.state is states[0]


def test_load_states_is_running_after_load():
    simulator = Simulator()

    simulator.load_states(create_states())

    assert simulator.running is True


def test_load_states_can_pause_and_resume():
    simulator = Simulator()

    simulator.load_states(create_states())

    simulator.pause()
    assert simulator.running is False

    simulator.resume()
    assert simulator.running is True


def test_load_states_rejects_empty_list():
    simulator = Simulator()

    with pytest.raises(ValueError):
        simulator.load_states([])
