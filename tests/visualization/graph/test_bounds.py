import pytest

from algolab.visualization.graph.bounds import BoundsCalculator


def test_calculate_y_bounds():
    calculator = BoundsCalculator()

    curves = [
        [(0, 1), (5, 5), (10, 10)],
        [(0, 2), (5, 8), (10, 20)],
    ]

    assert calculator.calculate_y_bounds(curves) == (1, 20)


def test_calculate_y_bounds_with_negative_values():
    calculator = BoundsCalculator()

    curves = [
        [(0, -5), (5, 0), (10, 5)],
        [(0, -10), (5, 2), (10, 8)],
    ]

    assert calculator.calculate_y_bounds(curves) == (-10, 8)


def test_calculate_y_bounds_with_single_curve():
    calculator = BoundsCalculator()

    curves = [
        [(0, 1), (5, 4), (10, 9)],
    ]

    assert calculator.calculate_y_bounds(curves) == (1, 9)


def test_calculate_y_bounds_rejects_empty_curves():
    calculator = BoundsCalculator()

    with pytest.raises(ValueError):
        calculator.calculate_y_bounds([])


def test_calculate_y_bounds_rejects_curves_without_points():
    calculator = BoundsCalculator()

    with pytest.raises(ValueError):
        calculator.calculate_y_bounds([[]])