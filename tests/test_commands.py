"""Tests for the Click commands.

The commands import a module-level singleton (``gemini_interface``) from
``cli_wizard.state``. We patch attributes on that singleton rather than
trying to replace the binding inside each commands module.
"""
import json

import pytest

from cli_wizard import state
from cli_wizard.commands.ask import ask
from cli_wizard.commands.config import config as config_cmd
from cli_wizard.commands.generate import generate
from cli_wizard.core.gemini.gemini_interface import NoClientError


# ---- helpers ---------------------------------------------------------------


def _set_methods(monkeypatch, *, generate_cmd=None, explain_cmd=None, ask_q=None):
    if generate_cmd is not None:
        monkeypatch.setattr(state.gemini_interface, "generate_command", generate_cmd)
    if explain_cmd is not None:
        monkeypatch.setattr(state.gemini_interface, "explain_command", explain_cmd)
    if ask_q is not None:
        monkeypatch.setattr(state.gemini_interface, "ask_question", ask_q)


@pytest.fixture(autouse=True)
def _stub_clipboard(monkeypatch):
    """pyperclip can fail in headless environments; replace with a no-op.

    generate.py does ``import pyperclip`` then ``pyperclip.copy(...)``,
    so patching the attribute on the pyperclip module propagates.
    """
    import pyperclip

    copied = []
    monkeypatch.setattr(pyperclip, "copy", lambda v: copied.append(v))
    return copied


# ---- ask -------------------------------------------------------------------


def test_ask_prints_answer(runner, monkeypatch):
    _set_methods(
        monkeypatch,
        ask_q=lambda q: {"text": "use tar -xzf", "token_count_in": 1, "token_count_out": 2},
    )

    result = runner.invoke(ask, ["how do I extract a tarball?"])

    assert result.exit_code == 0
    assert "use tar -xzf" in result.output
    assert "Answer" in result.output


def test_ask_token_usage_flag_shows_counts(runner, monkeypatch):
    _set_methods(
        monkeypatch,
        ask_q=lambda q: {"text": "hello", "token_count_in": 13, "token_count_out": 17},
    )

    result = runner.invoke(ask, ["--token_usage", "anything"])

    assert result.exit_code == 0
    assert "13" in result.output
    assert "17" in result.output
    assert "Token Usage" in result.output


def test_ask_omits_token_usage_by_default(runner, monkeypatch):
    _set_methods(
        monkeypatch,
        ask_q=lambda q: {"text": "answer", "token_count_in": 9, "token_count_out": 9},
    )

    result = runner.invoke(ask, ["question"])

    assert result.exit_code == 0
    assert "Token Usage" not in result.output


def test_ask_handles_no_client_error(runner, monkeypatch):
    def _raise(_q):
        raise NoClientError("no key")

    _set_methods(monkeypatch, ask_q=_raise)

    result = runner.invoke(ask, ["anything"])

    assert result.exit_code == 0  # command returns cleanly, just prints error
    assert "No Gemini API Key configured" in result.output
    assert "wiz config" in result.output


# ---- generate --------------------------------------------------------------


def test_generate_prints_command_and_copies(runner, monkeypatch, _stub_clipboard):
    _set_methods(
        monkeypatch,
        generate_cmd=lambda d: {"text": "ls -la", "token_count_in": 1, "token_count_out": 2},
    )

    result = runner.invoke(generate, ["list everything"])

    assert result.exit_code == 0
    assert "ls -la" in result.output
    assert "copied to clipboard" in result.output
    assert _stub_clipboard[-1] == "ls -la"


def test_generate_handles_none_text_without_crashing(
    runner, monkeypatch, _stub_clipboard
):
    _set_methods(
        monkeypatch,
        generate_cmd=lambda d: {"text": None, "token_count_in": 0, "token_count_out": 0},
    )

    result = runner.invoke(generate, ["broken"])

    assert result.exit_code == 0
    # falls back to empty string for the clipboard
    assert _stub_clipboard[-1] == ""


def test_generate_handles_no_client_error(runner, monkeypatch):
    def _raise(_d):
        raise NoClientError("no key")

    _set_methods(monkeypatch, generate_cmd=_raise)

    result = runner.invoke(generate, ["something"])

    assert result.exit_code == 0
    assert "No Gemini API Key configured" in result.output


def test_generate_token_usage_sums_generate_only_when_not_explaining(
    runner, monkeypatch
):
    _set_methods(
        monkeypatch,
        generate_cmd=lambda d: {"text": "ls", "token_count_in": 5, "token_count_out": 6},
    )

    result = runner.invoke(generate, ["--token_usage", "list"])

    assert result.exit_code == 0
    assert "5" in result.output
    assert "6" in result.output


