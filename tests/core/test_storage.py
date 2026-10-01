import json
from datetime import date

import pytest

from algolab.core.storage import (
    FILE_EXTENSION,
    FORMAT_VERSION,
    ExportStore,
    FileExistsStorageError,
    StorageError,
    clean_filename,
    is_allowed_name_character,
)


@pytest.fixture
def store(tmp_path):
    return ExportStore(tmp_path / "exports", tmp_path / "settings.json")


# ----------------------------------------------------------------------
# File names
# ----------------------------------------------------------------------


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("my stack", "my stack"),
        ("  padded  ", "padded"),
        ("data.json", "data"),
        ("DATA.JSON", "DATA"),
        ("v1.2 (final)", "v1.2 (final)"),
        ("caf\u00e9", "caf\u00e9"),
    ],
)
def test_clean_filename_accepts_safe_names(raw, expected):
    assert clean_filename(raw) == expected


@pytest.mark.parametrize(
    "raw",
    [
        "",
        "   ",
        ".json",
        "../escape",
        "a/b",
        "a\\b",
        'quote"d',
        "star*",
        "what?",
        "colon:name",
        ".hidden",
        "trailing.",
        "CON",
        "nul.txt",
        "x" * 81,
    ],
)
def test_clean_filename_rejects_unsafe_names(raw):
    with pytest.raises(StorageError):
        clean_filename(raw)


def test_typed_character_filter_matches_name_rules():
    assert is_allowed_name_character("a")
    assert is_allowed_name_character(" ")
    assert is_allowed_name_character("-")
    assert not is_allowed_name_character("/")
    assert not is_allowed_name_character("\\")
    assert not is_allowed_name_character("*")


# ----------------------------------------------------------------------
# Save and load
# ----------------------------------------------------------------------


def test_save_then_load_round_trips(store):
    path = store.save("first", "stack", None, {"items": [1, 2, 3]})

    assert path == store.directory / "first.json"

    envelope = store.load(path, expected_topic="stack")

    assert envelope.topic == "stack"
    assert envelope.mode is None
    assert envelope.data == {"items": [1, 2, 3]}
    assert envelope.saved_at


def test_save_creates_the_export_folder_on_demand(store):
    assert not store.directory.exists()

    store.save("first", "stack", None, {"items": []})

    assert store.directory.is_dir()


def test_saved_file_has_a_versioned_envelope(store):
    path = store.save("first", "bst", "avl", {"root": None})

    raw = json.loads(path.read_text(encoding="utf-8"))

    assert raw["app"] == "AlgoLab"
    assert raw["version"] == FORMAT_VERSION
    assert raw["topic"] == "bst"
    assert raw["mode"] == "avl"
    assert raw["data"] == {"root": None}


def test_extension_is_added_once(store):
    path = store.save("name.json", "stack", None, {"items": []})

    assert path.name == "name" + FILE_EXTENSION


def test_save_refuses_to_overwrite_by_default(store):
    store.save("same", "stack", None, {"items": [1]})

    with pytest.raises(FileExistsStorageError):
        store.save("same", "stack", None, {"items": [2]})

    assert store.load("same.json").data == {"items": [1]}


def test_save_can_overwrite_when_asked(store):
    store.save("same", "stack", None, {"items": [1]})
    store.save("same", "stack", None, {"items": [2]}, overwrite=True)

    assert store.load("same.json").data == {"items": [2]}


def test_failed_save_leaves_no_temporary_file(store):
    with pytest.raises(StorageError):
        store.save("bad", "stack", None, {"items": [object()]})

    assert not store.directory.exists() or list(store.directory.glob("*")) == []


def test_nan_is_rejected_rather_than_written_as_invalid_json(store):
    with pytest.raises(StorageError):
        store.save("nan", "stack", None, {"items": [float("nan")]})


def test_unsafe_name_never_writes_outside_the_folder(store, tmp_path):
    with pytest.raises(StorageError):
        store.save("../../evil", "stack", None, {"items": []})

    assert not (tmp_path / "evil.json").exists()


def test_relative_names_resolve_inside_the_export_folder(store):
    store.save("inside", "stack", None, {"items": [7]})

    assert store.load("inside.json").data == {"items": [7]}


# ----------------------------------------------------------------------
# Loading bad files
# ----------------------------------------------------------------------


