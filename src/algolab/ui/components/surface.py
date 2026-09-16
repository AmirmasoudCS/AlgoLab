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


def draw_arrow_head(
    surface,
    tip: tuple[float, float],
    angle: float,
    color: tuple[int, int, int],
    size: int = 8,
) -> None:
    """Draw an arrowhead at `tip`, pointing in the direction of `angle` (radians)."""

    spread = math.radians(28)

    left = (
        tip[0] - size * math.cos(angle - spread),
        tip[1] - size * math.sin(angle - spread),
    )

    right = (
        tip[0] - size * math.cos(angle + spread),
        tip[1] - size * math.sin(angle + spread),
    )

    pygame.draw.polygon(surface, color, [tip, left, right])


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
    draw_arrow_head(surface, end, angle, color, head_size)


def draw_curved_edge(
    surface,
    start: tuple[int, int],
    end: tuple[int, int],
    color: tuple[int, int, int],
    width: int = 2,
    head_size: int = 7,
    steps: int = 16,
) -> None:
    """
    Draw a smooth vertical-biased curve between two points with an
    arrowhead at the end, used for BST parent-child edges (and any
    future tree-shaped topic, like heap or AVL).
    """

    mid_y = (start[1] + end[1]) / 2

    points = []

    for step in range(steps + 1):
        t = step / steps
        x = (1 - t) * start[0] + t * end[0]
        y = (1 - t) ** 2 * start[1] + 2 * (1 - t) * t * mid_y + t ** 2 * end[1]
        points.append((x, y))

    pygame.draw.lines(surface, color, False, points, width)

    tail = points[-2]
    angle = math.atan2(end[1] - tail[1], end[0] - tail[0])
    draw_arrow_head(surface, end, angle, color, head_size)


def draw_toggle_button(
    surface,
    button,
    is_on: bool,
    on_background: tuple[int, int, int] = Color.STATE_SUCCESS_SOFT,
    on_border: tuple[int, int, int] = Color.STATE_SUCCESS,
) -> None:
    """
    Draw a button that lights up green when "on" instead of Button's
    own flat accent-blue `selected` style.

    Used for anything that reads as a physical on/off switch rather
    than "the chosen option among several" (which stays accent blue
    everywhere else): the Directed/Weighted toggles, and the pause
    button while a simulation is actively playing. When `is_on` is
    False this just delegates to the button's normal render, so
    callers don't need an if/else at the call site.
    """

    if not is_on:
        button.render(surface)
        return

    pygame.draw.rect(
        surface, on_background, button.rect, border_radius=Radius.MD
    )
    pygame.draw.rect(
        surface, on_border, button.rect, 2, border_radius=Radius.MD
    )

    text = button.font.render(button.label, True, Color.TEXT_PRIMARY)
    surface.blit(text, text.get_rect(center=button.rect.center))