def test_generate_with_explain_renders_section(runner, monkeypatch):
    # explain_command's return value is read with .get("explanation"); the
    # interface actually returns 'text'. Either way the command should not
    # crash and the Explanation header should appear.
    _set_methods(
        monkeypatch,
        generate_cmd=lambda d: {"text": "ls -a", "token_count_in": 1, "token_count_out": 1},
        explain_cmd=lambda c: {
            "explanation": json.dumps({"ls": "list", "-a": "all"}),
            "token_count_in": 4,
            "token_count_out": 8,
        },
    )

    result = runner.invoke(generate, ["--explain", "list all"])

    assert result.exit_code == 0
    assert "Explanation" in result.output
    assert "ls" in result.output
    assert "list" in result.output


def test_generate_with_explain_falls_back_when_not_json(runner, monkeypatch):
    _set_methods(
        monkeypatch,
        generate_cmd=lambda d: {"text": "ls", "token_count_in": 0, "token_count_out": 0},
        explain_cmd=lambda c: {
            "explanation": "not valid json at all",
            "token_count_in": 1,
            "token_count_out": 2,
        },
    )

    result = runner.invoke(generate, ["--explain", "list"])

    assert result.exit_code == 0
    assert "Explanation" in result.output
    assert "not valid json at all" in result.output


def test_generate_explain_token_counts_are_summed(runner, monkeypatch):
    _set_methods(
        monkeypatch,
        generate_cmd=lambda d: {"text": "ls", "token_count_in": 10, "token_count_out": 20},
        explain_cmd=lambda c: {
            "explanation": "{}",
            "token_count_in": 3,
            "token_count_out": 4,
        },
    )

    result = runner.invoke(generate, ["--explain", "--token_usage", "x"])

    assert result.exit_code == 0
    # 10 + 3 = 13, 20 + 4 = 24
    assert "13" in result.output
    assert "24" in result.output


# ---- config ----------------------------------------------------------------


def test_config_displays_current_then_declines_edit(runner, monkeypatch):
    monkeypatch.setattr(
        state.config_settings,
        "_config",
        {"GEMINI_API_KEY": "abc", "OS": "macOS", "SHELL": "zsh"},
    )

    result = runner.invoke(config_cmd, [], input="n\n")

    assert result.exit_code == 0
    assert "Current config" in result.output
    assert "macOS" in result.output
    assert "zsh" in result.output
    # We declined the edit prompt, so no "Config saved!" line.
    assert "Config saved" not in result.output


def test_config_edit_path_updates_settings(runner, monkeypatch, tmp_config_file):
    # Start from a clean in-memory state but write through to the temp file.
    monkeypatch.setattr(state.config_settings, "_config", {})

    captured = []
    # Refactored from 'update_client' to 'update'
    monkeypatch.setattr(
        state.gemini_interface, "update", lambda: captured.append("updated")
    )

    # Inputs: y (edit) -> api key -> os -> shell
    user_input = "y\nnew-key\nlinux\nbash\n"
    result = runner.invoke(config_cmd, [], input=user_input)

    assert result.exit_code == 0
    assert "Config saved" in result.output
    assert captured == ["updated"]

    written = json.loads(tmp_config_file.read_text())
    assert written == {"GEMINI_API_KEY": "new-key", "OS": "linux", "SHELL": "bash"}


def test_config_edit_keeps_blank_fields_unchanged(runner, monkeypatch, tmp_config_file):
    monkeypatch.setattr(
        state.config_settings,
        "_config",
        {"GEMINI_API_KEY": "keep", "OS": "macOS", "SHELL": "zsh"},
    )
    # Refactored from 'update_client' to 'update'
    monkeypatch.setattr(state.gemini_interface, "update", lambda: None)

    # Accept defaults for all three prompts by hitting enter.
    user_input = "y\n\n\n\n"
    result = runner.invoke(config_cmd, [], input=user_input)

    assert result.exit_code == 0
    # No writes should have occurred since all prompts kept the existing values
    # (which equal the in-memory state).
    assert not tmp_config_file.exists() or json.loads(
        tmp_config_file.read_text()
    ) == {"GEMINI_API_KEY": "keep", "OS": "macOS", "SHELL": "zsh"}


# ---- top-level CLI group ---------------------------------------------------


def test_cli_group_lists_all_commands(runner):
    from cli_wizard.main import cli

    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    for name in ("config", "generate", "ask"):
        assert name in result.output


@pytest.mark.parametrize("subcommand", ["config", "generate", "ask"])
def test_each_subcommand_has_help(runner, subcommand):
    from cli_wizard.main import cli

    result = runner.invoke(cli, [subcommand, "--help"])
    assert result.exit_code == 0
    assert "Usage" in result.output