"""Shared fixtures for the cli-wizard test suite.

We have to patch the config-file location before any test imports
``cli_wizard.state`` -- otherwise the module-level singleton would read
(and later potentially write) the developer's real config file.
"""
import json
import tempfile
from pathlib import Path

import pytest
from click.testing import CliRunner

# Redirect the config file to a throwaway location BEFORE any
# `cli_wizard.state` import runs. ``load_config`` and ``save_config`` read
# CONFIG_FILE via module globals, so reassigning the attribute is enough.
from cli_wizard.core import config_settings as _cs

_TMP_ROOT = Path(tempfile.mkdtemp(prefix="cli-wizard-tests-"))
_cs.CONFIG_DIR = _TMP_ROOT / "cli-wizard"
_cs.CONFIG_FILE = _cs.CONFIG_DIR / "config.json"


@pytest.fixture
def tmp_config_file(monkeypatch, tmp_path):
    """Point config_settings at a per-test temp file."""
    cfg_dir = tmp_path / "cli-wizard"
    cfg_file = cfg_dir / "config.json"
    monkeypatch.setattr(_cs, "CONFIG_DIR", cfg_dir)
    monkeypatch.setattr(_cs, "CONFIG_FILE", cfg_file)
    return cfg_file


@pytest.fixture
def runner():
    return CliRunner()


class _FakeUsage:
    def __init__(self, prompt=0, candidates=0):
        self.prompt_token_count = prompt
        self.candidates_token_count = candidates


class _FakeResponse:
    def __init__(self, text="ok", prompt=3, candidates=7):
        self.text = text
        self.usage_metadata = _FakeUsage(prompt=prompt, candidates=candidates)


class _FakeModels:
    def __init__(self, response):
        self._response = response
        self.calls = []

    def generate_content(self, *, model, contents):
        self.calls.append({"model": model, "contents": contents})
        return self._response


class FakeGenaiClient:
    """Stands in for ``google.genai.Client``."""

    def __init__(self, *, api_key=None, response=None):
        self.api_key = api_key
        self.models = _FakeModels(response or _FakeResponse())


@pytest.fixture
def fake_response_factory():
    def _make(text="ok", prompt=3, candidates=7):
        return _FakeResponse(text=text, prompt=prompt, candidates=candidates)

    return _make


@pytest.fixture
def patch_genai(monkeypatch):
    """Patch ``google.genai.Client`` to return a FakeGenaiClient.

    Returns the list of created clients so tests can inspect calls.
    """
    created = []

    def _factory(response=None):
        def _ctor(*, api_key=None):
            client = FakeGenaiClient(api_key=api_key, response=response)
            created.append(client)
            return client

        from cli_wizard.core.gemini import gemini_interface as gi
        monkeypatch.setattr(gi.genai, "Client", _ctor)
        return created

    return _factory


@pytest.fixture
def write_config():
    """Write a config JSON to an arbitrary path and return the path."""
    def _write(path: Path, data: dict):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data))
        return path

    return _write
