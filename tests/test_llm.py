"""Tests for ``cli_wizard.core.llm``.

The llm module reads the configured model + API key from the
``cli_wizard.state.config_settings`` singleton and delegates the actual API
call to ``litellm.completion``. We patch ``completion`` via the
``patch_litellm`` fixture and seed the singleton with monkeypatch'd values.
"""
import pytest
from litellm import APIConnectionError

from cli_wizard import state
from cli_wizard.core import llm


def _seed_config(monkeypatch, **values):
    """Replace ``state.config_settings._config`` with ``values``."""
    monkeypatch.setattr(state.config_settings, "_config", dict(values))


def test_llmresponse_is_a_dataclass_with_expected_fields():
    response = llm.LLMResponse(
        model="m", message="hi", tokens_input=1, tokens_output=2, tokens_total=3
    )
    assert response.model == "m"
    assert response.message == "hi"
    assert response.tokens_input == 1
    assert response.tokens_output == 2
    assert response.tokens_total == 3


# ---- _execute_prompt -------------------------------------------------------


def test_execute_prompt_raises_when_model_missing(monkeypatch):
    _seed_config(monkeypatch, LLM_API_KEY="k")
    with pytest.raises(llm.ConfigError, match="LLM_MODEL"):
        llm._execute_prompt("hi")


def test_execute_prompt_raises_when_api_key_missing(monkeypatch):
    _seed_config(monkeypatch, LLM_MODEL="gpt-4o")
    with pytest.raises(llm.ConfigError, match="LLM_API_KEY"):
        llm._execute_prompt("hi")


def test_execute_prompt_returns_llmresponse_with_token_counts(
    monkeypatch, patch_litellm, fake_completion_factory
):
    response = fake_completion_factory(
        text="my-output", prompt_tokens=11, completion_tokens=22
    )
    patch_litellm(response=response)
    _seed_config(monkeypatch, LLM_API_KEY="k", LLM_MODEL="gpt-4o")

    result = llm._execute_prompt("hi there")

    assert isinstance(result, llm.LLMResponse)
    assert result.model == "gpt-4o"
    assert result.message == "my-output"
    assert result.tokens_input == 11
    assert result.tokens_output == 22
    assert result.tokens_total == 33


def test_execute_prompt_passes_model_key_and_user_message(
    monkeypatch, patch_litellm
):
    calls = patch_litellm()
    _seed_config(monkeypatch, LLM_API_KEY="secret", LLM_MODEL="gpt-4o")

    llm._execute_prompt("hello world")

    assert len(calls) == 1
    call = calls[0]
    assert call["model"] == "gpt-4o"
    assert call["api_key"] == "secret"
    assert call["messages"] == [{"role": "user", "content": "hello world"}]


def test_execute_prompt_wraps_api_connection_error_as_config_error(
    monkeypatch, patch_litellm
):
    def _raise(**_kwargs):
        # APIConnectionError requires a model and llm_provider kwarg.
        raise APIConnectionError(
            message="bad key", model="gpt-4o", llm_provider="openai"
        )

    patch_litellm(response=_raise)
    _seed_config(monkeypatch, LLM_API_KEY="k", LLM_MODEL="gpt-4o")

    with pytest.raises(llm.ConfigError, match="Mismatch"):
        llm._execute_prompt("hi")


# ---- ask_question / generate_command / explain_command ---------------------


def test_ask_question_embeds_question_in_prompt(monkeypatch, patch_litellm):
    calls = patch_litellm()
    _seed_config(monkeypatch, LLM_API_KEY="k", LLM_MODEL="gpt-4o")

    llm.ask_question("how do I tar a directory?")

    content = calls[-1]["messages"][0]["content"]
    assert "how do I tar a directory?" in content


def test_generate_command_embeds_os_shell_and_description(
    monkeypatch, patch_litellm
):
    calls = patch_litellm()
    _seed_config(
        monkeypatch,
        LLM_API_KEY="k",
        LLM_MODEL="gpt-4o",
        OS="macOS",
        SHELL="zsh",
    )

    llm.generate_command("list hidden files")

    content = calls[-1]["messages"][0]["content"]
    assert "macOS" in content
    assert "zsh" in content
    assert "list hidden files" in content


def test_generate_command_falls_back_to_unknown_when_os_missing(
    monkeypatch, patch_litellm
):
    calls = patch_litellm()
    _seed_config(monkeypatch, LLM_API_KEY="k", LLM_MODEL="gpt-4o")

    llm.generate_command("do a thing")

    content = calls[-1]["messages"][0]["content"]
    assert "Unknown" in content


def test_explain_command_includes_command_in_prompt(
    monkeypatch, patch_litellm
):
    calls = patch_litellm()
    _seed_config(monkeypatch, LLM_API_KEY="k", LLM_MODEL="gpt-4o")

    llm.explain_command("ls -la")

    content = calls[-1]["messages"][0]["content"]
    assert "ls -la" in content


def test_public_helpers_propagate_config_error(monkeypatch):
    # No model configured -> every helper should surface ConfigError.
    _seed_config(monkeypatch, LLM_API_KEY="k")
    for fn, arg in (
        (llm.ask_question, "q"),
        (llm.generate_command, "d"),
        (llm.explain_command, "c"),
    ):
        with pytest.raises(llm.ConfigError):
            fn(arg)


# ---- handle_config_error ---------------------------------------------------


def test_handle_config_error_prints_error_and_recovery_hints(capsys):
    llm.handle_config_error(llm.ConfigError("bad thing happened"))
    out = capsys.readouterr().out
    assert "bad thing happened" in out
    assert "wizard config --edit" in out
    assert "wizard config --init" in out
