from unittest.mock import Mock

from algolab.ui.screens.screen_manager import ScreenManager


def test_screen_manager_starts_without_screen():
    manager = ScreenManager()

    assert manager.current_screen is None


def test_set_screen():
    manager = ScreenManager()
    screen = Mock()

    manager.set_screen(screen)

    assert manager.current_screen is screen


def test_handle_event_forwards_to_current_screen():
    manager = ScreenManager()

    screen = Mock()
    manager.set_screen(screen)

    event = Mock()

    manager.handle_event(event)

    screen.handle_event.assert_called_once_with(event)


def test_update_forwards_to_current_screen():
    manager = ScreenManager()

    screen = Mock()
    manager.set_screen(screen)

    manager.update(0.016)

    screen.update.assert_called_once_with(0.016)


def test_render_forwards_to_current_screen():
    manager = ScreenManager()

    screen = Mock()
    manager.set_screen(screen)

    manager.render()

    screen.render.assert_called_once()


def test_manager_is_safe_without_screen():
    manager = ScreenManager()

    manager.handle_event(Mock())
    manager.update(0.016)
    manager.render()