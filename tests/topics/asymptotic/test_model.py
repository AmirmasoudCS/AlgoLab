import pytest

from algolab.topics.asymptotic.complexity import (
    COMPLEXITIES,
    LINEAR,
    QUADRATIC,
)

from algolab.topics.asymptotic.model import AsymptoticModel


def test_model_initial_state():
    model = AsymptoticModel()

    assert model.complexities == COMPLEXITIES
    assert model.visible_complexities == list(COMPLEXITIES)
    assert model.selected_complexity is COMPLEXITIES[0]

    assert model.minimum_input == 1
    assert model.maximum_input == 10


def test_select_complexity():
    model = AsymptoticModel()

    model.select_complexity(QUADRATIC)

    assert model.selected_complexity is QUADRATIC


def test_select_unknown_complexity():
    model = AsymptoticModel()

    with pytest.raises(ValueError):
        model.select_complexity(object())


def test_hide_complexity():
    model = AsymptoticModel()

    model.set_visible(LINEAR, False)

    assert LINEAR not in model.visible_complexities


def test_show_complexity():
    model = AsymptoticModel()

    model.set_visible(LINEAR, False)
    model.set_visible(LINEAR, True)

    assert LINEAR in model.visible_complexities


def test_showing_already_visible_complexity_does_not_duplicate_it():
    model = AsymptoticModel()

    model.set_visible(LINEAR, True)

    assert model.visible_complexities.count(LINEAR) == 1


def test_hiding_already_hidden_complexity_is_safe():
    model = AsymptoticModel()

    model.set_visible(LINEAR, False)
    model.set_visible(LINEAR, False)

    assert LINEAR not in model.visible_complexities


def test_set_visible_rejects_unknown_complexity():
    model = AsymptoticModel()

    with pytest.raises(ValueError):
        model.set_visible(object(), True)


def test_set_input_range():
    model = AsymptoticModel()

    model.set_input_range(5, 100)

    assert model.minimum_input == 5
    assert model.maximum_input == 100


def test_minimum_input_must_be_at_least_one():
    model = AsymptoticModel()

    with pytest.raises(ValueError):
        model.set_input_range(0, 10)


def test_maximum_must_be_greater_than_minimum():
    model = AsymptoticModel()

    with pytest.raises(ValueError):
        model.set_input_range(10, 10)

    with pytest.raises(ValueError):
        model.set_input_range(20, 10)