import pygame

from algolab.topics.asymptotic.model import AsymptoticModel
from algolab.topics.asymptotic.visualizer import AsymptoticVisualizer


def test_visualizer_can_be_created():
    surface = pygame.Surface((1000, 700))
    model = AsymptoticModel()

    visualizer = AsymptoticVisualizer(
        surface,
        model,
    )

    assert visualizer.surface is surface
    assert visualizer.model is model


def test_visualizer_can_render():
    surface = pygame.Surface((1000, 700))
    model = AsymptoticModel()

    visualizer = AsymptoticVisualizer(
        surface,
        model,
    )

    visualizer.render()


def test_visualizer_can_render_without_visible_complexities():
    surface = pygame.Surface((1000, 700))
    model = AsymptoticModel()

    for complexity in model.complexities:
        model.set_visible(complexity, False)

    visualizer = AsymptoticVisualizer(
        surface,
        model,
    )

    visualizer.render()