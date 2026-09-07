import pytest

from algolab.core.configuration import Configuration


def test_configuration_loads_toml(tmp_path):
    config_file = tmp_path / "config.toml"

    config_file.write_text(
        """
[window]
width = 1280
height = 720
title = "AlgoLab"
resizable = true

[performance]
fps = 60
""",
        encoding="utf-8",
    )

    config = Configuration(config_file)

    assert config.window["width"] == 1280
    assert config.window["height"] == 720
    assert config.window["title"] == "AlgoLab"
    assert config.window["resizable"] is True
    assert config.performance["fps"] == 60


def test_configuration_raises_for_missing_file(tmp_path):
    config_file = tmp_path / "missing.toml"

    with pytest.raises(FileNotFoundError):
        Configuration(config_file)