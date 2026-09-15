from pathlib import Path
import sys
import tomllib


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


def get_resource_path(relative_path: str) -> Path:
    """Return the path to an application resource."""
    if getattr(sys, "frozen", False):
        base_path = Path(sys.executable).parent
    else:
        base_path = Path(__file__).resolve().parents[3]

    return base_path / relative_path