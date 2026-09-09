import pygame


class RadioButton:
    """A clickable radio button with a label."""

    def __init__(
        self,
        rect: pygame.Rect,
        label: str,
        selected: bool = False,
    ) -> None:
        self.rect = rect
        self.label = label
        self.selected = selected

        self.font = pygame.font.Font(None, 28)

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle user interaction with the radio button."""

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.selected = True

    def render(self, surface: pygame.Surface) -> None:
        """Render the radio button and its label."""

        center = self.rect.center
        radius = self.rect.width // 2

        pygame.draw.circle(
            surface,
            (220, 220, 220),
            center,
            radius,
            2,
        )

        if self.selected:
            pygame.draw.circle(
                surface,
                (80, 200, 120),
                center,
                radius - 5,
        )

        text = self.font.render(
            self.label,
            True,
            (240, 240, 240),
        )

        text_position = (
            self.rect.right + 10,
            self.rect.centery - text.get_height() // 2,
        )

        surface.blit(text, text_position)