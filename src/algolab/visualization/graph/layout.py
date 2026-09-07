from dataclasses import dataclass


@dataclass(frozen=True)
class GraphLayout:
    """Defines the position and dimensions of a graph."""

    x: int
    y: int
    width: int
    height: int