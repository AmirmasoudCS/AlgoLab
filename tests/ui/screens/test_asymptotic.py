import pygame

from algolab.ui.screens.asymptotic import AsymptoticScreen


def test_asymptotic_screen_can_render():
    surface = pygame.Surface((1280, 720))

    screen = AsymptoticScreen(surface)

    screen.render()