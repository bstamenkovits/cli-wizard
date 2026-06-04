import json
from pathlib import Path
from platformdirs import user_config_dir


APP_NAME = "cli-wizard"
CONFIG_DIR = Path(user_config_dir(APP_NAME))
CONFIG_FILE = CONFIG_DIR / "config.json"


def load_config():
    if not CONFIG_FILE.exists():
        return {}
    with CONFIG_FILE.open() as f:
        return json.load(f)


def save_config(config: dict):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with CONFIG_FILE.open("w") as f:
        json.dump(config, f, indent=2)


def delete_config():
    if CONFIG_FILE.exists():
        CONFIG_FILE.unlink()


class ConfigSettings:

    def __init__(self) -> None:
        self._config = load_config()

    def get(self, key: str, default=None):
        return self._config.get(key, default)

    def set(self, key: str, value):
        self._config[key] = value
        save_config(self._config)
        self._config = load_config()
