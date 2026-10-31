import ctypes
import sys

from algolab.core.application import Application
from algolab.core.configuration import Configuration, get_resource_path


def enable_dpi_awareness() -> None:
    """
    Tell Windows this process handles its own DPI scaling.

    Without this, Windows reports a scaled-down logical resolution on
    high-DPI displays and then stretches the window, which makes the
    detected screen size unreliable on laptops running at 125% or 150%.
    Must run before pygame.init(). A no-op on non-Windows platforms.
    """
    if sys.platform != "win32":
        return

    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except (AttributeError, OSError):
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except (AttributeError, OSError):
            pass


def main() -> None:
    enable_dpi_awareness()

    config_path = get_resource_path("config/config.toml")

    config = Configuration(config_path)
    app = Application(config)

    app.run()


if __name__ == "__main__":
    main()