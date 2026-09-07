from abc import ABC, abstractmethod

import pygame


class Screen(ABC):
    """Base class for all application screens."""

    def __init__(self, surface: pygame.Surface) -> None:
        self.surface = surface

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