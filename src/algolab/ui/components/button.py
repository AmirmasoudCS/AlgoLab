import pygame


class Button:
    """A clickable button with a label."""

    def __init__(
        self,
        rect: pygame.Rect,
        label: str,
        enabled: bool = True,
    ) -> None:
        self.rect = rect
        self.label = label
        self.enabled = enabled

        self.font = pygame.font.Font(None, 28)

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle user interaction and return whether the button was clicked."""

        if not self.enabled:
            return False

        if event.type != pygame.MOUSEBUTTONDOWN:
            return False

        if event.button != 1:
            return False

        return self.rect.collidepoint(event.pos)

    def render(self, surface: pygame.Surface) -> None:
        """Render the button."""

        mouse_position = pygame.mouse.get_pos()

        if not self.enabled:
            background = (40, 40, 40)

        elif self.rect.collidepoint(mouse_position):
            background = (70, 70, 70)

        else:
            background = (50, 50, 50)

        pygame.draw.rect(
            surface,
            background,
            self.rect,
            border_radius=8,
        )

        border_color = (
            (100, 100, 100)
            if self.enabled
            else (70, 70, 70)
        )

        pygame.draw.rect(
            surface,
            border_color,
            self.rect,
            2,
            border_radius=8,
        )

        text_color = (
            (240, 240, 240)
            if self.enabled
            else (120, 120, 120)
        )

        text = self.font.render(
            self.label,
            True,
            text_color,
        )

        text_rect = text.get_rect(
            center=self.rect.center,
        )

        surface.blit(
            text,
            text_rect,
        )