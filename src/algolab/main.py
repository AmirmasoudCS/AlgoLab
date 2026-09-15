from algolab.core.application import Application
from algolab.core.configuration import Configuration, get_resource_path


def main() -> None:
    config_path = get_resource_path("config/config.toml")

    config = Configuration(config_path)
    app = Application(config)

    app.run()


if __name__ == "__main__":
    main()