import math

import pytest

from algolab.topics.asymptotic.complexity import (
    COMPLEXITIES,
    CONSTANT,
    LOGARITHMIC,
    LINEAR,
    LINEARITHMIC,
    QUADRATIC,
    CUBIC,
    EXPONENTIAL,
    N_TO_N,
)


def test_all_complexities_are_registered():
    assert len(COMPLEXITIES) == 8

    assert CONSTANT in COMPLEXITIES
    assert LOGARITHMIC in COMPLEXITIES
    assert LINEAR in COMPLEXITIES
    assert LINEARITHMIC in COMPLEXITIES
    assert QUADRATIC in COMPLEXITIES
    assert CUBIC in COMPLEXITIES
    assert EXPONENTIAL in COMPLEXITIES
    assert N_TO_N in COMPLEXITIES


@pytest.mark.parametrize(
    ("complexity", "expected"),
    [
        (CONSTANT, 1),
        (LOGARITHMIC, math.log2(100)),
        (LINEAR, 100),
        (LINEARITHMIC, 100 * math.log2(100)),
        (QUADRATIC, 100**2),
        (CUBIC, 100**3),
        (EXPONENTIAL, 2**10),
        (N_TO_N, 10**10),
    ],
)
def test_complexity_functions(complexity, expected):
    assert complexity.function(100 if complexity != EXPONENTIAL and complexity != N_TO_N else 10) == expected