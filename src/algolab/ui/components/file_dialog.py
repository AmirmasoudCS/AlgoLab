from __future__ import annotations

from pathlib import Path
from typing import Callable

import pygame

from algolab.core.storage import (
    MAX_FILENAME_LENGTH,
    ExportStore,
    FileExistsStorageError,
    SavedFile,
    StorageError,
    clean_filename,
    get_store,
    is_allowed_name_character,
)
from algolab.ui.components.button import Button
from algolab.ui.components.text_input import TextInput
from algolab.ui.theme import Color, Font, Radius


Capture = Callable[[], "tuple[str | None, dict]"]
Restore = Callable[["str | None", dict], None]


class FileDialog:
    """A modal dialog for saving and loading one screen's data structure.

    Two views share the same panel:

    files    Save: a file name field plus the folder's existing files
             (click one to reuse its name). Load: a list of saved files
             to choose from; files saved from other screens are dimmed
             and cannot be loaded here. Both show the current export
             folder with a "Change Folder" button.
    folders  A small folder browser: type a path or click through
             sub-folders, then "Use This Folder" (remembered for next
             time) or "Reset to Default".

    Usage from a screen (normally through StorageControls):
        # in handle_event, BEFORE other input handling (modal):
        if self.dialog.handle_event(event):
            return
        # in update():  self.dialog.update(dt)
        # in render(), last: self.dialog.render(self.surface)

    Like InfoPanel, handle_event() returns True for every event while
    the dialog is open so nothing underneath reacts.

    The owning screen supplies two callbacks:
        capture() -> (mode, data)   the current structure as a
                                    JSON-serializable dict; `mode` is
                                    the active mode or None.
        restore(mode, data)         apply a loaded structure. It MUST
                                    validate everything before changing
                                    the screen and raise ValueError (or
                                    TypeError/KeyError) on bad data, so a
                                    failed load never leaves a
                                    half-applied structure behind.
    """

    _open_count = 0

    PANEL_WIDTH = 760
    PANEL_HEIGHT = 560
    ROW_HEIGHT = 32
    VISIBLE_ROWS = 7
    DOUBLE_CLICK_MS = 400

    @classmethod
    def any_open(cls) -> bool:
        """True while any FileDialog is showing.

        Application uses this so Escape closes the dialog instead of
        quitting the whole app.
        """
        return cls._open_count > 0

    def __init__(
        self,
        surface_size: tuple[int, int],
        topic: str,
        label: str,
        capture: Capture,
        restore: Restore,
        on_done: Callable[[str], None] | None = None,
        store: ExportStore | None = None,
    ) -> None:
        self.topic = topic
        self.label = label
        self.capture = capture
        self.restore = restore
        self.on_done = on_done
        self._store = store

        self.title_font = Font.H1()
        self.label_font = Font.H2()
        self.body_font = Font.BODY()
        self.small_font = Font.SMALL()

        width, height = surface_size
        self.panel = pygame.Rect(
            (width - self.PANEL_WIDTH) // 2,
            (height - self.PANEL_HEIGHT) // 2,
            self.PANEL_WIDTH,
            self.PANEL_HEIGHT,
        )
        self._build_widgets()

        self._visible = False
        self._mode = "save"
        self._view = "files"

        self._files: list[SavedFile] = []
        self._selected: int | None = None
        self._scroll = 0
        self._last_click: tuple[int, int] | None = None

        self._browse_dir = Path.home()
        self._subdirs: list[Path] = []

        self._pending_overwrite: str | None = None
        self._message = ""
        self._message_kind = "info"

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------

    def _build_widgets(self) -> None:
        panel = self.panel
        left = panel.x + 24
        inner_width = panel.width - 48
        button_y = panel.bottom - 24 - 38

        self.close_rect = pygame.Rect(panel.right - 44, panel.y + 14, 28, 28)

        # Files view.
        self.change_button = Button(
            pygame.Rect(panel.right - 24 - 140, panel.y + 66, 140, 32),
            "Change Folder",
        )
        self.filename_input = TextInput(
            pygame.Rect(panel.x + 110, panel.y + 112, 380, 32),
            max_length=MAX_FILENAME_LENGTH,
            allowed=is_allowed_name_character,
            placeholder="file name",
        )
        self.extension_position = (panel.x + 498, panel.y + 117)
        self.primary_button = Button(
            pygame.Rect(panel.right - 24 - 110 - 10 - 130, button_y, 130, 38),
            "Save",
            variant="primary",
        )
        cancel_rect = pygame.Rect(panel.right - 24 - 110, button_y, 110, 38)
        self.cancel_button = Button(cancel_rect, "Cancel")

        # Folder browser view.
        self.path_input = TextInput(
            pygame.Rect(left, panel.y + 66, inner_width - 78, 32),
            max_length=400,
            placeholder="type a folder path",
        )
        self.go_button = Button(
            pygame.Rect(panel.right - 24 - 70, panel.y + 66, 70, 32), "Go"
        )
        self.up_button = Button(pygame.Rect(left, panel.y + 112, 80, 32), "Up")
        self.default_button = Button(
            pygame.Rect(left + 88, panel.y + 112, 170, 32), "Reset to Default"
        )
        self.use_button = Button(
            pygame.Rect(panel.right - 24 - 110 - 10 - 170, button_y, 170, 38),
            "Use This Folder",
            variant="primary",
        )
        self.back_button = Button(cancel_rect.copy(), "Back")

        # Shared areas.
        self.list_rect = pygame.Rect(
            left, panel.y + 172, inner_width, self.ROW_HEIGHT * self.VISIBLE_ROWS
        )
        self.message_rect = pygame.Rect(
            left, self.list_rect.bottom + 10, inner_width, 56
        )

    # ------------------------------------------------------------------
    # Open / close
    # ------------------------------------------------------------------

    @property
    def store(self) -> ExportStore:
        return self._store if self._store is not None else get_store()

    @property
    def visible(self) -> bool:
        return self._visible

    def open(self, mode: str) -> None:
        """Show the dialog as "save" or "load"."""

        if mode not in ("save", "load"):
            raise ValueError(f"Unknown dialog mode: {mode!r}")

        if not self._visible:
            FileDialog._open_count += 1

        self._visible = True
        self._mode = mode
        self._view = "files"
        self._pending_overwrite = None
        self._set_message("", "info")
        self._refresh_files()

        self.path_input.blur()

        if mode == "save":
            current_mode, _ = self.capture()
            self.filename_input.set_text(
                self.store.suggest_stem(self.topic, current_mode)
            )
            self.filename_input.focus()
        else:
            self.filename_input.blur()

        self._update_primary()

    def close(self) -> None:
        if self._visible:
            FileDialog._open_count = max(0, FileDialog._open_count - 1)

        self._visible = False
        self.filename_input.blur()
        self.path_input.blur()

    # ------------------------------------------------------------------
    # Events
    # ------------------------------------------------------------------

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Returns True for every event while visible (modal)."""

        if not self._visible:
            return False

        if event.type == pygame.MOUSEWHEEL:
            if self.list_rect.collidepoint(pygame.mouse.get_pos()):
                self._scroll_by(-event.y)

            return True

        if event.type == pygame.KEYDOWN:
            self._handle_key(event)
            return True

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.close_rect.collidepoint(event.pos):
                self.close()
                return True

            if self._view == "files":
                if self._mode == "save":
                    self.filename_input.handle_event(event)
            else:
                self.path_input.handle_event(event)

            self._handle_list_click(event.pos)

        # Buttons see both the press and the release. Stop at the first
        # one that fires, since an action may switch views.
        for button, action in self._buttons_and_actions():
            if button.handle_event(event):
                action()
                break

        return True

    def _buttons_and_actions(self) -> list[tuple[Button, Callable[[], None]]]:
        if self._view == "files":
            return [
                (self.primary_button, self._primary),
                (self.cancel_button, self.close),
                (self.change_button, self._open_folder_view),
            ]

        return [
            (self.use_button, self._use_folder),
            (self.back_button, self._back_to_files),
            (self.go_button, self._go),
            (self.up_button, self._up),
            (self.default_button, self._reset_folder),
        ]

    def _handle_key(self, event: pygame.event.Event) -> None:
        if event.key == pygame.K_ESCAPE:
            if self._view == "folders":
                self._back_to_files()
            else:
                self.close()

            return

        active_input = self._active_input()

        if active_input is not None and active_input.active:
            result = active_input.handle_event(event)

            if result == "changed" and active_input is self.filename_input:
                self._on_name_edited()
            elif result == "submit":
                if self._view == "folders":
                    self._go()
                else:
                    self._primary()

            return

        if self._view != "files":
            return

        if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            self._primary()
        elif self._mode == "load" and event.key == pygame.K_UP:
            self._move_selection(-1)
        elif self._mode == "load" and event.key == pygame.K_DOWN:
            self._move_selection(1)

    def _active_input(self) -> TextInput | None:
        if self._view == "folders":
            return self.path_input

        if self._mode == "save":
            return self.filename_input

        return None

    def _handle_list_click(self, position: tuple[int, int]) -> None:
        if not self.list_rect.collidepoint(position):
            return

        row = (position[1] - self.list_rect.y) // self.ROW_HEIGHT + self._scroll

        if self._view == "folders":
            if 0 <= row < len(self._subdirs):
                self._enter_folder(self._subdirs[row])

            return

        if not 0 <= row < len(self._files):
            return

        file = self._files[row]

        if self._mode == "save":
            # Clicking an existing file reuses its name; saving then
            # asks before replacing it.
            self.filename_input.set_text(file.name)
            self._on_name_edited()
            return

        if not self._compatible(file):
            self._set_message(self._incompatible_reason(file), "warn")
            return

        now = pygame.time.get_ticks()

        if (
            self._selected == row
            and self._last_click is not None
            and self._last_click[0] == row
            and now - self._last_click[1] <= self.DOUBLE_CLICK_MS
        ):
            self._do_load()
            return

        self._selected = row
        self._last_click = (row, now)
        self._set_message("", "info")
        self._update_primary()

    # ------------------------------------------------------------------
    # Files view
    # ------------------------------------------------------------------

    def _compatible(self, file: SavedFile) -> bool:
        return file.topic == self.topic

    def _incompatible_reason(self, file: SavedFile) -> str:
        if file.error is not None:
            return file.error

        return (
            f"'{file.name}' was saved from the '{file.topic}' screen, "
            "so it cannot be loaded here."
        )

    def _refresh_files(self) -> None:
        self._files = self.store.list_files()
        self._scroll = 0
        self._selected = None
        self._last_click = None

        if self._mode == "load":
            for index, file in enumerate(self._files):
                if self._compatible(file):
                    self._selected = index
                    break

    def _move_selection(self, step: int) -> None:
        candidates = [
            index for index, file in enumerate(self._files)
            if self._compatible(file)
        ]

        if not candidates:
            return

        if self._selected not in candidates:
            target = candidates[0] if step > 0 else candidates[-1]
        else:
            position = candidates.index(self._selected) + step
            target = candidates[max(0, min(len(candidates) - 1, position))]

        self._selected = target

        # Keep the selection inside the visible window.
        if target < self._scroll:
            self._scroll = target
        elif target >= self._scroll + self.VISIBLE_ROWS:
            self._scroll = target - self.VISIBLE_ROWS + 1

        self._update_primary()

    def _on_name_edited(self) -> None:
        self._pending_overwrite = None

        if self._message_kind == "warn":
            self._set_message("", "info")

        self._update_primary()

    def _update_primary(self) -> None:
        if self._mode == "save":
            self.primary_button.label = (
                "Overwrite" if self._pending_overwrite else "Save"
            )
            self.primary_button.enabled = True
        else:
            self.primary_button.label = "Load"
            self.primary_button.enabled = self._selected is not None

    def _primary(self) -> None:
        if self._mode == "save":
            self._do_save()
        else:
            self._do_load()

    def _do_save(self) -> None:
        try:
            stem = clean_filename(self.filename_input.text)
        except StorageError as error:
            self._set_message(str(error), "error")
            return

        overwrite = self._pending_overwrite == stem

        if not overwrite and self.store.exists(stem):
            self._ask_overwrite(stem)
            return

        try:
            mode, data = self.capture()
            path = self.store.save(
                stem, self.topic, mode, data, overwrite=overwrite
            )
        except FileExistsStorageError:
            self._ask_overwrite(stem)
            return
        except StorageError as error:
            self._set_message(str(error), "error")
            return
        except (TypeError, ValueError) as error:
            self._set_message(
                f"This structure could not be prepared for saving: {error}",
                "error",
            )
            return

        self.close()
        self._finish(f"Saved {path.name}")

    def _ask_overwrite(self, stem: str) -> None:
        self._pending_overwrite = stem
        self._set_message(
            f"'{stem}.json' already exists. Click Overwrite to replace it, "
            "or change the name.",
            "warn",
        )
        self._update_primary()

    def _do_load(self) -> None:
        if self._selected is None or not 0 <= self._selected < len(self._files):
            self._set_message("Select a file to load first.", "warn")
            return

        file = self._files[self._selected]

        if not self._compatible(file):
            self._set_message(self._incompatible_reason(file), "warn")
            return

        try:
            envelope = self.store.load(file.path, expected_topic=self.topic)
            self.restore(envelope.mode, envelope.data)
        except StorageError as error:
            self._set_message(str(error), "error")
            return
        except (ValueError, TypeError, KeyError) as error:
            self._set_message(
                f"'{file.path.name}' contains invalid data: {error}", "error"
            )
            return

        self.close()
        self._finish(f"Loaded {file.path.name}")

    def _finish(self, message: str) -> None:
        if self.on_done is not None:
            self.on_done(message)

    # ------------------------------------------------------------------
    # Folder view
    # ------------------------------------------------------------------

    def _open_folder_view(self) -> None:
        self._view = "folders"
        self._set_message("", "info")
        self._go_to(self._nearest_existing(self.store.directory))
        self.filename_input.blur()
        self.path_input.blur()

    def _back_to_files(self) -> None:
        self._view = "files"
        self._scroll = 0
        self._set_message("", "info")

        if self._mode == "save":
            self.filename_input.focus()

        self._refresh_files()
        self._update_primary()

    @staticmethod
    def _nearest_existing(path: Path) -> Path:
        candidate = path

        while not candidate.is_dir():
            if candidate.parent == candidate:
                return Path.home()

            candidate = candidate.parent

        return candidate

    def _go_to(self, directory: Path) -> None:
        self._browse_dir = directory
        self._scroll = 0
        self.path_input.set_text(str(directory))

        try:
            self._subdirs = sorted(
                (
                    entry
                    for entry in directory.iterdir()
                    if entry.is_dir() and not entry.name.startswith(".")
                ),
                key=lambda entry: entry.name.lower(),
            )
        except OSError as error:
            self._subdirs = []
            self._set_message(
                f"Cannot read this folder: {error.strerror or error}", "error"
            )

    def _enter_folder(self, directory: Path) -> None:
        self._set_message("", "info")
        self._go_to(directory)

    def _go(self) -> None:
        text = self.path_input.text.strip()

        if not text:
            self._set_message("Type a folder path first.", "warn")
            return

        candidate = Path(text).expanduser()

        try:
            is_folder = candidate.is_dir()
        except OSError:
            is_folder = False

        if not is_folder:
            self._set_message("That folder does not exist.", "error")
            return

        self._set_message("", "info")
        self._go_to(candidate.resolve())

    def _up(self) -> None:
        parent = self._browse_dir.parent

        if parent == self._browse_dir:
            self._set_message("This is the top of the file system.", "info")
            return

        self._set_message("", "info")
        self._go_to(parent)

    def _use_folder(self) -> None:
        try:
            remembered = self.store.set_directory(self._browse_dir)
        except StorageError as error:
            self._set_message(str(error), "error")
            return

        self._after_folder_change("Export folder changed.", remembered)

    def _reset_folder(self) -> None:
        remembered = self.store.reset_directory()

        self._after_folder_change("Using the default export folder.", remembered)

    def _after_folder_change(self, message: str, remembered: bool) -> None:
        self._view = "files"
        self._pending_overwrite = None
        self._refresh_files()

        if remembered:
            self._set_message(message, "info")
        else:
            self._set_message(
                message + " It could not be remembered for next time.", "warn"
            )

        if self._mode == "save":
            self.filename_input.focus()

        self._update_primary()

    # ------------------------------------------------------------------
    # Shared helpers
    # ------------------------------------------------------------------

    def _set_message(self, text: str, kind: str) -> None:
        self._message = text
        self._message_kind = kind

    def _current_rows(self) -> list:
        return self._subdirs if self._view == "folders" else self._files

    def _scroll_by(self, delta: int) -> None:
        maximum = max(0, len(self._current_rows()) - self.VISIBLE_ROWS)
        self._scroll = max(0, min(maximum, self._scroll + delta))

    # ------------------------------------------------------------------
    # Update / render
    # ------------------------------------------------------------------

    def update(self, dt: float) -> None:
        if not self._visible:
            return

        for button in (
            self.change_button, self.primary_button, self.cancel_button,
            self.go_button, self.up_button, self.default_button,
            self.use_button, self.back_button,
        ):
            button.update(dt)

    def render(self, surface: pygame.Surface) -> None:
        if not self._visible:
            return

        width, height = surface.get_size()

        backdrop = pygame.Surface((width, height), pygame.SRCALPHA)
        backdrop.fill((0, 0, 0, 170))
        surface.blit(backdrop, (0, 0))

        pygame.draw.rect(
            surface, Color.SURFACE_RAISED, self.panel, border_radius=Radius.LG
        )
        pygame.draw.rect(
            surface, Color.BORDER, self.panel, 2, border_radius=Radius.LG
        )

        if self._view == "files":
            title = f"{'Save' if self._mode == 'save' else 'Load'} {self.label}"
        else:
            title = "Choose Export Folder"

        self._draw_text(
            surface, title, (self.panel.x + 24, self.panel.y + 16),
            self.title_font, Color.TEXT_PRIMARY,
        )

        pygame.draw.rect(
            surface, Color.STATE_DANGER, self.close_rect, border_radius=Radius.SM
        )
        close_label = self.label_font.render("x", True, Color.TEXT_PRIMARY)
        surface.blit(
            close_label, close_label.get_rect(center=self.close_rect.center)
        )

        if self._view == "files":
            self._render_files_view(surface)
        else:
            self._render_folders_view(surface)

        self._render_message(surface)

    def _render_files_view(self, surface: pygame.Surface) -> None:
        panel = self.panel

        self._draw_text(
            surface, "Folder", (panel.x + 24, panel.y + 72),
            self.label_font, Color.TEXT_SECONDARY,
        )
        path_left = panel.x + 110
        path_width = self.change_button.rect.x - 12 - path_left
        self._draw_text(
            surface,
            self._fit_left(str(self.store.directory), self.body_font, path_width),
            (path_left, panel.y + 74),
            self.body_font,
            Color.TEXT_PRIMARY,
        )
        self.change_button.render(surface)

        if self._mode == "save":
            self._draw_text(
                surface, "Name", (panel.x + 24, panel.y + 118),
                self.label_font, Color.TEXT_SECONDARY,
            )
            self.filename_input.render(surface)
            self._draw_text(
                surface, ".json", self.extension_position,
                self.body_font, Color.TEXT_SECONDARY,
            )
            header = "Existing files (click one to reuse its name)"
        else:
            self._draw_text(
                surface,
                "Select a file, then click Load. Files from other screens "
                "are dimmed.",
                (panel.x + 24, panel.y + 122),
                self.small_font,
                Color.TEXT_MUTED,
            )
            header = "Saved files"

        self._draw_text(
            surface, header, (panel.x + 24, panel.y + 150),
            self.small_font, Color.TEXT_SECONDARY,
        )

        self._render_list(surface)

        self.primary_button.render(surface)
        self.cancel_button.render(surface)

    def _render_folders_view(self, surface: pygame.Surface) -> None:
        panel = self.panel

        self.path_input.render(surface)
        self.go_button.render(surface)
        self.up_button.render(surface)
        self.default_button.render(surface)

        self._draw_text(
            surface, "Folders inside this folder (click one to open it)",
            (panel.x + 24, panel.y + 150), self.small_font,
            Color.TEXT_SECONDARY,
        )

        self._render_list(surface)

        self.use_button.render(surface)
        self.back_button.render(surface)

    def _render_list(self, surface: pygame.Surface) -> None:
        rect = self.list_rect
        rows = self._current_rows()

        pygame.draw.rect(surface, Color.SURFACE, rect, border_radius=Radius.SM)
        pygame.draw.rect(
            surface, Color.BORDER_SOFT, rect, 1, border_radius=Radius.SM
        )

        if not rows:
            empty = (
                "No subfolders here."
                if self._view == "folders"
                else "No saved files in this folder yet."
            )
            text = self.body_font.render(empty, True, Color.TEXT_MUTED)
            surface.blit(text, text.get_rect(center=rect.center))
            return

        mouse = pygame.mouse.get_pos()
        first = self._scroll
        last = min(len(rows), first + self.VISIBLE_ROWS)

        for position, index in enumerate(range(first, last)):
            row_rect = pygame.Rect(
                rect.x + 3,
                rect.y + position * self.ROW_HEIGHT + 2,
                rect.width - 14,
                self.ROW_HEIGHT - 4,
            )

            if self._view == "folders":
                self._render_folder_row(surface, row_rect, rows[index], mouse)
            else:
                self._render_file_row(surface, row_rect, index, rows[index], mouse)

        if len(rows) > self.VISIBLE_ROWS:
            self._render_scrollbar(surface, len(rows))

    def _render_file_row(
        self,
        surface: pygame.Surface,
        row_rect: pygame.Rect,
        index: int,
        file: SavedFile,
        mouse: tuple[int, int],
    ) -> None:
        usable = self._mode == "save" or self._compatible(file)
        selected = self._mode == "load" and index == self._selected

        if selected:
            pygame.draw.rect(
                surface, Color.ACCENT_SOFT, row_rect, border_radius=Radius.SM
            )
            pygame.draw.rect(
                surface, Color.ACCENT, row_rect, 1, border_radius=Radius.SM
            )
        elif usable and row_rect.collidepoint(mouse):
            pygame.draw.rect(
                surface, Color.SURFACE_RAISED, row_rect, border_radius=Radius.SM
            )

        if file.error is not None:
            tag = "not a valid save"
        elif file.mode:
            tag = f"{file.topic} / {file.mode}"
        else:
            tag = str(file.topic)

        name_color = Color.TEXT_PRIMARY if usable else Color.TEXT_MUTED
        tag_color = Color.TEXT_SECONDARY if usable else Color.TEXT_MUTED

        tag_surface = self.small_font.render(tag, True, tag_color)
        tag_x = row_rect.right - 10 - tag_surface.get_width()
        name = self._fit_right(
            file.name, self.body_font, tag_x - row_rect.x - 24
        )

        name_surface = self.body_font.render(name, True, name_color)
        surface.blit(
            name_surface,
            (row_rect.x + 10, row_rect.centery - name_surface.get_height() // 2),
        )
        surface.blit(
            tag_surface,
            (tag_x, row_rect.centery - tag_surface.get_height() // 2),
        )

    def _render_folder_row(
        self,
        surface: pygame.Surface,
        row_rect: pygame.Rect,
        directory: Path,
        mouse: tuple[int, int],
    ) -> None:
        if row_rect.collidepoint(mouse):
            pygame.draw.rect(
                surface, Color.SURFACE_RAISED, row_rect, border_radius=Radius.SM
            )

        name = self._fit_right(
            f"> {directory.name}", self.body_font, row_rect.width - 20
        )
        text = self.body_font.render(name, True, Color.TEXT_PRIMARY)
        surface.blit(
            text, (row_rect.x + 10, row_rect.centery - text.get_height() // 2)
        )

    def _render_scrollbar(self, surface: pygame.Surface, total: int) -> None:
        track = pygame.Rect(
            self.list_rect.right - 9, self.list_rect.y + 4,
            4, self.list_rect.height - 8,
        )
        pygame.draw.rect(
            surface, Color.BORDER_SOFT, track, border_radius=2
        )

        visible_fraction = self.VISIBLE_ROWS / total
        thumb_height = max(20, int(track.height * visible_fraction))
        scrollable = total - self.VISIBLE_ROWS
        thumb_y = track.y + int(
            (track.height - thumb_height) * (self._scroll / scrollable)
        )
        pygame.draw.rect(
            surface, Color.BORDER,
            pygame.Rect(track.x, thumb_y, track.width, thumb_height),
            border_radius=2,
        )

    def _render_message(self, surface: pygame.Surface) -> None:
        if not self._message:
            return

        color = {
            "error": Color.STATE_DANGER,
            "warn": Color.STATE_COMPARING,
            "success": Color.STATE_SUCCESS,
        }.get(self._message_kind, Color.TEXT_SECONDARY)

        self._draw_wrapped(
            surface, self._message, self.message_rect, self.small_font, color
        )

    # ------------------------------------------------------------------
    # Text helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _draw_text(surface, text, position, font, color) -> None:
        surface.blit(font.render(text, True, color), position)

    @staticmethod
    def _fit_right(text: str, font: pygame.font.Font, max_width: int) -> str:
        """Shorten `text` with '...' at the end so it fits `max_width`."""

        if font.size(text)[0] <= max_width:
            return text

        while text and font.size(text + "...")[0] > max_width:
            text = text[:-1]

        return text + "..."

    @staticmethod
    def _fit_left(text: str, font: pygame.font.Font, max_width: int) -> str:
        """Shorten `text` with '...' at the start, keeping the end (the
        most specific part of a path) visible."""

        if font.size(text)[0] <= max_width:
            return text

        while text and font.size("..." + text)[0] > max_width:
            text = text[1:]

        return "..." + text

    @staticmethod
    def _draw_wrapped(surface, text, rect, font, color) -> None:
        lines: list[str] = []
        current = ""

        for word in text.split():
            trial = word if not current else f"{current} {word}"

            if font.size(trial)[0] <= rect.width:
                current = trial
            else:
                if current:
                    lines.append(current)

                current = word

        if current:
            lines.append(current)

        y = rect.y

        for line in lines:
            if y + font.get_height() > rect.bottom:
                break

            surface.blit(font.render(line, True, color), (rect.x, y))
            y += font.get_height()