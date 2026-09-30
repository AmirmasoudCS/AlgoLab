from __future__ import annotations

from typing import Callable

import pygame

from algolab.ui.theme import Color, Font, Radius


class TextInput:
    """A single-line text field, styled like NumericInput.

    Click to focus; typed characters are appended, Backspace deletes.
    Text longer than the field scrolls so the end (where you are
    typing) stays visible.

    handle_event() returns:
        "submit"   when Enter is pressed while focused,
        "changed"  when the text was edited,
        None       otherwise.

    Pasting is not supported (pygame has no portable clipboard API), so
    callers that need to enter long text should offer another way too,
    such as the folder browser in FileDialog.
    """

    def __init__(
        self,
        rect: pygame.Rect,
        text: str = "",
        max_length: int = 64,
        allowed: Callable[[str], bool] | None = None,
        placeholder: str = "",
    ) -> None:
        self.rect = rect
        self.max_length = max_length
        self.allowed = allowed
        self.placeholder = placeholder

        self.font = Font.BODY()

        self._text = text[:max_length]
        self._active = False

    @property
    def text(self) -> str:
        return self._text

    @property
    def active(self) -> bool:
        return self._active

    def set_text(self, text: str) -> None:
        self._text = text[: self.max_length]

    def focus(self) -> None:
        self._active = True

    def blur(self) -> None:
        self._active = False

    def handle_event(self, event: pygame.event.Event) -> str | None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._active = self.rect.collidepoint(event.pos)
            return None

        if event.type != pygame.KEYDOWN or not self._active:
            return None

        if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            return "submit"

        if event.key == pygame.K_BACKSPACE:
            if self._text:
                self._text = self._text[:-1]
                return "changed"

            return None

        character = event.unicode

        if (
            character
            and character.isprintable()
            and len(self._text) < self.max_length
            and (self.allowed is None or self.allowed(character))
        ):
            self._text += character
            return "changed"

        return None

    def render(self, surface: pygame.Surface) -> None:
        background = Color.ACCENT_SOFT if self._active else Color.SURFACE
        border_color = Color.ACCENT if self._active else Color.BORDER

        pygame.draw.rect(surface, background, self.rect, border_radius=Radius.SM)
        pygame.draw.rect(
            surface, border_color, self.rect, 2, border_radius=Radius.SM
        )

        padding = 8
        inner_width = self.rect.width - padding * 2

        if self._text:
            text_surface = self.font.render(self._text, True, Color.TEXT_PRIMARY)
        elif self.placeholder and not self._active:
            text_surface = self.font.render(
                self.placeholder, True, Color.TEXT_MUTED
            )
        else:
            text_surface = None

        text_y = self.rect.centery - self.font.get_height() // 2
        cursor_x = self.rect.x + padding

        if text_surface is not None:
            overflow = max(0, text_surface.get_width() - inner_width)

            # Show the tail of long text: skip `overflow` pixels from
            # the left so the caret end stays inside the field.
            visible = pygame.Rect(
                overflow,
                0,
                min(inner_width, text_surface.get_width()),
                text_surface.get_height(),
            )
            surface.blit(text_surface, (self.rect.x + padding, text_y), visible)

            if self._text:
                cursor_x += visible.width + 3

        if self._active:
            pygame.draw.line(
                surface,
                Color.ACCENT,
                (cursor_x, text_y),
                (cursor_x, text_y + self.font.get_height()),
                2,
            )