def _write(store, name, text):
    store.directory.mkdir(parents=True, exist_ok=True)
    path = store.directory / name
    path.write_text(text, encoding="utf-8")
    return path


def test_load_missing_file_is_a_storage_error(store):
    with pytest.raises(StorageError, match="no longer exists"):
        store.load("nothing.json")


def test_load_rejects_invalid_json(store):
    path = _write(store, "broken.json", "{not json")

    with pytest.raises(StorageError, match="not valid JSON"):
        store.load(path)


def test_load_rejects_non_algolab_json(store):
    path = _write(store, "other.json", json.dumps({"hello": "world"}))

    with pytest.raises(StorageError, match="not an AlgoLab save"):
        store.load(path)


def test_load_rejects_a_list_at_the_top_level(store):
    path = _write(store, "list.json", "[1, 2, 3]")

    with pytest.raises(StorageError, match="not an AlgoLab save"):
        store.load(path)


def test_load_rejects_newer_versions(store):
    envelope = {
        "app": "AlgoLab", "version": FORMAT_VERSION + 1,
        "topic": "stack", "mode": None, "data": {},
    }
    path = _write(store, "future.json", json.dumps(envelope))

    with pytest.raises(StorageError, match="newer version"):
        store.load(path)


@pytest.mark.parametrize("version", [0, -1, "1", True, None, 1.5])
def test_load_rejects_invalid_versions(store, version):
    envelope = {
        "app": "AlgoLab", "version": version,
        "topic": "stack", "mode": None, "data": {},
    }
    path = _write(store, "v.json", json.dumps(envelope))

    with pytest.raises(StorageError, match="invalid version"):
        store.load(path)


def test_load_rejects_a_file_from_another_screen(store):
    store.save("tree", "bst", None, {"root": None})

    with pytest.raises(StorageError, match="'bst' screen, not 'stack'"):
        store.load("tree.json", expected_topic="stack")


def test_load_without_expected_topic_accepts_any_topic(store):
    store.save("tree", "bst", None, {"root": None})

    assert store.load("tree.json").topic == "bst"


def test_load_rejects_missing_or_malformed_fields(store):
    base = {"app": "AlgoLab", "version": 1, "topic": "stack", "mode": None, "data": {}}

    for name, change in [
        ("no_topic", {"topic": None}),
        ("empty_topic", {"topic": ""}),
        ("bad_mode", {"mode": 5}),
        ("no_data", {"data": None}),
        ("list_data", {"data": [1]}),
    ]:
        path = _write(store, name + ".json", json.dumps({**base, **change}))

        with pytest.raises(StorageError):
            store.load(path)


def test_load_rejects_binary_files(store):
    store.directory.mkdir(parents=True)
    path = store.directory / "binary.json"
    path.write_bytes(b"\xff\xfe\x00\x01\x80")

    with pytest.raises(StorageError, match="not a text file"):
        store.load(path)


def test_load_rejects_oversized_files(store):
    path = _write(store, "huge.json", " " * (5 * 1024 * 1024 + 1))

    with pytest.raises(StorageError, match="too large"):
        store.load(path)


def test_load_rejects_absurdly_deep_nesting(store):
    path = _write(store, "deep.json", "[" * 100000 + "]" * 100000)

    with pytest.raises(StorageError):
        store.load(path)


# ----------------------------------------------------------------------
# Listing
# ----------------------------------------------------------------------


def test_list_files_is_empty_for_a_missing_folder(store):
    assert store.list_files() == []


def test_list_files_reports_topic_mode_and_problems(store):
    store.save("a_stack", "stack", None, {"items": []})
    store.save("a_tree", "bst", "avl", {"root": None})
    _write(store, "junk.json", "{nope")
    _write(store, "notes.txt", "ignored, not .json")

    by_name = {file.name: file for file in store.list_files()}

    assert set(by_name) == {"a_stack", "a_tree", "junk"}
    assert (by_name["a_stack"].topic, by_name["a_stack"].mode) == ("stack", None)
    assert (by_name["a_tree"].topic, by_name["a_tree"].mode) == ("bst", "avl")
    assert by_name["junk"].topic is None
    assert "not valid JSON" in by_name["junk"].error


def test_list_files_is_newest_first(store):
    import os

    first = store.save("older", "stack", None, {"items": []})
    second = store.save("newer", "stack", None, {"items": []})
    os.utime(first, (1_000_000, 1_000_000))
    os.utime(second, (2_000_000, 2_000_000))

    assert [file.name for file in store.list_files()] == ["newer", "older"]


