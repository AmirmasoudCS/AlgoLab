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