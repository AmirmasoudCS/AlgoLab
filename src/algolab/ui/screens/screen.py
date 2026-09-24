from abc import ABC, abstractmethod
from typing import Callable, Optional

import pygame

from algolab.ui.components.button import Button
from algolab.ui.components.surface import draw_toggle_button

# (label, multiplier applied to a screen's base step interval).
# A larger multiplier means a LONGER pause between steps, i.e. slower
# playback, so "Slow" has the biggest number here.
SPEED_OPTIONS = (("Slow", 1.8), ("Normal", 1.0), ("Fast", 0.45))


class Screen(ABC):
    """Base class for all application screens."""

    def __init__(
        self,
        surface: pygame.Surface,
        on_back: Optional[Callable[[], None]] = None,
    ) -> None:
        self.surface = surface
        self.on_back = on_back

        # Screens that receive an on_back callback automatically get a
        # back button in the same spot, so every topic screen looks and
        # behaves the same way when navigating back to the main menu.
        # Screens that don't need one (like the main menu itself) simply
        # don't pass on_back, and no button is created.
        self.back_button: Button | None = None

        if self.on_back is not None:
            self.back_button = Button(
                pygame.Rect(10, 15, 100, 38),
                "< Menu",
            )

        # Playback speed for step-by-step simulations. Screens with no
        # animation to speed up (the main menu, asymptotic notation)
        # simply never call the methods below, so this costs them
        # nothing. Screens that do animate simulations position these
        # three buttons themselves (rects default to zero-size here,
        # since layout is screen-specific) and call scaled_interval()
        # wherever they currently use a hardcoded step_interval.
        self.speed_multiplier: float = 1.0
        self.speed_buttons: list[Button] = [
            Button(pygame.Rect(0, 0, 0, 0), label) for label, _ in SPEED_OPTIONS
        ]

    def handle_back_event(self, event: pygame.event.Event) -> bool:
        """
        Handle a click on the back button, if one exists.

        Returns True when the button was clicked and on_back was
        invoked, so callers can short-circuit their own event handling.
        """

        if self.back_button is None:
            return False

        if self.back_button.handle_event(event):
            self.on_back()
            return True

        return False

    def update_back_button(self, dt: float) -> None:
        if self.back_button is not None:
            self.back_button.update(dt)

    def render_back_button(self) -> None:
        if self.back_button is not None:
            self.back_button.render(self.surface)

    def handle_speed_event(self, event: pygame.event.Event) -> bool:
        """
        Handle a click on one of the three speed buttons.

        Returns True when a speed button was clicked, so callers can
        treat it the same way as handle_back_event: check it, and skip
        the rest of event handling for that event if it returns True.
        """

        for index, button in enumerate(self.speed_buttons):
            if button.handle_event(event):
                self.speed_multiplier = SPEED_OPTIONS[index][1]
                return True

        return False

    def update_speed_buttons(self, dt: float) -> None:
        for button in self.speed_buttons:
            button.update(dt)

    def render_speed_buttons(self) -> None:
        for index, button in enumerate(self.speed_buttons):
            is_on = SPEED_OPTIONS[index][1] == self.speed_multiplier
            draw_toggle_button(self.surface, button, is_on)

    def scaled_interval(self, base_interval: float) -> float:
        """
        Apply the current speed setting to a screen's base step
        interval. Screens keep their own per-topic base pace (sorting
        is naturally faster than, say, BST since a 30-element sort has
        far more steps) and this just scales that baseline up or down.
        """

        return base_interval * self.speed_multiplier

    def cancel_current_simulation(self) -> None:
        """
        Discard any in-progress simulation so an editing action can
        apply immediately instead of being silently refused.

        Requires the subclass to define current_simulation, simulator
        and operation_committed.
        """

        if getattr(self, "current_simulation", None) is not None:
            self.simulator.reset()
            self.current_simulation = None
            self.operation_committed = False

    @abstractmethod
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle an incoming Pygame event."""
        pass

    @abstractmethod
    def update(self, dt: float) -> None:
        """Update the screen."""
        pass

    @abstractmethod
    def render(self) -> None:
        """Render the screen."""
        pass