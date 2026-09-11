import pytest

from algolab.simulation.events import (
    CompareEvent,
    MarkSortedEvent,
    SimulationEvent,
    SwapEvent,
)


def test_simulation_event_is_base_event():
    event = SimulationEvent()

    assert isinstance(event, SimulationEvent)


def test_compare_event():
    event = CompareEvent(2, 5)

    assert event.first_index == 2
    assert event.second_index == 5
    assert isinstance(event, SimulationEvent)


def test_swap_event():
    event = SwapEvent(1, 4)

    assert event.first_index == 1
    assert event.second_index == 4
    assert isinstance(event, SimulationEvent)


def test_mark_sorted_event():
    event = MarkSortedEvent(3)

    assert event.index == 3
    assert isinstance(event, SimulationEvent)


def test_events_are_immutable():
    event = CompareEvent(1, 2)

    with pytest.raises(AttributeError):
        event.first_index = 5