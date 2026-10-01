"""Saving and loading data structures as JSON files.

Every saved file is a small, versioned "envelope" around a screen's own
payload:

    {
      "app": "AlgoLab",
      "version": 1,
      "topic": "bst",
      "mode": "avl",            (null for topics with a single mode)
      "saved_at": "2026-09-30T10:19:00",
      "data": { ... whatever the topic's model serializes ... }
    }

This module knows nothing about individual data structures. Each topic's
model turns itself into / out of the plain ``data`` dict; this module
only handles files, folders, naming, and validating the envelope.

All user-facing failures are raised as StorageError with a message that
is safe to show directly in the UI.
"""

from __future__ import annotations

import json
import os
import re
import sys
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

from algolab.core.configuration import DEFAULT_EXPORT_DIRECTORY, get_app_dir


FORMAT_NAME = "AlgoLab"
FORMAT_VERSION = 1
FILE_EXTENSION = ".json"

# A real save is a few kilobytes. These limits only exist so a wrong or
# hostile file cannot make the app read gigabytes.
MAX_FILE_BYTES = 5 * 1024 * 1024
PEEK_LIMIT_BYTES = 1024 * 1024

MAX_FILENAME_LENGTH = 80
MAX_LISTED_FILES = 200

_SETTINGS_KEY = "export_directory"


class StorageError(Exception):
    """A problem with saving or loading. str(error) is user-presentable."""


class FileExistsStorageError(StorageError):
    """Raised when saving would overwrite a file and overwrite was not allowed."""


# ----------------------------------------------------------------------
# Paths
# ----------------------------------------------------------------------


def user_data_dir() -> Path:
    """Per-user folder for AlgoLab's own settings (not exports)."""

    if sys.platform == "win32":
        base = os.environ.get("APPDATA")
        root = Path(base) if base else Path.home() / "AppData" / "Roaming"
        return root / "AlgoLab"

    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "AlgoLab"

    base = os.environ.get("XDG_CONFIG_HOME")
    root = Path(base) if base else Path.home() / ".config"

    return root / "algolab"


def user_settings_path() -> Path:
    return user_data_dir() / "settings.json"


# ----------------------------------------------------------------------
# File names
# ----------------------------------------------------------------------

_ALLOWED_NAME = re.compile(r"^[\w .()\-]+$")

_RESERVED_NAMES = {
    "con",
    "prn",
    "aux",
    "nul",
    *(f"com{number}" for number in range(1, 10)),
    *(f"lpt{number}" for number in range(1, 10)),
}


def is_allowed_name_character(character: str) -> bool:
    """True if a single typed character may appear in a file name."""
    return bool(_ALLOWED_NAME.match(character))


def clean_filename(name: str) -> str:
    """Validate a user-typed file name and return it without extension.

    Raises:
        StorageError: If the name is empty or unsafe. Path separators
            and other characters that are invalid on common file
            systems are rejected, so a name can never point outside the
            export folder.
    """

    stem = name.strip()

    if stem.lower().endswith(FILE_EXTENSION):
        stem = stem[: -len(FILE_EXTENSION)].rstrip()

    if not stem:
        raise StorageError("Enter a file name.")

    if len(stem) > MAX_FILENAME_LENGTH:
        raise StorageError(
            f"File names can be at most {MAX_FILENAME_LENGTH} characters."
        )

    if not _ALLOWED_NAME.match(stem):
        raise StorageError(
            "File names may only use letters, digits, spaces, and "
            "the characters _ - . ( )"
        )

    if stem.startswith(".") or stem.endswith("."):
        raise StorageError("File names cannot start or end with a dot.")

    if stem.split(".")[0].strip().lower() in _RESERVED_NAMES:
        raise StorageError(f"'{stem}' is a reserved name on some systems.")

    return stem


# ----------------------------------------------------------------------
# Data classes
# ----------------------------------------------------------------------


@dataclass(frozen=True)
class Envelope:
    """A validated saved file."""

    topic: str
    mode: str | None
    data: dict
    saved_at: str


@dataclass(frozen=True)
class SavedFile:
    """One row of a folder listing.

    topic/mode are None when the file could not be read as an AlgoLab
    save; `error` then says why.
    """

    path: Path
    name: str
    topic: str | None
    mode: str | None
    modified: float
    error: str | None = None


# ----------------------------------------------------------------------
# The store
# ----------------------------------------------------------------------


