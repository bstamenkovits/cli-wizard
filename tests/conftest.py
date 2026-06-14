"""Shared fixtures for the cli-wizard test suite.

We have to patch the config-file location before any test imports
``cli_wizard.state`` -- otherwise the module-level singleton would read
(and later potentially write) the developer's real config file.
"""
import json
import tempfile
from pathlib import Path
from types import SimpleNamespace

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


def _make_completion_response(text="ok", prompt_tokens=3, completion_tokens=7):
    """Build a stand-in for the object ``litellm.completion`` returns.

    The llm module only touches ``choices[0].message.content`` and the three
    ``usage.*`` token counters, so a SimpleNamespace tree is enough.
    """
    return SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content=text))],
        usage=SimpleNamespace(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
        ),
    )


@pytest.fixture
def fake_completion_factory():
    """Return a factory that builds fake litellm completion responses."""
    return _make_completion_response


@pytest.fixture
def patch_litellm(monkeypatch):
    """Patch ``litellm.completion`` as imported by ``cli_wizard.core.llm``.

    Returns a list of recorded call kwargs so tests can inspect what was sent
    to the model. By default, every call returns the same canned response;
    pass ``response=`` to ``_install`` (or supply a callable) to customise.
    """
    calls = []

    def _install(response=None):
        if response is None:
            response = _make_completion_response()

        if callable(response):
            responder = response
        else:
            def responder(**_kwargs):
                return response

        def _fake_completion(**kwargs):
            calls.append(kwargs)
            return responder(**kwargs)

        from cli_wizard.core import llm as llm_mod
        monkeypatch.setattr(llm_mod, "completion", _fake_completion)
        return calls

    return _install


@pytest.fixture
def write_config():
    """Write a config JSON to an arbitrary path and return the path."""
    def _write(path: Path, data: dict):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data))
        return path

    return _write
