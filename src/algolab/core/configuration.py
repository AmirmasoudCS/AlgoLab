from pathlib import Path
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