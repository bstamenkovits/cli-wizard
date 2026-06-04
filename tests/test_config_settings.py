import json

from cli_wizard.core import config_settings as cs
from cli_wizard.core.config_settings import (
    ConfigSettings,
    delete_config,
    load_config,
    save_config,
)


def test_load_config_returns_empty_when_file_missing(tmp_config_file):
    assert not tmp_config_file.exists()
    assert load_config() == {}


def test_save_config_creates_dir_and_writes_json(tmp_config_file):
    save_config({"a": 1, "b": "two"})
    assert tmp_config_file.exists()
    assert json.loads(tmp_config_file.read_text()) == {"a": 1, "b": "two"}


def test_load_config_reads_back_saved_data(tmp_config_file):
    save_config({"GEMINI_API_KEY": "secret", "OS": "macOS"})
    assert load_config() == {"GEMINI_API_KEY": "secret", "OS": "macOS"}


def test_delete_config_removes_file_when_present(tmp_config_file):
    save_config({"x": 1})
    assert tmp_config_file.exists()
    delete_config()
    assert not tmp_config_file.exists()


def test_delete_config_is_noop_when_missing(tmp_config_file):
    assert not tmp_config_file.exists()
    # Should not raise.
    delete_config()


def test_config_settings_get_with_default(tmp_config_file):
    settings = ConfigSettings()
    assert settings.get("missing") is None
    assert settings.get("missing", "fallback") == "fallback"


def test_config_settings_set_persists_to_disk(tmp_config_file):
    settings = ConfigSettings()
    settings.set("OS", "linux")
    assert settings.get("OS") == "linux"
    # Verify what's actually on disk.
    assert json.loads(tmp_config_file.read_text()) == {"OS": "linux"}


def test_config_settings_set_then_get_updated_via_reload(tmp_config_file):
    settings = ConfigSettings()
    settings.set("k1", "v1")
    settings.set("k2", "v2")
    # set() reloads from disk after each write, so both keys are visible.
    assert settings.get("k1") == "v1"
    assert settings.get("k2") == "v2"


def test_config_settings_loads_existing_file_on_init(tmp_config_file):
    tmp_config_file.parent.mkdir(parents=True, exist_ok=True)
    tmp_config_file.write_text(json.dumps({"SHELL": "zsh"}))
    settings = ConfigSettings()
    assert settings.get("SHELL") == "zsh"


def test_module_constants_point_at_tmp(tmp_config_file):
    # Sanity check: the monkeypatch is wired up.
    assert cs.CONFIG_FILE == tmp_config_file
    assert cs.CONFIG_DIR == tmp_config_file.parent
