import pygame

from algolab.core.configuration import Configuration
from algolab.ui.screens.main_menu import MainMenuScreen
from algolab.ui.screens.screen_manager import ScreenManager
from algolab.ui.screens.asymptotic import AsymptoticScreen


class Application:
    """Main application responsible for the Pygame lifecycle."""

    def __init__(self, config: Configuration) -> None:
        self.config = config

        pygame.init()

        window_config = self.config.window
        performance_config = self.config.performance

        flags = 0

        if window_config["resizable"]:
            flags |= pygame.RESIZABLE

        self.screen = pygame.display.set_mode(
            (
                window_config["width"],
                window_config["height"],
            ),
            flags,
        )

        pygame.display.set_caption(window_config["title"])

        self.clock = pygame.time.Clock()
        self.target_fps = performance_config["fps"]

        self.running = True

        self.screen_manager = ScreenManager()
        self.screen_manager.set_screen(
            AsymptoticScreen(self.screen)

        )

    def run(self) -> None:
        """Run the main application loop."""
        while self.running:
            dt = self.clock.tick(self.target_fps) / 1000.0

            self._handle_events()
            self._update(dt)
            self._render()

        pygame.quit()

    def _handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            else:
                self.screen_manager.handle_event(event)

    def _update(self, dt: float) -> None:
        self.screen_manager.update(dt)

    def _render(self) -> None:
        self.screen_manager.render()
        pygame.display.flip()