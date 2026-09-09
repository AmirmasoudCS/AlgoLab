import pygame

from algolab.ui.components.radio_button import RadioButton


def test_radio_button_can_be_created():
    rect = pygame.Rect(100, 100, 20, 20)

    radio_button = RadioButton(
        rect,
        "Linear",
    )

    assert radio_button.rect == rect
    assert radio_button.label == "Linear"
    assert radio_button.selected is False


def test_radio_button_can_start_selected():
    rect = pygame.Rect(100, 100, 20, 20)

    radio_button = RadioButton(
        rect,
        "Linear",
        selected=True,
    )

    assert radio_button.selected is True


def test_radio_button_becomes_selected_when_clicked():
    rect = pygame.Rect(100, 100, 20, 20)

    radio_button = RadioButton(
        rect,
        "Linear",
    )

    event = pygame.event.Event(
        pygame.MOUSEBUTTONDOWN,
        {
            "button": 1,
            "pos": (110, 110),
        },
    )

    radio_button.handle_event(event)

    assert radio_button.selected is True


def test_radio_button_does_not_change_when_clicked_outside():
    rect = pygame.Rect(100, 100, 20, 20)

    radio_button = RadioButton(
        rect,
        "Linear",
    )

    event = pygame.event.Event(
        pygame.MOUSEBUTTONDOWN,
        {
            "button": 1,
            "pos": (200, 200),
        },
    )

    radio_button.handle_event(event)

    assert radio_button.selected is False


def test_radio_button_ignores_non_left_click():
    rect = pygame.Rect(100, 100, 20, 20)

    radio_button = RadioButton(
        rect,
        "Linear",
    )

    event = pygame.event.Event(
        pygame.MOUSEBUTTONDOWN,
        {
            "button": 3,
            "pos": (110, 110),
        },
    )

    radio_button.handle_event(event)

    assert radio_button.selected is False


def test_radio_button_can_render():
    pygame.init()

    surface = pygame.Surface((640, 480))
    rect = pygame.Rect(100, 100, 20, 20)

    radio_button = RadioButton(
        rect,
        "Linear",
        selected=True,
    )

    radio_button.render(surface)

    pygame.quit()