import json
from pathlib import Path
from platformdirs import user_config_dir


# config file (JSON) located in user's config directory (different for each OS)
APP_NAME = "cli-wizard"
CONFIG_DIR = Path(user_config_dir(APP_NAME))
CONFIG_FILE = CONFIG_DIR / "config.json"


def load_config() -> dict:
    """
    Loads the configuration from a predefined configuration file.

    The function checks for the existence of a predefined configuration file. If the
    file exists, it loads and returns its contents as a dictionary. If the file
    does not exist, it returns an empty dictionary.

    Returns:
        dict: A dictionary containing the configuration data loaded from the file.
              Returns an empty dictionary if the configuration file does not exist.
    """
    if not CONFIG_FILE.exists():
        return {}
    with CONFIG_FILE.open() as f:
        return json.load(f)


def save_config(config: dict) -> None:
    """
    Saves the given configuration dictionary to a specified configuration file.

    This function ensures the directory path for the configuration file is created
    if it does not already exist. The configuration dictionary is then serialized
    into a JSON file with an indentation of 2 spaces.

    Args:
        config (dict): The configuration data to save.

    """
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with CONFIG_FILE.open("w") as f:
        json.dump(config, f, indent=2)


def delete_config() -> None:
    """
    Deletes the configuration file if it exists.

    This function checks for the existence of a pre-defined configuration
    file and removes it from the filesystem if it is present. It performs
    no additional actions or error handling.
    """
    if CONFIG_FILE.exists():
        CONFIG_FILE.unlink()


class ConfigSettings:
    """
    Handles configuration settings management.

    This class provides methods for retrieving and updating application
    configuration settings. It utilizes a configuration loading and saving
    mechanism to ensure that updates are persisted.

    The user settings are stored inside of a JSON file in the user's
    configuration directory.

    Attributes:
        None
    """

    def __init__(self) -> None:
        self._config = load_config()

    def get(self, key: str, default=None):
        return self._config.get(key, default)

    def set(self, key: str, value):
        self._config[key] = value
        save_config(self._config)
        self._config = load_config()
