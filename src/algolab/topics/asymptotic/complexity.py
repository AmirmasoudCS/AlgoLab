import math
from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class ComplexityFunction:
    """Represents a mathematical complexity function."""

    name: str
    notation: str
    description: str
    function: Callable[[float], float]


CONSTANT = ComplexityFunction(
    name="Constant",
    notation="O(1)",
    description="The running time does not depend on the input size.",
    function=lambda n: 1,
)

LOGARITHMIC = ComplexityFunction(
    name="Logarithmic",
    notation="O(log n)",
    description="The running time grows logarithmically with the input size.",
    function=lambda n: math.log2(n),
)

LINEAR = ComplexityFunction(
    name="Linear",
    notation="O(n)",
    description="The running time grows proportionally with the input size.",
    function=lambda n: n,
)

LINEARITHMIC = ComplexityFunction(
    name="Linearithmic",
    notation="O(n log n)",
    description="The running time grows as n multiplied by log n.",
    function=lambda n: n * math.log2(n),
)

QUADRATIC = ComplexityFunction(
    name="Quadratic",
    notation="O(n²)",
    description="The running time grows proportionally to the square of the input size.",
    function=lambda n: n**2,
)

CUBIC = ComplexityFunction(
    name="Cubic",
    notation="O(n³)",
    description="The running time grows proportionally to the cube of the input size.",
    function=lambda n: n**3,
)

EXPONENTIAL = ComplexityFunction(
    name="Exponential",
    notation="O(2ⁿ)",
    description="The running time doubles as the input size increases by one.",
    function=lambda n: 2**n,
)

N_TO_N = ComplexityFunction(
    name="n to the n",
    notation="O(nⁿ)",
    description="The running time grows as n raised to the power of n.",
    function=lambda n: n**n,
)