import pygame


class Application:
    """Main application responsible for the Pygame lifecycle."""

    def __init__(self) -> None:
        pygame.init()

        self.screen = pygame.display.set_mode((1280, 720))
        pygame.display.set_caption("AlgoLab")

        self.clock = pygame.time.Clock()
        self.running = True

    def run(self) -> None:
        """Run the main application loop."""
        while self.running:
            dt = self.clock.tick(60) / 1000.0

            self._handle_events()
            self._update(dt)
            self._render()

        pygame.quit()

    def _handle_events(self) -> None:
        """Handle application-level events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def _update(self, dt: float) -> None:
        """Update application state."""
        pass

    def _render(self) -> None:
        """Render the current application state."""
        self.screen.fill((30, 30, 30))
        pygame.display.flip()