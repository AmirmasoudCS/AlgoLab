from abc import ABC, abstractmethod
from typing import Callable, Optional

import pygame

from algolab.ui.components.button import Button


class Screen(ABC):
    """Base class for all application screens."""

    def __init__(
        self,
        surface: pygame.Surface,
        on_back: Optional[Callable[[], None]] = None,
    ) -> None:
        self.surface = surface
        self.on_back = on_back

        # Screens that receive an on_back callback automatically get a
        # back button in the same spot, so every topic screen looks and
        # behaves the same way when navigating back to the main menu.
        # Screens that don't need one (like the main menu itself) simply
        # don't pass on_back, and no button is created.
        self.back_button: Button | None = None

        if self.on_back is not None:
            self.back_button = Button(
                pygame.Rect(10, 15, 100, 38),
                "< Menu",
            )

    def handle_back_event(self, event: pygame.event.Event) -> bool:
        """
        Handle a click on the back button, if one exists.

        Returns True when the button was clicked and on_back was
        invoked, so callers can short-circuit their own event handling.
        """

        if self.back_button is None:
            return False

        if self.back_button.handle_event(event):
            self.on_back()
            return True

        return False

    def update_back_button(self, dt: float) -> None:
        if self.back_button is not None:
            self.back_button.update(dt)

    def render_back_button(self) -> None:
        if self.back_button is not None:
            self.back_button.render(self.surface)

    @abstractmethod
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle an incoming Pygame event."""
        pass

    @abstractmethod
    def update(self, dt: float) -> None:
        """Update the screen."""
        pass

    @abstractmethod
    def render(self) -> None:
        """Render the screen."""
        pass