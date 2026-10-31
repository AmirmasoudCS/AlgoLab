"""Print what pygame and Windows report about the display.

Run on the machine that misbehaves and send back the output.
"""

import ctypes
import sys

import pygame


def main() -> None:
    print("platform:", sys.platform)
    print("pygame:", pygame.version.ver, "SDL:", pygame.version.SDL)

    if sys.platform == "win32":
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
            print("dpi awareness: set to per-monitor")
        except (AttributeError, OSError) as error:
            print("dpi awareness: could not set:", error)

        try:
            dpi = ctypes.windll.user32.GetDpiForSystem()
            print("system dpi:", dpi, f"({dpi / 96 * 100:.0f}% scaling)")
        except (AttributeError, OSError):
            pass

    pygame.init()

    print("desktop sizes:", pygame.display.get_desktop_sizes())
    info = pygame.display.Info()
    print("display.Info:", info.current_w, info.current_h)

    screen = pygame.display.set_mode((1280, 820), pygame.SCALED | pygame.FULLSCREEN)
    print("surface size:", screen.get_size())
    print("window size:", pygame.display.get_window_size())
    print("fullscreen flag:", bool(screen.get_flags() & pygame.FULLSCREEN))

    pygame.time.wait(3000)
    pygame.quit()


if __name__ == "__main__":
    main()