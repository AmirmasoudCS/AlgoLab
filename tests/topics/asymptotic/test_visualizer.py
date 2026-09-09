import pygame

from algolab.topics.asymptotic.model import AsymptoticModel
from algolab.topics.asymptotic.visualizer import AsymptoticVisualizer
from algolab.visualization.graph.layout import GraphLayout
from algolab.visualization.graph.scaling import LogarithmicScaling, LinearScaling


def test_visualizer_can_be_created():
    surface = pygame.Surface((1000, 700))
    model = AsymptoticModel()

    layout = GraphLayout(
        x=100,
        y=100,
        width=800,
        height=500,
    )

    visualizer = AsymptoticVisualizer(
        surface,
        model,
        layout,
        y_scaling=LinearScaling,
    )

    assert visualizer.surface is surface
    assert visualizer.model is model
    assert visualizer.layout is layout


def test_visualizer_uses_provided_scaling():
    surface = pygame.Surface((1000, 700))
    model = AsymptoticModel()

    layout = GraphLayout(
        x=100,
        y=100,
        width=800,
        height=500,
    )

    scaling = LinearScaling()

    visualizer = AsymptoticVisualizer(
        surface,
        model,
        layout,
        scaling,
    )

    assert visualizer.y_scaling is scaling


def test_visualizer_can_render():
    surface = pygame.Surface((1000, 700))
    model = AsymptoticModel()

    layout = GraphLayout(
        x=100,
        y=100,
        width=800,
        height=500,
    )

    visualizer = AsymptoticVisualizer(
        surface,
        model,
        layout,
        y_scaling=LinearScaling(),
    )

    visualizer.render()


def test_visualizer_can_render_without_visible_complexities():
    surface = pygame.Surface((1000, 700))
    model = AsymptoticModel()

    for complexity in model.complexities:
        model.set_visible(complexity, False)

    layout = GraphLayout(
        x=100,
        y=100,
        width=800,
        height=500,
    )

    visualizer = AsymptoticVisualizer(
        surface,
        model,
        layout,
        y_scaling=LinearScaling,
    )

    visualizer.render()

def test_visualizer_uses_linear_scaling_label():
    surface = pygame.Surface((1000, 700))
    model = AsymptoticModel()
    layout = GraphLayout(
        x=100,
        y=100,
        width=800,
        height=500,
    )

    visualizer = AsymptoticVisualizer(
        surface,
        model,
        layout,
        LinearScaling(),
    )

    assert visualizer._get_scaling_label() == "Linear"

def test_visualizer_uses_logarithmic_scaling_label():
    surface = pygame.Surface((1000, 700))
    model = AsymptoticModel()
    layout = GraphLayout(
        x=100,
        y=100,
        width=800,
        height=500,
    )

    visualizer = AsymptoticVisualizer(
        surface,
        model,
        layout,
        LogarithmicScaling(),
    )

    assert visualizer._get_scaling_label() == "Logarithmic"