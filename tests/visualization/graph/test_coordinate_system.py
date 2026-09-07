import pytest

from algolab.visualization.graph.coordinate_system import (
    GraphCoordinateSystem,
)


@pytest.fixture
def graph():
    return GraphCoordinateSystem(
        x=100,
        y=100,
        width=800,
        height=500,
        x_min=0,
        x_max=10,
        y_min=0,
        y_max=100,
    )


def test_bottom_left_corner(graph):
    assert graph.to_screen(0, 0) == (100, 600)


def test_top_right_corner(graph):
    assert graph.to_screen(10, 100) == (900, 100)


def test_center(graph):
    assert graph.to_screen(5, 50) == (500, 350)


def test_x_axis_direction(graph):
    first_x, _ = graph.to_screen(0, 50)
    second_x, _ = graph.to_screen(10, 50)

    assert first_x == 100
    assert second_x == 900


def test_y_axis_is_inverted(graph):
    _, lower_y = graph.to_screen(5, 0)
    _, upper_y = graph.to_screen(5, 100)

    assert lower_y == 600
    assert upper_y == 100


def test_contains_inside_point(graph):
    assert graph.contains(5, 50) is True


def test_contains_boundary_points(graph):
    assert graph.contains(0, 0) is True
    assert graph.contains(10, 100) is True


def test_contains_outside_point(graph):
    assert graph.contains(-1, 50) is False
    assert graph.contains(11, 50) is False
    assert graph.contains(5, -1) is False
    assert graph.contains(5, 101) is False


def test_fractional_coordinates(graph):
    assert graph.to_screen(2.5, 25) == (300, 475)

from algolab.visualization.graph.coordinate_system import (
    GraphCoordinateSystem,
)
from algolab.visualization.graph.scaling import (
    LogarithmicScaling,
)


def test_coordinate_system_uses_y_scaling():
    graph = GraphCoordinateSystem(
        x=100,
        y=100,
        width=800,
        height=500,
        x_min=1,
        x_max=10,
        y_min=0,
        y_max=2,
        y_scaling=LogarithmicScaling(),
    )

    assert graph.to_screen(1, 1) == (100, 600)
    assert graph.to_screen(10, 100) == (900, 100)
    

def test_coordinate_system_defaults_to_linear_scaling():
    graph = GraphCoordinateSystem(
        x=100,
        y=100,
        width=800,
        height=500,
        x_min=0,
        x_max=10,
        y_min=0,
        y_max=100,
    )

    assert graph.to_screen(5, 50) == (500, 350)

from algolab.visualization.graph.coordinate_system import (
    GraphCoordinateSystem,
)
from algolab.visualization.graph.scaling import (
    LinearScaling,
    LogarithmicScaling,
)


def test_coordinate_system_converts_coordinates():
    graph = GraphCoordinateSystem(
        x=100,
        y=100,
        width=800,
        height=500,
        x_min=0,
        x_max=10,
        y_min=0,
        y_max=10,
    )

    assert graph.to_screen(0, 0) == (100, 600)
    assert graph.to_screen(10, 10) == (900, 100)
    assert graph.to_screen(5, 5) == (500, 350)


def test_coordinate_system_contains_point():
    graph = GraphCoordinateSystem(
        x=100,
        y=100,
        width=800,
        height=500,
        x_min=0,
        x_max=10,
        y_min=0,
        y_max=10,
    )

    assert graph.contains(5, 5)
    assert not graph.contains(11, 5)


def test_coordinate_system_supports_logarithmic_scaling():
    graph = GraphCoordinateSystem(
        x=100,
        y=100,
        width=800,
        height=500,
        x_min=1,
        x_max=10,
        y_min=1,
        y_max=100,
        y_scaling=LogarithmicScaling(),
    )

    assert graph.to_screen(1, 1) == (100, 600)
    assert graph.to_screen(10, 100) == (900, 100)
    assert graph.to_screen(10, 10) == (900, 350)