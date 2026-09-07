from algolab.simulation.events import CompareEvent
from algolab.simulation.state import SimulationState


def test_simulation_state_defaults():
    state = SimulationState(data=[1, 2, 3])

    assert state.data == [1, 2, 3]
    assert state.events == []
    assert state.step == 0


def test_simulation_state_stores_events():
    event = CompareEvent(0, 1)

    state = SimulationState(
        data=[2, 1],
        events=[event],
        step=1,
    )

    assert state.data == [2, 1]
    assert state.events == [event]
    assert state.step == 1