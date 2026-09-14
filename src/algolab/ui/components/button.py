# button.py
import pygame
from algolab.ui.theme import Color, Font, Radius


def _lerp_color(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


class Button:
    def __init__(self, rect, label, enabled=True, variant="default"):
        self.rect = rect
        self.label = label
        self.enabled = enabled
        self.variant = variant  # "default" | "primary" | "danger"
        self.font = Font.BODY()
        self._hover_t = 0.0   # 0..1, animated
        self._pressed = False

    def _base_colors(self):
        if self.variant == "primary":
            return Color.ACCENT_SOFT, Color.ACCENT
        if self.variant == "danger":
            return (56, 32, 32), Color.STATE_DANGER
        return Color.SURFACE_RAISED, Color.BORDER

    def handle_event(self, event) -> bool:
        if not self.enabled:
            return False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self._pressed = True
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            was_pressed = self._pressed
            self._pressed = False
            if was_pressed and self.rect.collidepoint(event.pos):
                return True
        return False

    def update(self, dt: float) -> None:
        hovered = self.enabled and self.rect.collidepoint(pygame.mouse.get_pos())
        target = 1.0 if hovered else 0.0
        speed = 10.0  # higher = snappier
        self._hover_t += (target - self._hover_t) * min(1.0, speed * dt)

    def render(self, surface: pygame.Surface) -> None:
        bg_base, border_base = self._base_colors()
        bg_hover = _lerp_color(bg_base, Color.SURFACE_RAISED if self.variant == "default" else border_base, 0.35)
        bg = _lerp_color(bg_base, bg_hover, self._hover_t)

        rect = self.rect.copy()
        if self._pressed:
            rect.inflate_ip(-2, -2)  # subtle press feedback

        if not self.enabled:
            bg = Color.SURFACE

        pygame.draw.rect(surface, bg, rect, border_radius=Radius.MD)

        border_color = border_base if self.enabled else Color.BORDER_SOFT
        pygame.draw.rect(surface, border_color, rect, 1, border_radius=Radius.MD)

        text_color = Color.TEXT_PRIMARY if self.enabled else Color.TEXT_MUTED
        label = self.font.render(self.label, True, text_color)
        surface.blit(label, label.get_rect(center=rect.center))