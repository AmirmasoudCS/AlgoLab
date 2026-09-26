from __future__ import annotations

import pygame

from algolab.ui.theme import Color, Font, Radius


class InfoPanel:
    """
    A modal overlay listing time-complexity information for a topic's
    operations, as a simple three-column table (Operation, Time
    Complexity, Notes).

    Usage from a screen:
        self.info_panel = InfoPanel("Stack — Time Complexity", rows)
        # in handle_event, BEFORE any other input handling:
        if self.info_panel.handle_event(event):
            return
        # elsewhere, a normal button:
        if self.info_button.handle_event(event):
            self.info_panel.open()
        # in render, as the LAST call, so it draws over everything:
        self.info_panel.render(self.surface)

    The panel is modal: handle_event() returns True for every event
    while visible, which the owning screen uses as a signal to stop
    processing that event any further, so a click meant for the
    overlay (or its backdrop) never reaches a button underneath it.
    """

    def __init__(
        self,
        title: str,
        rows: list[tuple[str, str, str]],
    ) -> None:
        """
        rows: a list of (operation, complexity, note) string triples.
        Keep `note` short (well under half the panel width) since this
        table renders each cell as a single line, with no wrapping.
        """

        self.title = title
        self.rows = rows
        self.visible = False

        self.title_font = Font.H1()
        self.header_font = Font.H2()
        self.row_font = Font.BODY()
        self.note_font = Font.SMALL()

        # Populated by render(); handle_event() reads these back, so a
        # click can be tested against the panel actually drawn last
        # frame. Both start as empty rects so an event arriving before
        # the first render simply misses everything, rather than
        # matching a stale or nonsensical area.
        self.panel_rect = pygame.Rect(0, 0, 0, 0)
        self.close_button_rect = pygame.Rect(0, 0, 0, 0)

    def open(self) -> None:
        self.visible = True

    def close(self) -> None:
        self.visible = False

    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Returns True if the panel consumed the event (always the case
        while visible), telling the caller not to process it further.
        """

        if not self.visible:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.close_button_rect.collidepoint(event.pos):
                self.visible = False
            elif not self.panel_rect.collidepoint(event.pos):
                # A click on the dimmed backdrop, outside the panel,
                # also dismisses it -- standard modal behavior. A click
                # inside the panel body (not on the close button) does
                # nothing, but is still consumed below.
                self.visible = False

        return True

    def render(self, surface: pygame.Surface) -> None:
        if not self.visible:
            return

        width, height = surface.get_size()

        backdrop = pygame.Surface((width, height), pygame.SRCALPHA)
        backdrop.fill((0, 0, 0, 170))
        surface.blit(backdrop, (0, 0))

        row_height = 34
        header_block = 100
        footer_margin = 24

        panel_width = min(720, width - 80)
        panel_height = min(
            header_block + len(self.rows) * row_height + footer_margin,
            height - 80,
        )

        self.panel_rect = pygame.Rect(
            (width - panel_width) // 2,
            (height - panel_height) // 2,
            panel_width,
            panel_height,
        )

        pygame.draw.rect(
            surface, Color.SURFACE_RAISED, self.panel_rect, border_radius=Radius.LG
        )
        pygame.draw.rect(
            surface, Color.BORDER, self.panel_rect, 2, border_radius=Radius.LG
        )

        title_surface = self.title_font.render(self.title, True, Color.TEXT_PRIMARY)
        surface.blit(title_surface, (self.panel_rect.x + 24, self.panel_rect.y + 16))

        self.close_button_rect = pygame.Rect(
            self.panel_rect.right - 44, self.panel_rect.y + 14, 28, 28
        )
        pygame.draw.rect(
            surface, Color.STATE_DANGER, self.close_button_rect, border_radius=Radius.SM
        )
        close_label = self.header_font.render("x", True, Color.TEXT_PRIMARY)
        surface.blit(close_label, close_label.get_rect(center=self.close_button_rect.center))

        col_operation_x = self.panel_rect.x + 24
        col_complexity_x = self.panel_rect.x + int(panel_width * 0.40)
        col_note_x = self.panel_rect.x + int(panel_width * 0.62)

        header_y = self.panel_rect.y + 60

        self._draw_cell(surface, "Operation", col_operation_x, header_y, self.header_font, Color.TEXT_SECONDARY)
        self._draw_cell(surface, "Time Complexity", col_complexity_x, header_y, self.header_font, Color.TEXT_SECONDARY)
        self._draw_cell(surface, "Notes", col_note_x, header_y, self.header_font, Color.TEXT_SECONDARY)

        divider_y = header_y + 28
        pygame.draw.line(
            surface,
            Color.BORDER,
            (self.panel_rect.x + 24, divider_y),
            (self.panel_rect.right - 24, divider_y),
            1,
        )

        row_y = divider_y + 10

        for operation, complexity, note in self.rows:
            if row_y + row_height > self.panel_rect.bottom - footer_margin:
                break

            self._draw_cell(surface, operation, col_operation_x, row_y, self.row_font, Color.TEXT_PRIMARY)
            self._draw_cell(surface, complexity, col_complexity_x, row_y, self.row_font, Color.ACCENT)
            self._draw_cell(surface, note, col_note_x, row_y, self.note_font, Color.TEXT_MUTED)

            row_y += row_height

    def _draw_cell(
        self,
        surface: pygame.Surface,
        text: str,
        x: int,
        y: int,
        font: pygame.font.Font,
        color: tuple[int, int, int],
    ) -> None:
        rendered = font.render(text, True, color)
        surface.blit(rendered, (x, y))