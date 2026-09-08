import math

import pytest

from algolab.visualization.graph.scaling import (
    LinearScaling,
    LogarithmicScaling,
    NormalizedScaling,
)


def test_linear_scaling():
    scaling = LinearScaling()

    assert scaling.scale(10) == 10
    assert scaling.scale(100) == 100


def test_logarithmic_scaling_matches_math():
    scaling = LogarithmicScaling()

    assert scaling.scale(1) == math.log10(1)
    assert scaling.scale(10) == math.log10(10)
    assert scaling.scale(100) == math.log10(100)


def test_logarithmic_scaling_requires_positive_value():
    scaling = LogarithmicScaling()

    with pytest.raises(ValueError):
        scaling.scale(0)

    with pytest.raises(ValueError):
        scaling.scale(-10)


def test_normalized_scaling():
    scaling = NormalizedScaling(100)

    assert scaling.scale(0) == 0
    assert scaling.scale(25) == 0.25
    assert scaling.scale(50) == 0.5
    assert scaling.scale(100) == 1


def test_normalized_scaling_rejects_invalid_maximum():
    with pytest.raises(ValueError):
        NormalizedScaling(0)

    with pytest.raises(ValueError):
        NormalizedScaling(-100)

def test_linear_scaling_returns_evenly_spaced_ticks():
    scaling = LinearScaling()

    ticks = scaling.get_ticks(0, 100)

    assert len(ticks) == 11
    assert ticks[0] == 0
    assert ticks[-1] == 100


def test_linear_scaling_uses_integer_ticks_for_small_ranges():
    scaling = LinearScaling()

    ticks = scaling.get_ticks(1, 10)

    assert ticks == list(range(1, 11))
    

def test_logarithmic_scaling_returns_powers_of_ten():
    scaling = LogarithmicScaling()

    ticks = scaling.get_ticks(1, 10_000)

    assert ticks == [
        1,
        10,
        100,
        1_000,
        10_000,
    ]

def test_logarithmic_scaling_rejects_non_positive_minimum():
    scaling = LogarithmicScaling()

    with pytest.raises(ValueError):
        scaling.get_ticks(0, 100)