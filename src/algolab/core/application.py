import pygame

from algolab.core.configuration import Configuration, get_resource_path
from algolab.ui.screens.main_menu import MainMenuScreen
from algolab.ui.screens.screen_manager import ScreenManager
from algolab.ui.theme import Color


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
                self.running = False
                continue

            self.screen_manager.handle_event(self._translate_event(event))

    def _update(self, dt: float) -> None:
        self.screen_manager.update(dt)

    def _render(self) -> None:
        self.screen_manager.render()

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