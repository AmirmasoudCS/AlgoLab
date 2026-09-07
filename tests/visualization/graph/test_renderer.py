import os

os.environ["SDL_VIDEODRIVER"] = "dummy"

import pygame
import pytest

from algolab.visualization.graph.coordinate_system import (
    GraphCoordinateSystem,
)
from algolab.visualization.graph.renderer import GraphRenderer


@pytest.fixture
def surface():
    pygame.init()

    surface = pygame.Surface((1000, 700))

    yield surface

    pygame.quit()


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
        y_max=10,
    )


@pytest.fixture
def renderer(surface, graph):
    return GraphRenderer(surface, graph)


def test_renderer_can_be_created(surface, graph):
    renderer = GraphRenderer(surface, graph)

    assert renderer.surface is surface
    assert renderer.coordinate_system is graph


def test_render_does_not_raise(renderer):
    renderer.render()


def test_render_draws_graph_background(surface, renderer, graph):
    surface.fill((0, 0, 0))

    renderer.render()

    pixel = surface.get_at((graph.x + 10, graph.y + 10))

    assert pixel[:3] == (245, 245, 245)


def test_render_draws_grid(surface, renderer, graph):
    surface.fill((0, 0, 0))

    renderer.render()

    x, y = graph.to_screen(5, 5)

    pixel = surface.get_at((x, y))

    assert pixel[:3] != (245, 245, 245)


def test_render_draws_axes(surface, renderer, graph):
    surface.fill((0, 0, 0))

    renderer.render()

    x_axis_x, x_axis_y = graph.to_screen(5, 0)
    y_axis_x, y_axis_y = graph.to_screen(0, 5)

    assert surface.get_at((x_axis_x, x_axis_y))[:3] == (30, 30, 30)
    assert surface.get_at((y_axis_x, y_axis_y))[:3] == (30, 30, 30)

def test_draw_curve_with_multiple_points():
    surface = pygame.Surface((1000, 700))

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

    renderer = GraphRenderer(surface, graph)

    renderer.draw_curve(
        [
            (0, 0),
            (5, 50),
            (10, 100),
        ]
    )

def test_draw_curve_with_insufficient_points():
    surface = pygame.Surface((1000, 700))

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

    renderer = GraphRenderer(surface, graph)

    renderer.draw_curve([])
    renderer.draw_curve([(5, 50)])

def test_renderer_can_render_large_bounds():
    surface = pygame.Surface((1000, 700))

    graph = GraphCoordinateSystem(
        x=100,
        y=100,
        width=800,
        height=500,
        x_min=1,
        x_max=10,
        y_min=1,
        y_max=10_000_000_000,
    )

    renderer = GraphRenderer(surface, graph)

    renderer.render()