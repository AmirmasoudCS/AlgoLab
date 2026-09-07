import pygame

from algolab.ui.screens.main_menu import MainMenuScreen


def test_main_menu_can_render():
    surface = pygame.Surface((1280, 720))

    screen = MainMenuScreen(surface)

    screen.render()


def test_main_menu_can_handle_event():
    surface = pygame.Surface((1280, 720))

    screen = MainMenuScreen(surface)

    event = pygame.event.Event(pygame.KEYDOWN)

    screen.handle_event(event)


def test_main_menu_can_update():
    surface = pygame.Surface((1280, 720))

    screen = MainMenuScreen(surface)

    screen.update(0.016)