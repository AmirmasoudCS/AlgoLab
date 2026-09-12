import pygame

from algolab.ui.screens.asymptotic import AsymptoticScreen
from algolab.ui.screens.main_menu import MainMenuScreen
from algolab.ui.screens.screen_manager import ScreenManager


pygame.init()


def create_screen():
    surface = pygame.Surface((1280, 720))
    screen_manager = ScreenManager()

    screen = MainMenuScreen(
        surface,
        screen_manager,
    )

    return surface, screen_manager, screen


def test_main_menu_can_render():
    _, _, screen = create_screen()

    screen.render()


def test_main_menu_can_handle_event():
    _, _, screen = create_screen()

    event = pygame.event.Event(
        pygame.KEYDOWN
    )

    screen.handle_event(event)


def test_main_menu_can_update():
    _, _, screen = create_screen()

    screen.update(0.016)


def test_main_menu_starts_with_no_active_screen():
    _, screen_manager, _ = create_screen()

    assert screen_manager.current_screen is None


def test_clicking_asymptotic_notation_opens_asymptotic_screen():
    _, screen_manager, screen = create_screen()

    rect, enabled = screen.button_rects[0]

    assert enabled is True

    event = pygame.event.Event(
        pygame.MOUSEBUTTONDOWN,
        {
            "button": 1,
            "pos": rect.center,
        },
    )

    screen.handle_event(event)

    assert isinstance(
        screen_manager.current_screen,
        AsymptoticScreen,
    )


def test_clicking_disabled_queue_does_nothing():
    _, screen_manager, screen = create_screen()

    rect, enabled = screen.button_rects[3]

    assert enabled is False

    event = pygame.event.Event(
        pygame.MOUSEBUTTONDOWN,
        {
            "button": 1,
            "pos": rect.center,
        },
    )

    screen.handle_event(event)

    assert screen_manager.current_screen is None