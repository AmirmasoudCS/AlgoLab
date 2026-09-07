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


def test_logarithmic_scaling():
    scaling = LogarithmicScaling()

    assert scaling.scale(1) == 0
    assert scaling.scale(10) == 1
    assert scaling.scale(100) == 2


def test_logarithmic_scaling_matches_math():
    scaling = LogarithmicScaling()

    assert scaling.scale(50) == math.log10(50)


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