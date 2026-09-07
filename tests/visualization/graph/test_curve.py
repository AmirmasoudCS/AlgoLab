import pytest

from algolab.visualization.graph.curve import CurveGenerator


def test_generate_curve():
    generator = CurveGenerator()

    points = generator.generate(
        lambda x: x**2,
        0,
        10,
        samples=3,
    )

    assert points == [
        (0, 0),
        (5, 25),
        (10, 100),
    ]


def test_generate_curve_with_different_sample_count():
    generator = CurveGenerator()

    points = generator.generate(
        lambda x: x,
        0,
        10,
        samples=11,
    )

    assert len(points) == 11


def test_generate_curve_includes_range_boundaries():
    generator = CurveGenerator()

    points = generator.generate(
        lambda x: x,
        5,
        20,
        samples=5,
    )

    assert points[0][0] == 5
    assert points[-1][0] == 20


def test_generate_curve_uses_evenly_spaced_x_values():
    generator = CurveGenerator()

    points = generator.generate(
        lambda x: x,
        0,
        10,
        samples=5,
    )

    assert [point[0] for point in points] == [
        0,
        2.5,
        5,
        7.5,
        10,
    ]


def test_generate_curve_requires_at_least_two_samples():
    generator = CurveGenerator()

    with pytest.raises(ValueError):
        generator.generate(
            lambda x: x,
            0,
            10,
            samples=1,
        )


def test_generate_curve_rejects_invalid_range():
    generator = CurveGenerator()

    with pytest.raises(ValueError):
        generator.generate(
            lambda x: x,
            10,
            0,
        )


def test_generate_curve_rejects_equal_range():
    generator = CurveGenerator()

    with pytest.raises(ValueError):
        generator.generate(
            lambda x: x,
            10,
            10,
        )