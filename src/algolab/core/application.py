from datetime import datetime
from pathlib import Path

import pygame

from algolab.core.configuration import Configuration, get_resource_path
from algolab.ui.screens.main_menu import MainMenuScreen
from algolab.ui.screens.screen_manager import ScreenManager
from algolab.ui.theme import Color, Font, Radius
from algolab.core.storage import ExportStore, configure_store, user_settings_path
from algolab.ui.components.file_dialog import FileDialog


class Application:
    """
    Main application responsible for the Pygame lifecycle.

    Rendering strategy
    ------------------
    Every screen in this app is written against a fixed "virtual"
    resolution (the width/height from window.ini, e.g. 1280x820) --
    every button rect, node position, and canvas boundary assumes that
    coordinate space. Rather than teach every screen to be resolution-
    aware, screens keep drawing onto one fixed-size off-screen Surface
    (self.virtual_surface) exactly as before, and this class scales
    that whole image up to fill the machine's actual screen at the end
    of every frame.

    The scale factor is uniform (the same for x and y), so shapes stay
    circles and text stays undistorted; letterbox bars fill any leftover
    space when the real screen's aspect ratio doesn't exactly match the
    virtual one. This is a deliberate choice over a non-uniform stretch,
    which would visibly warp every graph node and heap circle.

    Mouse input translation
    ------------------------
    Because screens only know about virtual coordinates, two kinds of
    mouse input need to be translated from real screen pixels back into
    virtual space:

    1. Click/motion events, translated in _translate_event() before
       being handed to the ScreenManager.
    2. Direct pygame.mouse.get_pos() calls, used by Button.update() (and
       by HeapScreen's heap-type buttons) purely for hover highlighting,
       not for handling clicks. These calls happen deep inside widget
       code this class doesn't own, so rather than edit every widget
       file, pygame.mouse.get_pos is monkeypatched once, here, to
       transparently return virtual coordinates everywhere it's called
       in the process. This is unusual enough to call out explicitly:
       it's a deliberate, narrow patch of a single library function,
       not a general practice used elsewhere in this app.
    """

    def __init__(self, config: Configuration) -> None:
        self.config = config
        configure_store(ExportStore(config.export_directory, user_settings_path()))

        pygame.init()

        window_config = self.config.window
        performance_config = self.config.performance

        # The virtual resolution is exactly the size every screen's
        # hardcoded layout was designed against. Screens never see the
        # real display surface directly; they only ever draw onto a
        # Surface of this fixed size.
        self.virtual_width = window_config["width"]
        self.virtual_height = window_config["height"]

        # Detect the machine's actual screen resolution and always run
        # in true fullscreen at that resolution. window_config["resizable"]
        # no longer affects the display mode, since a fixed fullscreen
        # window has nothing to resize; the key is left in window.ini
        # harmlessly unused rather than requiring a config file change.
        display_info = pygame.display.Info()
        self.real_width = display_info.current_w
        self.real_height = display_info.current_h

        self.screen = pygame.display.set_mode(
            (self.real_width, self.real_height),
            pygame.FULLSCREEN,
        )

        self.virtual_surface = pygame.Surface(
            (self.virtual_width, self.virtual_height)
        ).convert()

        # Uniform scale factor (same for both axes) so proportions are
        # preserved; letterbox offset centers the scaled image within
        # whatever space is left over on a mismatched aspect ratio.
        self.scale = min(
            self.real_width / self.virtual_width,
            self.real_height / self.virtual_height,
        )

        scaled_width = round(self.virtual_width * self.scale)
        scaled_height = round(self.virtual_height * self.scale)
        self.scaled_size = (scaled_width, scaled_height)

        self.offset = (
            (self.real_width - scaled_width) // 2,
            (self.real_height - scaled_height) // 2,
        )

        self._install_mouse_position_patch()

        # Screenshots save the clean virtual surface (before scaling and
        # letterboxing), so a screenshot always looks the same 1280x820
        # image regardless of what real screen resolution it was taken
        # on. The path is relative to wherever the app is run from, not
        # resolved through get_resource_path -- that helper is for
        # reading bundled assets, and its behavior for a *writable*
        # directory in a packaged/frozen build is untested here, so a
        # plain relative path is the safer, more literal choice.
        self.screenshot_dir = Path("assets/screenshots")
        self._screenshot_counter = 0

        self.toast_font = Font.BODY()
        self._toast_message: str | None = None
        self._toast_timer = 0.0
        self.TOAST_DURATION = 1.5

        icon_path = get_resource_path("assets/icon.png")
        icon = pygame.image.load(icon_path).convert_alpha()
        pygame.display.set_icon(icon)

        pygame.display.set_caption(window_config["title"])

        self.clock = pygame.time.Clock()
        self.target_fps = performance_config["fps"]

        self.running = True

        self.screen_manager = ScreenManager()

        # Every screen receives the fixed-size virtual surface, never
        # the real display surface, so self.surface.get_width()/height()
        # inside any screen always returns the virtual resolution
        # regardless of the machine's actual screen size.
        self.screen_manager.set_screen(
            MainMenuScreen(
                self.virtual_surface,
                self.screen_manager,
            )
        )

    def _install_mouse_position_patch(self) -> None:
        """
        Make pygame.mouse.get_pos() transparently return virtual
        coordinates everywhere in the process, for the reason explained
        in this class's docstring: hover-detection code inside Button
        and elsewhere reads the mouse position directly rather than
        through a translated event, and that code lives outside files
        this class can edit.
        """

        real_get_pos = pygame.mouse.get_pos

        def virtual_get_pos():
            return self._real_to_virtual(real_get_pos())

        pygame.mouse.get_pos = virtual_get_pos

    def _real_to_virtual(self, position: tuple[int, int]) -> tuple[int, int]:
        """Convert a point in real screen pixels to virtual-surface coordinates."""

        real_x, real_y = position

        virtual_x = (real_x - self.offset[0]) / self.scale
        virtual_y = (real_y - self.offset[1]) / self.scale

        return (int(virtual_x), int(virtual_y))

    def _translate_event(self, event: pygame.event.Event) -> pygame.event.Event:
        """
        Return a copy of event with its `pos` field (if any) converted
        from real screen coordinates to virtual coordinates, so every
        screen's handle_event() keeps working against the same
        coordinate space its button rects were written in.
        """

        if not hasattr(event, "pos"):
            return event

        attributes = dict(event.dict)
        attributes["pos"] = self._real_to_virtual(event.pos)

        return pygame.event.Event(event.type, attributes)

    def run(self) -> None:
        """Run the main application loop."""
        while self.running:
            dt = self.clock.tick(self.target_fps) / 1000.0

            self._handle_events()
            self._update(dt)
            self._render()

        pygame.quit()

    def _handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                continue

            # True fullscreen has no window chrome and no close button,
            # so Escape is bound as a way out. This is an addition, not
            # something carried over from the windowed version -- remove
            # or rebind it if you'd rather handle exiting differently.
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if FileDialog.any_open():
                    self.screen_manager.handle_event(self._translate_event(event))
                    continue
                self.running = False
                continue

            if event.type == pygame.KEYDOWN and event.key == pygame.K_F12:
                self._take_screenshot()
                continue

            self.screen_manager.handle_event(self._translate_event(event))

    def _take_screenshot(self) -> None:
        """
        Save the current frame (the clean virtual surface, before
        scaling/letterboxing) to assets/screenshots/, then arm a brief
        on-screen toast confirming it. The toast is set *after* saving,
        so the saved image itself never contains the toast.
        """

        try:
            self.screenshot_dir.mkdir(parents=True, exist_ok=True)
        except OSError as error:
            # A failed screenshot save shouldn't crash a live demo; the
            # toast doubles as the only feedback in a packaged build
            # with no visible console for a print() to land in.
            self._toast_message = f"Screenshot failed: {error}"
            self._toast_timer = self.TOAST_DURATION
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self._screenshot_counter += 1
        filename = f"screenshot_{timestamp}_{self._screenshot_counter:03d}.png"
        path = self.screenshot_dir / filename

        try:
            pygame.image.save(self.virtual_surface, str(path))
        except pygame.error as error:
            self._toast_message = f"Screenshot failed: {error}"
            self._toast_timer = self.TOAST_DURATION
            return

        print(f"Screenshot saved to {path}")

        self._toast_message = f"Screenshot saved: {filename}"
        self._toast_timer = self.TOAST_DURATION

    def _update(self, dt: float) -> None:
        self.screen_manager.update(dt)

        if self._toast_timer > 0:
            self._toast_timer = max(0.0, self._toast_timer - dt)

    def _render(self) -> None:
        self.screen_manager.render()

        if self._toast_timer > 0:
            self._render_toast()

        # Letterbox background matches the app's own dark theme so the
        # bars (visible only when the real screen's aspect ratio doesn't
        # exactly match the virtual one) blend in rather than showing as
        # plain black borders.
        self.screen.fill(Color.BG)

        # smoothscale (bilinear) over scale (nearest-neighbor) trades a
        # small amount of per-frame cost for noticeably cleaner text and
        # rounded edges at non-integer scale factors. If this becomes a
        # performance problem on lower-end hardware, swap this for
        # pygame.transform.scale instead.
        scaled_surface = pygame.transform.smoothscale(
            self.virtual_surface, self.scaled_size
        )

        self.screen.blit(scaled_surface, self.offset)

        pygame.display.flip()

    def _render_toast(self) -> None:
        """
        Draw the screenshot confirmation as a small pill centered in
        the empty middle of the top toolbar strip -- every screen
        already keeps that area clear between the back button (top
        left) and the Info/Exit button (top right).
        """

        text_surface = self.toast_font.render(
            self._toast_message, True, Color.TEXT_PRIMARY
        )

        padding_x = 16
        padding_y = 8

        pill_width = text_surface.get_width() + padding_x * 2
        pill_height = text_surface.get_height() + padding_y * 2

        pill_rect = pygame.Rect(
            (self.virtual_width - pill_width) // 2,
            15,
            pill_width,
            pill_height,
        )

        # Fade out over the last third of TOAST_DURATION rather than
        # popping off abruptly.
        fade_start = self.TOAST_DURATION / 3
        if self._toast_timer < fade_start:
            alpha = int(255 * (self._toast_timer / fade_start))
        else:
            alpha = 255

        pill_surface = pygame.Surface(pill_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(
            pill_surface,
            (*Color.SURFACE_RAISED, min(230, alpha)),
            pill_surface.get_rect(),
            border_radius=Radius.PILL,
        )
        pygame.draw.rect(
            pill_surface,
            (*Color.BORDER, alpha),
            pill_surface.get_rect(),
            2,
            border_radius=Radius.PILL,
        )

        text_surface.set_alpha(alpha)
        pill_surface.blit(text_surface, (padding_x, padding_y))

        self.virtual_surface.blit(pill_surface, pill_rect)