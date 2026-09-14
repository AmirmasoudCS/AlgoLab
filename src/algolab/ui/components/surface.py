# add to theme.py, or a new src/algolab/ui/components/surface.py
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