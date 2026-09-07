import math

from algolab.topics.asymptotic.complexity import (
    CONSTANT,
    LOGARITHMIC,
    LINEAR,
    LINEARITHMIC,
    QUADRATIC,
    CUBIC,
    EXPONENTIAL,
    N_TO_N,
)


def test_constant():
    assert CONSTANT.function(100) == 1


def test_logarithmic():
    assert LOGARITHMIC.function(100) == math.log2(100)


def test_linear():
    assert LINEAR.function(100) == 100


def test_linearithmic():
    assert LINEARITHMIC.function(100) == 100 * math.log2(100)


def test_quadratic():
    assert QUADRATIC.function(100) == 100**2


def test_cubic():
    assert CUBIC.function(100) == 100**3


def test_exponential():
    assert EXPONENTIAL.function(10) == 2**10


def test_n_to_n():
    assert N_TO_N.function(10) == 10**10