import pygame

from algolab.ui.screens.screen import Screen


class MainMenuScreen(Screen):
    """Main menu screen."""

    def handle_event(self, event: pygame.event.Event) -> None:
        pass

    def update(self, dt: float) -> None:
        pass

    def render(self) -> None:
        self.surface.fill((30, 30, 30))