import pygame

from algolab.ui.theme import Color, Font, Radius


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

        self.font = Font.BODY()

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle user interaction with the checkbox."""

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.checked = not self.checked

    def render(self, surface: pygame.Surface) -> None:
        """Render the checkbox and its label."""

        hovered = self.rect.collidepoint(pygame.mouse.get_pos())

        if self.checked:
            pygame.draw.rect(
                surface,
                Color.ACCENT,
                self.rect,
                border_radius=Radius.SM,
            )
        else:
            fill = Color.SURFACE_RAISED if hovered else Color.SURFACE
            pygame.draw.rect(
                surface,
                fill,
                self.rect,
                border_radius=Radius.SM,
            )

        border_color = Color.ACCENT if self.checked else Color.BORDER
        pygame.draw.rect(
            surface,
            border_color,
            self.rect,
            2,
            border_radius=Radius.SM,
        )

        if self.checked:
            inset = self.rect.inflate(-int(self.rect.width * 0.45), -int(self.rect.height * 0.45))

            pygame.draw.line(
                surface,
                Color.BG,
                (inset.left, inset.centery),
                (inset.centerx, inset.bottom),
                3,
            )

            pygame.draw.line(
                surface,
                Color.BG,
                (inset.centerx, inset.bottom),
                (inset.right, inset.top),
                3,
            )

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