import math

import pygame

from algolab.ui.theme import Color, Radius


def draw_panel(surface, rect, elevated=False, border=True):
    """Draw a consistently-styled dark panel/card."""
    bg = Color.SURFACE_RAISED if elevated else Color.SURFACE
    pygame.draw.rect(surface, bg, rect, border_radius=Radius.LG)
    if border:
        pygame.draw.rect(surface, Color.BORDER_SOFT, rect, 1, border_radius=Radius.LG)


def draw_pill(surface, rect, color, text, font, text_color=Color.TEXT_PRIMARY):
    pygame.draw.rect(surface, color, rect, border_radius=Radius.PILL)
    label = font.render(text, True, text_color)
    surface.blit(label, label.get_rect(center=rect.center))


def draw_item_card(
    surface,
    rect: pygame.Rect,
    background: tuple[int, int, int],
    value_font: pygame.font.Font,
    value,
    caption_font: pygame.font.Font | None = None,
    caption: str | None = None,
    caption_position: str = "below",
    label_font: pygame.font.Font | None = None,
    label: str | None = None,
):
    """
    Draw a single data item card, used for stack, queue and linked
    list items alike, so every topic's boxes share the exact same
    shadow, fill, border and text treatment.

    caption_position: "below" draws the caption under the card
    (e.g. "index 2"). "above" draws a label above it (e.g. "NEW").
    """

    if label is not None and label_font is not None:
        label_surface = label_font.render(label, True, background)
        label_rect = label_surface.get_rect(
            centerx=rect.centerx,
            bottom=rect.top - 5,
        )
        surface.blit(label_surface, label_rect)

    # Faint shadow for a hint of depth, sitting just behind the card.
    shadow_rect = rect.move(0, 3)
    pygame.draw.rect(surface, Color.BG, shadow_rect, border_radius=Radius.MD)

    pygame.draw.rect(surface, background, rect, border_radius=Radius.MD)

    border_color = tuple(min(255, channel + 45) for channel in background)
    pygame.draw.rect(surface, border_color, rect, 2, border_radius=Radius.MD)

    value_text = value_font.render(str(value), True, Color.TEXT_PRIMARY)
    surface.blit(value_text, value_text.get_rect(center=rect.center))

    if caption is not None and caption_font is not None and caption_position == "below":
        caption_text = caption_font.render(caption, True, Color.TEXT_MUTED)
        caption_rect = caption_text.get_rect(centerx=rect.centerx, top=rect.bottom + 3)
        surface.blit(caption_text, caption_rect)


def draw_arrow(
    surface,
    start: tuple[int, int],
    end: tuple[int, int],
    color: tuple[int, int, int],
    width: int = 3,
    head_size: int = 8,
) -> None:
    """
    Draw a straight line with an arrowhead pointing at `end`.

    Unlike a fixed "left/right/up/down" arrowhead, the head angle is
    derived from the line's direction, so this works for the vertical
    HEAD/TOP/FRONT pointers, the horizontal NEXT pointers, and the
    diagonal algorithm pointers in the linked list screen, all with one
    function.
    """

    pygame.draw.line(surface, color, start, end, width)

    angle = math.atan2(end[1] - start[1], end[0] - start[0])
    spread = math.radians(28)

    left = (
        end[0] - head_size * math.cos(angle - spread),
        end[1] - head_size * math.sin(angle - spread),
    )

    right = (
        end[0] - head_size * math.cos(angle + spread),
        end[1] - head_size * math.sin(angle + spread),
    )

    pygame.draw.polygon(surface, color, [end, left, right])