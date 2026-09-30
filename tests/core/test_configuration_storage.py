from pathlib import Path

from algolab.core.configuration import (
    Configuration,
    get_app_dir,
)

BASE = '[window]\nwidth = 1\nheight = 1\ntitle = "t"\nresizable = true\n[performance]\nfps = 30\n'


def _config(tmp_path, extra=""):
    path = tmp_path / "config.toml"
    path.write_text(BASE + extra, encoding="utf-8")

    return Configuration(path)


def test_export_directory_defaults_to_exports_in_the_app_folder(tmp_path):
    config = _config(tmp_path)

    assert config.storage == {}
    assert config.export_directory == get_app_dir() / "exports"


def test_relative_export_directory_is_resolved_against_the_app_folder(tmp_path):
    config = _config(tmp_path, '[storage]\nexport_directory = "my_saves"\n')

    assert config.export_directory == get_app_dir() / "my_saves"


def test_absolute_export_directory_is_used_as_is(tmp_path):
    target = tmp_path / "somewhere"
    config = _config(tmp_path, f'[storage]\nexport_directory = "{target.as_posix()}"\n')

    assert config.export_directory == Path(target.as_posix())