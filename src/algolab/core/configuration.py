from pathlib import Path
import sys
import tomllib


DEFAULT_EXPORT_DIRECTORY = "exports"


class Configuration:
    """Loads and provides access to application configuration."""

    def __init__(self, path: Path) -> None:
        self._data = self._load(path)

    @staticmethod
    def _load(path: Path) -> dict:
        with path.open("rb") as file:
            return tomllib.load(file)

    @property
    def window(self) -> dict:
        return self._data["window"]

    @property
    def performance(self) -> dict:
        return self._data["performance"]

    @property
    def storage(self) -> dict:
        """The optional [storage] section (empty if the file has none)."""
        return self._data.get("storage", {})

    @property
    def export_directory(self) -> Path:
        """Default folder for saved data structures.

        A relative value in config.toml is resolved against the
        application directory (see get_app_dir), so the default
        "exports" lands next to config/ in development and next to the
        executable in a packaged build. An absolute value is used as-is.
        """
        configured = self.storage.get("export_directory", DEFAULT_EXPORT_DIRECTORY)
        path = Path(str(configured)).expanduser()

        if path.is_absolute():
            return path

        return get_app_dir() / path


def get_resource_path(relative_path: str) -> Path:
    """Return the path to an application resource."""
    if getattr(sys, "frozen", False):
        base_path = Path(sys._MEIPASS)
    else:
        base_path = Path(__file__).resolve().parents[3]

    return base_path / relative_path


def get_app_dir() -> Path:
    """Return the folder the application lives in.

    Unlike get_resource_path (which points at bundled, read-only
    resources inside a PyInstaller bundle), this is where the app
    writes user-visible files such as exports: the project root when
    running from source, and the folder containing the executable when
    frozen.
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent

    return Path(__file__).resolve().parents[3]