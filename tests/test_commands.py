"""Tests for the Click commands.

The ``ask`` and ``generate`` commands resolve their LLM helpers through the
``cli_wizard.core.llm`` module, so we patch the helpers there. The ``config``
command now drives an interactive questionary-based editor; rather than try to
script that UI through CliRunner, we patch the editor helpers and assert that
the command wires the right one for each flag.
"""
import json
import sys

import pytest

from cli_wizard import state
from cli_wizard.commands.ask import ask
from cli_wizard.commands.config import config as config_cmd
from cli_wizard.commands.generate import generate
from cli_wizard.core import llm
from cli_wizard.core.llm import ConfigError, LLMResponse

# ``cli_wizard.commands`` re-exports each command at the package root, which
# shadows the submodule attribute. Grab the real module via ``sys.modules``
# so monkeypatch can target ``edit_config`` / ``init_config``.
config_module = sys.modules["cli_wizard.commands.config"]


# ---- helpers ---------------------------------------------------------------


def _llm_response(message="ok", tokens_input=1, tokens_output=2, model="gpt-4o"):
    return LLMResponse(
        model=model,
        message=message,
        tokens_input=tokens_input,
        tokens_output=tokens_output,
        tokens_total=tokens_input + tokens_output,
    )


def _patch_llm(monkeypatch, *, ask_question=None, generate_command=None, explain_command=None):
    if ask_question is not None:
        monkeypatch.setattr(llm, "ask_question", ask_question)
    if generate_command is not None:
        monkeypatch.setattr(llm, "generate_command", generate_command)
    if explain_command is not None:
        monkeypatch.setattr(llm, "explain_command", explain_command)


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
    _patch_llm(
        monkeypatch,
        ask_question=lambda q: _llm_response(message="use tar -xzf"),
    )

    result = runner.invoke(ask, ["how do I extract a tarball?"])

    assert result.exit_code == 0
    assert "use tar -xzf" in result.output
    assert "Answer" in result.output


def test_ask_token_usage_flag_shows_counts(runner, monkeypatch):
    _patch_llm(
        monkeypatch,
        ask_question=lambda q: _llm_response(
            message="hello", tokens_input=13, tokens_output=17
        ),
    )

    result = runner.invoke(ask, ["--token_usage", "anything"])

    assert result.exit_code == 0
    assert "13" in result.output
    assert "17" in result.output
    assert "Token Usage" in result.output


def test_ask_omits_token_usage_by_default(runner, monkeypatch):
    _patch_llm(
        monkeypatch,
        ask_question=lambda q: _llm_response(
            message="answer", tokens_input=9, tokens_output=9
        ),
    )

    result = runner.invoke(ask, ["question"])

    assert result.exit_code == 0
    assert "Token Usage" not in result.output


def test_ask_handles_config_error(runner, monkeypatch):
    def _raise(_q):
        raise ConfigError("LLM_API_KEY is not set in the config")

    _patch_llm(monkeypatch, ask_question=_raise)

    result = runner.invoke(ask, ["anything"])

    assert result.exit_code == 0  # command returns cleanly, just prints error
    assert "LLM_API_KEY is not set" in result.output
    assert "wizard config" in result.output


# ---- generate --------------------------------------------------------------


def test_generate_prints_command_and_copies(runner, monkeypatch, _stub_clipboard):
    _patch_llm(
        monkeypatch,
        generate_command=lambda d: _llm_response(message="ls -la"),
    )

    result = runner.invoke(generate, ["list everything"])

    assert result.exit_code == 0
    assert "ls -la" in result.output
    assert "copied to clipboard" in result.output
    assert _stub_clipboard[-1] == "ls -la"


def test_generate_handles_none_message_without_crashing(
    runner, monkeypatch, _stub_clipboard
):
    _patch_llm(
        monkeypatch,
        generate_command=lambda d: _llm_response(
            message=None, tokens_input=0, tokens_output=0
        ),
    )

    result = runner.invoke(generate, ["broken"])

    assert result.exit_code == 0
    # falls back to empty string for the clipboard
    assert _stub_clipboard[-1] == ""


def test_generate_handles_config_error(runner, monkeypatch):
    def _raise(_d):
        raise ConfigError("Mismatch between LLM_API_KEY and LLM_MODEL")

    _patch_llm(monkeypatch, generate_command=_raise)

    result = runner.invoke(generate, ["something"])

    assert result.exit_code == 0
    assert "Mismatch between LLM_API_KEY and LLM_MODEL" in result.output