def test_list_files_respects_the_limit(store):
    for number in range(5):
        store.save(f"f{number}", "stack", None, {"items": []})

    assert len(store.list_files(limit=3)) == 3


# ----------------------------------------------------------------------
# Suggested names
# ----------------------------------------------------------------------


def test_suggest_stem_includes_topic_mode_and_date(store):
    assert store.suggest_stem("stack", today=date(2026, 9, 30)) == "stack-2026-09-30"
    assert store.suggest_stem("bst", "avl", today=date(2026, 9, 30)) == "bst-avl-2026-09-30"


def test_suggest_stem_skips_a_mode_that_repeats_the_topic(store):
    assert store.suggest_stem("bst", "bst", today=date(2026, 9, 30)) == "bst-2026-09-30"


def test_suggest_stem_avoids_existing_files(store):
    today = date(2026, 9, 30)

    store.save("stack-2026-09-30", "stack", None, {"items": []})
    assert store.suggest_stem("stack", today=today) == "stack-2026-09-30-2"

    store.save("stack-2026-09-30-2", "stack", None, {"items": []})
    assert store.suggest_stem("stack", today=today) == "stack-2026-09-30-3"


def test_suggested_names_are_always_valid(store):
    assert clean_filename(store.suggest_stem("linked_list", "singly"))


# ----------------------------------------------------------------------
# Choosing and remembering the export folder
# ----------------------------------------------------------------------


def test_default_folder_is_used_at_first(store, tmp_path):
    assert store.directory == (tmp_path / "exports")
    assert store.is_default


def test_set_directory_changes_where_files_go(store, tmp_path):
    other = tmp_path / "elsewhere"
    other.mkdir()

    assert store.set_directory(other) is True

    path = store.save("here", "stack", None, {"items": []})

    assert path.parent == other.resolve()
    assert not store.is_default


def test_chosen_folder_is_remembered_by_the_next_store(store, tmp_path):
    other = tmp_path / "elsewhere"
    other.mkdir()
    store.set_directory(other)

    next_run = ExportStore(tmp_path / "exports", tmp_path / "settings.json")

    assert next_run.directory == other.resolve()


def test_reset_directory_returns_to_default_and_forgets_the_choice(store, tmp_path):
    other = tmp_path / "elsewhere"
    other.mkdir()
    store.set_directory(other)

    store.reset_directory()

    assert store.is_default
    assert ExportStore(tmp_path / "exports", tmp_path / "settings.json").is_default


def test_set_directory_rejects_missing_folders_and_keeps_the_old_one(store, tmp_path):
    before = store.directory

    with pytest.raises(StorageError, match="not an existing folder"):
        store.set_directory(tmp_path / "does_not_exist")

    assert store.directory == before


def test_set_directory_rejects_a_file(store, tmp_path):
    a_file = tmp_path / "file.txt"
    a_file.write_text("x")

    with pytest.raises(StorageError):
        store.set_directory(a_file)


def test_remembered_folder_that_disappeared_falls_back_to_default(store, tmp_path):
    other = tmp_path / "elsewhere"
    other.mkdir()
    store.set_directory(other)
    other.rmdir()

    next_run = ExportStore(tmp_path / "exports", tmp_path / "settings.json")

    assert next_run.is_default


def test_corrupt_settings_file_is_ignored(tmp_path):
    (tmp_path / "settings.json").write_text("{corrupt")

    store = ExportStore(tmp_path / "exports", tmp_path / "settings.json")

    assert store.is_default


def test_unwritable_settings_still_changes_folder_for_this_session(tmp_path):
    blocker = tmp_path / "blocker"
    blocker.write_text("a file where a folder is needed")
    store = ExportStore(tmp_path / "exports", blocker / "settings.json")

    other = tmp_path / "elsewhere"
    other.mkdir()

    assert store.set_directory(other) is False
    assert store.directory == other.resolve()


def test_settings_keep_unrelated_keys(tmp_path):
    settings = tmp_path / "settings.json"
    settings.write_text(json.dumps({"theme": "dark"}))
    store = ExportStore(tmp_path / "exports", settings)

    other = tmp_path / "elsewhere"
    other.mkdir()
    store.set_directory(other)

    saved = json.loads(settings.read_text())

    assert saved["theme"] == "dark"
    assert saved["export_directory"] == str(other.resolve())