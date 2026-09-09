import pygame


class Checkbox:
    """A clickable checkbox with a label."""

    def __init__(
        self,
        rect: pygame.Rect,
        label: str,
        checked: bool = False,
    ) -> None:
        self.rect = rect
        self.label = label
        self.checked = checked

        self.font = pygame.font.Font(None, 28)

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle user interaction with the checkbox."""

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.checked = not self.checked

    def render(self, surface: pygame.Surface) -> None:
        """Render the checkbox and its label."""

        pygame.draw.rect(
            surface,
            (220, 220, 220),
            self.rect,
            2,
        )

        if self.checked:
            pygame.draw.line(
                surface,
                (80, 200, 120),
                self.rect.topleft,
                self.rect.bottomright,
                3,
            )

            pygame.draw.line(
                surface,
                (80, 200, 120),
                self.rect.topright,
                self.rect.bottomleft,
                3,
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