from algolab.ui.screens.screen import Screen


class ScreenManager:
    """Manages the currently active screen."""

    def __init__(self) -> None:
        self._current_screen: Screen | None = None

    @property
    def current_screen(self) -> Screen | None:
        return self._current_screen

    def set_screen(self, screen: Screen) -> None:
        self._current_screen = screen

    def handle_event(self, event) -> None:
        if self._current_screen is not None:
            self._current_screen.handle_event(event)

    def update(self, dt: float) -> None:
        if self._current_screen is not None:
            self._current_screen.update(dt)

    def render(self) -> None:
        if self._current_screen is not None:
            self._current_screen.render()