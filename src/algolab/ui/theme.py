# src/algolab/ui/theme.py
import pygame


class Color:
    # Base surface layers (dark UI, layered by elevation)
    BG = (18, 19, 23)
    SURFACE = (28, 30, 36)
    SURFACE_RAISED = (36, 39, 46)
    BORDER = (54, 58, 68)
    BORDER_SOFT = (44, 47, 55)

    # Text
    TEXT_PRIMARY = (237, 238, 240)
    TEXT_SECONDARY = (158, 163, 173)
    TEXT_MUTED = (110, 114, 122)

    # Brand / accent
    ACCENT = (99, 141, 245)       # primary interactive blue
    ACCENT_HOVER = (124, 161, 250)
    ACCENT_SOFT = (46, 56, 82)    # accent tinted onto dark surface

    # Semantic states (used consistently across ALL topics)
    STATE_DEFAULT = (58, 63, 74)
    STATE_VISITED = (70, 92, 130)
    STATE_COMPARING = (207, 156, 61)
    STATE_ACTIVE = (99, 141, 245)
    STATE_SUCCESS = (86, 176, 125)
    STATE_DANGER = (214, 95, 95)
    STATE_RESULT = (110, 200, 140)
    STATE_REPLACE = (168, 122, 201)

    @staticmethod
    def with_alpha(color, alpha):
        return (*color, alpha)


class Font:
    _cache: dict[tuple[str, int], pygame.font.Font] = {}

    SANS = None  # None -> pygame default; swap for a bundled .ttf later

    @classmethod
    def get(cls, size: int, bold: bool = False) -> pygame.font.Font:
        key = (cls.SANS, size)
        font = cls._cache.get(key)
        if font is None:
            font = pygame.font.Font(cls.SANS, size)
            cls._cache[key] = font
        font.set_bold(bold)
        return font

    # Named scale so every screen speaks the same type system
    H1 = staticmethod(lambda: Font.get(30, bold=True))
    H2 = staticmethod(lambda: Font.get(22, bold=True))
    BODY = staticmethod(lambda: Font.get(20))
    SMALL = staticmethod(lambda: Font.get(16))
    LABEL = staticmethod(lambda: Font.get(15))
    NODE = staticmethod(lambda: Font.get(24, bold=True))


class Radius:
    SM = 6
    MD = 10
    LG = 14
    PILL = 999


class Spacing:
    XS, SM, MD, LG, XL = 4, 8, 16, 24, 32