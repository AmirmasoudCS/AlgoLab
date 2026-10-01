import pygame

from algolab.ui.theme import Color, Font, Radius


class NumericInput:
    """A simple input field for integer values."""

    def __init__(
        self,
        rect: pygame.Rect,
        value: int,
    ) -> None:
        self.rect = rect
        self.value = value

        self.font = Font.BODY()

        self._text = str(value)
        self._active = False

    @property
    def active(self) -> bool:
        return self._active

    def set_value(self, value: int) -> None:
        """Set the value from code (not from typing).

        Updates both the stored number and the text shown in the field,
        so the two can never disagree. Used when one field mirrors
        another, and when loading a saved structure.
        """

        self.value = value
        self._text = str(value)

    def handle_event(self, event: pygame.event.Event) -> int | None:
        """Handle input and return a new value when submitted."""

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._active = self.rect.collidepoint(event.pos)

        if (
            event.type == pygame.KEYDOWN
            and self._active
        ):
            if event.key == pygame.K_RETURN:
                self._active = False
                return self.value

            if event.key == pygame.K_BACKSPACE:
                self._text = self._text[:-1]

            elif event.unicode.isdigit():
                self._text += event.unicode

            if self._text:
                self.value = int(self._text)

        return None

    def render(self, surface: pygame.Surface) -> None:
        """Render the input field."""

        background = Color.ACCENT_SOFT if self._active else Color.SURFACE
        border_color = Color.ACCENT if self._active else Color.BORDER

        pygame.draw.rect(
            surface,
            background,
            self.rect,
            border_radius=Radius.SM,
        )

        pygame.draw.rect(
            surface,
            border_color,
            self.rect,
            2,
            border_radius=Radius.SM,
        )

        text = self.font.render(
            self._text,
            True,
            Color.TEXT_PRIMARY,
        )

        text_position = (
            self.rect.x + 8,
            self.rect.centery - text.get_height() // 2,
        )

        surface.blit(text, text_position)

        # A thin blinking-style cursor (always on, kept simple) gives a
        # visual cue that the field is focused and editable, matching
        # the hover/active feedback every other input in the app gives.
        if self._active:
            cursor_x = text_position[0] + text.get_width() + 3
            cursor_top = self.rect.centery - text.get_height() // 2
            cursor_bottom = cursor_top + text.get_height()

            if cursor_x < self.rect.right - 6:
                pygame.draw.line(
                    surface,
                    Color.ACCENT,
                    (cursor_x, cursor_top),
                    (cursor_x, cursor_bottom),
                    2,
                )