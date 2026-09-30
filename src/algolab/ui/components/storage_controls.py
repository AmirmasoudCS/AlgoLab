from __future__ import annotations

import pygame

from algolab.core.storage import ExportStore
from algolab.ui.components.button import Button
from algolab.ui.components.file_dialog import Capture, FileDialog, Restore
from algolab.ui.theme import Color, Font, Radius


class StorageControls:
    """Save / Load buttons in the top toolbar, plus the dialog they open.

    This is the only thing a screen needs to add save/load support:

        self.storage = StorageControls(
            surface, "stack", "Stack",
            capture=self._capture_structure,
            restore=self._restore_structure,
        )

        # handle_event(): after the Info panel check (both are modal)
        if self.storage.handle_event(event):
            return
        # update():
        self.storage.update(dt)
        # render(): after the Info button, before the Info panel
        self.storage.render(self.surface)

    The buttons sit immediately left of the Info button (which is at
    x = width - 115), in the toolbar strip every screen already keeps
    clear. After a successful save or load, a short confirmation pill
    fades in the middle of that same strip.

    capture / restore are documented on FileDialog.
    """

    TOAST_DURATION = 2.2

    def __init__(
        self,
        surface: pygame.Surface,
        topic: str,
        label: str,
        capture: Capture,
        restore: Restore,
        store: ExportStore | None = None,
    ) -> None:
        width = surface.get_width()

        self.save_button = Button(pygame.Rect(width - 331, 15, 100, 38), "Save")
        self.load_button = Button(pygame.Rect(width - 223, 15, 100, 38), "Load")

        self.dialog = FileDialog(
            surface.get_size(),
            topic,
            label,
            capture,
            restore,
            on_done=self.notify,
            store=store,
        )

        self.toast_font = Font.BODY()
        self._toast_message: str | None = None
        self._toast_timer = 0.0

    def notify(self, message: str) -> None:
        """Show a brief confirmation in the toolbar strip."""

        self._toast_message = message
        self._toast_timer = self.TOAST_DURATION

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Returns True if the event was consumed (dialog open, or a
        Save/Load button was clicked)."""

        if self.dialog.handle_event(event):
            return True

        if self.save_button.handle_event(event):
            self.dialog.open("save")
            return True

        if self.load_button.handle_event(event):
            self.dialog.open("load")
            return True

        return False

    def update(self, dt: float) -> None:
        self.save_button.update(dt)
        self.load_button.update(dt)
        self.dialog.update(dt)

        if self._toast_timer > 0:
            self._toast_timer = max(0.0, self._toast_timer - dt)

    def render(self, surface: pygame.Surface) -> None:
        self.save_button.render(surface)
        self.load_button.render(surface)

        if self._toast_timer > 0 and self._toast_message:
            self._render_toast(surface)

        # Last, so the dialog draws over everything else on the screen.
        self.dialog.render(surface)

    def _render_toast(self, surface: pygame.Surface) -> None:
        # The pill must stay clear of the Save button (left edge at
        # width - 331), so its width is capped and long names are cut.
        max_text_width = 420

        message = self._toast_message or ""

        while (
            message
            and self.toast_font.size(message)[0] > max_text_width
        ):
            message = message[:-1]

        if message != self._toast_message:
            message = message.rstrip() + "..."

        text_surface = self.toast_font.render(message, True, Color.TEXT_PRIMARY)

        padding_x = 16
        padding_y = 8

        pill_rect = pygame.Rect(
            0,
            15,
            text_surface.get_width() + padding_x * 2,
            text_surface.get_height() + padding_y * 2,
        )
        pill_rect.centerx = surface.get_width() // 2

        fade_start = self.TOAST_DURATION / 3

        if self._toast_timer < fade_start:
            alpha = int(255 * (self._toast_timer / fade_start))
        else:
            alpha = 255

        pill = pygame.Surface(pill_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(
            pill,
            (*Color.SURFACE_RAISED, min(230, alpha)),
            pill.get_rect(),
            border_radius=Radius.PILL,
        )
        pygame.draw.rect(
            pill,
            (*Color.STATE_SUCCESS, alpha),
            pill.get_rect(),
            2,
            border_radius=Radius.PILL,
        )

        text_surface.set_alpha(alpha)
        pill.blit(text_surface, (padding_x, padding_y))

        surface.blit(pill, pill_rect)