import pygame

from algolab.ui.theme import Color, Font


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

        self.font = Font.BODY()

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle user interaction with the radio button."""

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.selected = True

    def render(self, surface: pygame.Surface) -> None:
        """Render the radio button and its label."""

        center = self.rect.center
        radius = self.rect.width // 2
        hovered = self.rect.collidepoint(pygame.mouse.get_pos())

        fill = Color.SURFACE_RAISED if hovered else Color.SURFACE
        pygame.draw.circle(surface, fill, center, radius)

        border_color = Color.ACCENT if self.selected else Color.BORDER
        pygame.draw.circle(surface, border_color, center, radius, 2)

        if self.selected:
            pygame.draw.circle(surface, Color.ACCENT, center, radius - 6)

        text = self.font.render(
            self.label,
            True,
            Color.TEXT_PRIMARY,
        )

        text_position = (
            self.rect.right + 10,
            self.rect.centery - text.get_height() // 2,
        )

        surface.blit(text, text_position)