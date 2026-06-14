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
    In-memory accessor for the persisted user configuration.

    Loads the JSON config file once on construction and exposes ``get``,
    ``set``, and ``reset`` methods. Every mutating call writes the file back to
    disk so the in-memory and on-disk state stay in sync.

    Attributes:
        _config (dict): The configuration loaded from
            :data:`CONFIG_FILE`, kept in sync with disk on every mutation.
    """

    def __init__(self) -> None:
        """
        Load the on-disk configuration into memory.
        """
        self._config = load_config()

    def get(self, key: str, default=None):
        """
        Return the value stored under ``key``, or ``default`` if absent.

        Args:
            key (str): The configuration key to look up.
            default: Value to return when ``key`` is not present in the
                configuration. Defaults to ``None``.

        Returns:
            The stored value for ``key`` if present, otherwise ``default``.
        """
        return self._config.get(key, default)

    def set(self, key: str, value):
        """
        Store ``value`` under ``key`` and persist the change to disk.

        After writing, the in-memory state is reloaded from disk so subsequent
        reads reflect exactly what was saved.

        Args:
            key (str): The configuration key to write.
            value: The value to associate with ``key``. Must be JSON
                serialisable.
        """
        self._config[key] = value
        save_config(self._config)
        self._config = load_config()

    def reset(self):
        """
        Delete the on-disk configuration and clear the in-memory state.

        After this call, :meth:`get` returns ``default`` for every key.
        """
        delete_config()
        self._config = load_config()
