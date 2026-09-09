import pygame

from algolab.ui.components.checkbox import Checkbox


def test_checkbox_can_be_created():
    rect = pygame.Rect(100, 100, 20, 20)

    checkbox = Checkbox(
        rect,
        "O(n)",
    )

    assert checkbox.rect == rect
    assert checkbox.label == "O(n)"
    assert checkbox.checked is False


def test_checkbox_can_start_checked():
    rect = pygame.Rect(100, 100, 20, 20)

    checkbox = Checkbox(
        rect,
        "O(n)",
        checked=True,
    )

    assert checkbox.checked is True


def test_checkbox_toggles_when_clicked():
    rect = pygame.Rect(100, 100, 20, 20)

    checkbox = Checkbox(
        rect,
        "O(n)",
    )

    event = pygame.event.Event(
        pygame.MOUSEBUTTONDOWN,
        {
            "button": 1,
            "pos": (110, 110),
        },
    )

    checkbox.handle_event(event)

    assert checkbox.checked is True

    checkbox.handle_event(event)

    assert checkbox.checked is False


def test_checkbox_does_not_toggle_when_clicked_outside():
    rect = pygame.Rect(100, 100, 20, 20)

    checkbox = Checkbox(
        rect,
        "O(n)",
    )

    event = pygame.event.Event(
        pygame.MOUSEBUTTONDOWN,
        {
            "button": 1,
            "pos": (200, 200),
        },
    )

    checkbox.handle_event(event)

    assert checkbox.checked is False


def test_checkbox_ignores_non_left_click():
    rect = pygame.Rect(100, 100, 20, 20)

    checkbox = Checkbox(
        rect,
        "O(n)",
    )

    event = pygame.event.Event(
        pygame.MOUSEBUTTONDOWN,
        {
            "button": 3,
            "pos": (110, 110),
        },
    )

    checkbox.handle_event(event)

    assert checkbox.checked is False


def test_checkbox_can_render():
    pygame.init()

    surface = pygame.Surface((640, 480))
    rect = pygame.Rect(100, 100, 20, 20)

    checkbox = Checkbox(
        rect,
        "O(n)",
        checked=True,
    )

    checkbox.render(surface)

    pygame.quit()