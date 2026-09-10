import pygame


class NumericInput:
    """A simple input field for integer values."""

    def __init__(
        self,
        rect: pygame.Rect,
        value: int,
    ) -> None:
        self.rect = rect
        self.value = value

        self.font = pygame.font.Font(None, 26)

        self._text = str(value)
        self._active = False

    @property
    def active(self) -> bool:
        return self._active

    def handle_event(self, event: pygame.event.Event) -> int | None:
        """Handle input and return a new value when submitted."""

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._active = self.rect.collidepoint(event.pos)

        if (
            event.type == pygame.KEYDOWN
            and self._active
        ):
            if event.key == pygame.K_RETURN:
                try:
                    value = int(self._text)

                except ValueError:
                    self._text = str(self.value)
                    self._active = False
                    return None

                self.value = value
                self._active = False

                return value

            if event.key == pygame.K_BACKSPACE:
                self._text = self._text[:-1]

            elif event.unicode.isdigit():
                self._text += event.unicode

        return None

    def render(self, surface: pygame.Surface) -> None:
        """Render the input field."""

        border_color = (
            (80, 200, 120)
            if self._active
            else (180, 180, 180)
        )

        pygame.draw.rect(
            surface,
            (30, 30, 30),
            self.rect,
        )

        pygame.draw.rect(
            surface,
            border_color,
            self.rect,
            2,
        )

        text = self.font.render(
            self._text,
            True,
            (240, 240, 240),
        )

        surface.blit(
            text,
            (
                self.rect.x + 8,
                self.rect.centery - text.get_height() // 2,
            ),
        )