class ExportStore:
    """Reads and writes saved structures in one "current" export folder.

    The current folder starts as `default_directory`. The user can point
    it somewhere else; that choice is remembered in `settings_path`
    (a small JSON file kept outside the export folder, in a per-user
    location) and restored on the next run. If the remembered folder no
    longer exists, the default is used instead.
    """

    def __init__(
        self,
        default_directory: Path,
        settings_path: Path | None = None,
    ) -> None:
        self._default = Path(default_directory).expanduser().absolute()
        self._settings_path = settings_path
        self._directory = self._default

        self._restore_saved_directory()

    # ------------------------------------------------------------------
    # Export folder
    # ------------------------------------------------------------------

    @property
    def directory(self) -> Path:
        return self._directory

    @property
    def default_directory(self) -> Path:
        return self._default

    @property
    def is_default(self) -> bool:
        return self._directory == self._default

    def set_directory(self, path: Path | str) -> bool:
        """Use `path` as the export folder.

        Returns:
            True if the choice was also remembered for the next run,
            False if it only applies to this session because the
            settings file could not be written.

        Raises:
            StorageError: If the folder does not exist or is not
                writable. The current folder is left unchanged.
        """

        candidate = Path(path).expanduser()

        try:
            candidate = candidate.resolve()
        except OSError as error:
            raise StorageError(f"Cannot use '{path}': {error}") from error

        if not candidate.is_dir():
            raise StorageError(f"'{candidate}' is not an existing folder.")

        if not os.access(candidate, os.W_OK):
            raise StorageError(f"AlgoLab cannot write to '{candidate}'.")

        self._directory = candidate

        return self._remember_directory()

    def reset_directory(self) -> bool:
        """Go back to the default export folder (see set_directory)."""

        self._directory = self._default

        return self._remember_directory()

    def _restore_saved_directory(self) -> None:
        settings = self._read_settings()
        saved = settings.get(_SETTINGS_KEY)

        if not isinstance(saved, str) or not saved:
            return

        candidate = Path(saved)

        try:
            if candidate.is_dir():
                self._directory = candidate
        except OSError:
            pass

    def _remember_directory(self) -> bool:
        if self._settings_path is None:
            return True

        settings = self._read_settings()

        if self.is_default:
            settings.pop(_SETTINGS_KEY, None)
        else:
            settings[_SETTINGS_KEY] = str(self._directory)

        try:
            self._settings_path.parent.mkdir(parents=True, exist_ok=True)
            self._settings_path.write_text(
                json.dumps(settings, indent=2),
                encoding="utf-8",
            )
        except OSError:
            return False

        return True

    def _read_settings(self) -> dict:
        if self._settings_path is None:
            return {}

        try:
            raw = json.loads(self._settings_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return {}

        return raw if isinstance(raw, dict) else {}

    # ------------------------------------------------------------------
    # Naming
    # ------------------------------------------------------------------

    def path_for(self, name: str) -> Path:
        """Return the full path a (validated) name would be saved to."""
        return self._directory / f"{clean_filename(name)}{FILE_EXTENSION}"

    def exists(self, name: str) -> bool:
        return self.path_for(name).exists()

    def suggest_stem(
        self,
        topic: str,
        mode: str | None = None,
        today: date | None = None,
    ) -> str:
        """Suggest an unused file name, e.g. 'bst-avl-2026-09-30'."""

        parts = [topic]

        # Skip a mode that just repeats the topic (the BST screen's
        # "bst" mode would otherwise give "bst-bst-...").
        if mode and mode != topic:
            parts.append(mode)

        parts.append((today or date.today()).isoformat())

        base = "-".join(parts)
        candidate = base
        counter = 2

        while (self._directory / f"{candidate}{FILE_EXTENSION}").exists():
            candidate = f"{base}-{counter}"
            counter += 1

        return candidate

    # ------------------------------------------------------------------
    # Save
    # ------------------------------------------------------------------

    def save(
        self,
        name: str,
        topic: str,
        mode: str | None,
        data: dict,
        overwrite: bool = False,
    ) -> Path:
        """Write a structure to '<export folder>/<name>.json'.

        The file is written to a temporary name first and then moved
        into place, so a crash or full disk can never leave a
        half-written save behind or destroy the previous version.

        Raises:
            FileExistsStorageError: If the file exists and `overwrite`
                is False.
            StorageError: For an invalid name, data that is not JSON
                serializable, or any file system problem.
        """

        path = self.path_for(name)

        if path.exists() and not overwrite:
            raise FileExistsStorageError(f"'{path.name}' already exists.")

        envelope = {
            "app": FORMAT_NAME,
            "version": FORMAT_VERSION,
            "topic": topic,
            "mode": mode,
            "saved_at": datetime.now().isoformat(timespec="seconds"),
            "data": data,
        }

        try:
            text = json.dumps(envelope, indent=2, allow_nan=False)
        except (TypeError, ValueError) as error:
            raise StorageError(
                f"This structure cannot be saved: {error}"
            ) from error

        temporary = path.with_name(path.name + ".tmp")

        try:
            self._directory.mkdir(parents=True, exist_ok=True)
            temporary.write_text(text, encoding="utf-8")
            os.replace(temporary, path)
        except OSError as error:
            try:
                temporary.unlink(missing_ok=True)
            except OSError:
                pass

            raise StorageError(
                f"Could not write '{path.name}': {error.strerror or error}"
            ) from error

        return path

    # ------------------------------------------------------------------
    # Load / list
    # ------------------------------------------------------------------

    def load(
        self,
        path: Path | str,
        expected_topic: str | None = None,
    ) -> Envelope:
        """Read and validate a saved file.

        Raises:
            StorageError: If the file is missing, too large, not valid
                JSON, not an AlgoLab file, from a newer version, or
                (when `expected_topic` is given) saved from a different
                screen.
        """

        file_path = Path(path)

        if not file_path.is_absolute():
            file_path = self._directory / file_path

        envelope = self._read_envelope(file_path, MAX_FILE_BYTES)

        if expected_topic is not None and envelope.topic != expected_topic:
            raise StorageError(
                f"This file was saved from the '{envelope.topic}' screen, "
                f"not '{expected_topic}'."
            )

        return envelope

    def list_files(self, limit: int = MAX_LISTED_FILES) -> list[SavedFile]:
        """List the .json files in the export folder, newest first."""

        entries: list[tuple[Path, float]] = []

        try:
            if not self._directory.is_dir():
                return []

            for path in self._directory.iterdir():
                if path.suffix.lower() == FILE_EXTENSION and path.is_file():
                    entries.append((path, path.stat().st_mtime))
        except OSError:
            return []

        entries.sort(key=lambda entry: entry[1], reverse=True)

        files = []

        for path, modified in entries[:limit]:
            try:
                envelope = self._read_envelope(path, PEEK_LIMIT_BYTES)
            except StorageError as error:
                files.append(
                    SavedFile(
                        path=path,
                        name=path.stem,
                        topic=None,
                        mode=None,
                        modified=modified,
                        error=str(error),
                    )
                )
                continue

            files.append(
                SavedFile(
                    path=path,
                    name=path.stem,
                    topic=envelope.topic,
                    mode=envelope.mode,
                    modified=modified,
                )
            )

        return files

    @staticmethod
    def _read_envelope(path: Path, size_limit: int) -> Envelope:
        name = path.name

        try:
            size = path.stat().st_size
        except FileNotFoundError:
            raise StorageError(f"'{name}' no longer exists.") from None
        except OSError as error:
            raise StorageError(
                f"Cannot access '{name}': {error.strerror or error}"
            ) from error

        if size > size_limit:
            raise StorageError(f"'{name}' is too large to be an AlgoLab save.")

        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            raise StorageError(f"'{name}' is not a text file.") from None
        except OSError as error:
            raise StorageError(
                f"Cannot read '{name}': {error.strerror or error}"
            ) from error

        try:
            raw = json.loads(text)
        except (ValueError, RecursionError):
            raise StorageError(f"'{name}' is not valid JSON.") from None

        if not isinstance(raw, dict) or raw.get("app") != FORMAT_NAME:
            raise StorageError(f"'{name}' is not an AlgoLab save file.")

        version = raw.get("version")

        if (
            not isinstance(version, int)
            or isinstance(version, bool)
            or version < 1
        ):
            raise StorageError(f"'{name}' has an invalid version number.")

        if version > FORMAT_VERSION:
            raise StorageError(
                f"'{name}' was saved by a newer version of AlgoLab."
            )

        topic = raw.get("topic")

        if not isinstance(topic, str) or not topic:
            raise StorageError(f"'{name}' does not say which screen it is from.")

        mode = raw.get("mode")

        if mode is not None and not isinstance(mode, str):
            raise StorageError(f"'{name}' has an invalid mode.")

        data = raw.get("data")

        if not isinstance(data, dict):
            raise StorageError(f"'{name}' has no data section.")

        saved_at = raw.get("saved_at")

        return Envelope(
            topic=topic,
            mode=mode,
            data=data,
            saved_at=saved_at if isinstance(saved_at, str) else "",
        )


# ----------------------------------------------------------------------
# Process-wide store
# ----------------------------------------------------------------------
#
# Screens are constructed with just (surface, on_back), so they reach
# the store through this accessor rather than a constructor argument.
# Application calls configure_store() once at startup; tests construct
# an ExportStore directly and pass it in explicitly.

_store: ExportStore | None = None


def configure_store(store: ExportStore) -> None:
    global _store
    _store = store


def get_store() -> ExportStore:
    global _store

    if _store is None:
        _store = ExportStore(
            get_app_dir() / DEFAULT_EXPORT_DIRECTORY,
            user_settings_path(),
        )

    return _store