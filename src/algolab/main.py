from pathlib import Path

from algolab.core.application import Application
from algolab.core.configuration import Configuration


def main() -> None:
    project_root = Path(__file__).resolve().parents[2]
    config_path = project_root / "config" / "config.toml"

    config = Configuration(config_path)
    app = Application(config)

    app.run()


if __name__ == "__main__":
    main()