def test_generate_token_usage_sums_generate_only_when_not_explaining(
    runner, monkeypatch
):
    _patch_llm(
        monkeypatch,
        generate_command=lambda d: _llm_response(
            message="ls", tokens_input=5, tokens_output=6
        ),
    )

    result = runner.invoke(generate, ["--token_usage", "list"])

    assert result.exit_code == 0
    assert "5" in result.output
    assert "6" in result.output


def test_generate_with_explain_renders_section(runner, monkeypatch):
    _patch_llm(
        monkeypatch,
        generate_command=lambda d: _llm_response(message="ls -a"),
        explain_command=lambda c: _llm_response(
            message=json.dumps({"ls": "list", "-a": "all"}),
            tokens_input=4,
            tokens_output=8,
        ),
    )

    result = runner.invoke(generate, ["--explain", "list all"])

    assert result.exit_code == 0
    assert "Explanation" in result.output
    assert "ls" in result.output
    assert "list" in result.output


def test_generate_with_explain_falls_back_when_not_json(runner, monkeypatch):
    _patch_llm(
        monkeypatch,
        generate_command=lambda d: _llm_response(
            message="ls", tokens_input=0, tokens_output=0
        ),
        explain_command=lambda c: _llm_response(
            message="not valid json at all",
            tokens_input=1,
            tokens_output=2,
        ),
    )

    result = runner.invoke(generate, ["--explain", "list"])

    assert result.exit_code == 0
    assert "Explanation" in result.output
    assert "not valid json at all" in result.output


def test_generate_explain_token_counts_are_summed(runner, monkeypatch):
    _patch_llm(
        monkeypatch,
        generate_command=lambda d: _llm_response(
            message="ls", tokens_input=10, tokens_output=20
        ),
        explain_command=lambda c: _llm_response(
            message="{}", tokens_input=3, tokens_output=4
        ),
    )

    result = runner.invoke(generate, ["--explain", "--token_usage", "x"])

    assert result.exit_code == 0
    # 10 + 3 = 13, 20 + 4 = 24
    assert "13" in result.output
    assert "24" in result.output


# ---- config ----------------------------------------------------------------


def test_config_default_displays_current_settings(runner, monkeypatch):
    monkeypatch.setattr(
        state.config_settings,
        "_config",
        {
            "LLM_API_KEY": "abc",
            "LLM_MODEL": "gpt-4o",
            "OS": "macOS",
            "SHELL": "zsh",
        },
    )

    result = runner.invoke(config_cmd, [])

    assert result.exit_code == 0
    assert "macOS" in result.output
    assert "zsh" in result.output
    assert "gpt-4o" in result.output


def test_config_default_marks_unset_fields(runner, monkeypatch):
    monkeypatch.setattr(state.config_settings, "_config", {})

    result = runner.invoke(config_cmd, [])

    assert result.exit_code == 0
    assert "not set" in result.output


def test_config_edit_invokes_edit_helper(runner, monkeypatch):
    monkeypatch.setattr(
        state.config_settings,
        "_config",
        {"LLM_API_KEY": "k", "LLM_MODEL": "gpt-4o", "OS": "macOS", "SHELL": "zsh"},
    )
    called = []
    monkeypatch.setattr(config_module, "edit_config", lambda: called.append("edit"))

    result = runner.invoke(config_cmd, ["--edit"])

    assert result.exit_code == 0
    assert called == ["edit"]


def test_config_init_resets_then_invokes_init_helper(runner, monkeypatch, tmp_config_file):
    # Seed the in-memory state and the on-disk file so we can observe reset().
    tmp_config_file.parent.mkdir(parents=True, exist_ok=True)
    tmp_config_file.write_text(json.dumps({"LLM_API_KEY": "old"}))
    monkeypatch.setattr(
        state.config_settings, "_config", {"LLM_API_KEY": "old"}
    )

    called = []
    monkeypatch.setattr(config_module, "init_config", lambda: called.append("init"))

    result = runner.invoke(config_cmd, ["--init"])

    assert result.exit_code == 0
    assert called == ["init"]
    # reset() deletes the config file on disk and clears the in-memory state.
    assert not tmp_config_file.exists()
    assert state.config_settings._config == {}


def test_config_init_takes_precedence_over_edit(runner, monkeypatch):
    monkeypatch.setattr(state.config_settings, "_config", {})

    init_calls = []
    edit_calls = []
    monkeypatch.setattr(config_module, "init_config", lambda: init_calls.append(1))
    monkeypatch.setattr(config_module, "edit_config", lambda: edit_calls.append(1))

    result = runner.invoke(config_cmd, ["--init", "--edit"])

    assert result.exit_code == 0
    assert init_calls == [1]
    assert edit_calls == []


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
