import pytest

from cli_wizard.core.config_settings import ConfigSettings
from cli_wizard.core.gemini.gemini_interface import GeminiInterface, NoClientError


def test_no_api_key_leaves_client_none(tmp_config_file):
    iface = GeminiInterface(ConfigSettings())
    assert iface.client is None


def test_execute_prompt_without_client_raises(tmp_config_file):
    iface = GeminiInterface(ConfigSettings())
    with pytest.raises(NoClientError):
        iface._execute_prompt("hello")


def test_update_client_instantiates_when_api_key_present(
    tmp_config_file, patch_genai
):
    created = patch_genai()
    settings = ConfigSettings()
    settings.set("GEMINI_API_KEY", "key-123")

    iface = GeminiInterface(settings)

    assert iface.client is not None
    assert created[-1].api_key == "key-123"


def test_update_client_resets_to_none_when_key_cleared(
    tmp_config_file, patch_genai
):
    patch_genai()
    settings = ConfigSettings()
    settings.set("GEMINI_API_KEY", "k")
    iface = GeminiInterface(settings)
    assert iface.client is not None

    # Simulate clearing the key without saving an empty string in the file:
    # ConfigSettings.set always writes; we patch the in-memory view directly.
    settings._config.pop("GEMINI_API_KEY")
    iface.update()
    assert iface.client is None


def test_execute_prompt_returns_text_and_token_counts(
    tmp_config_file, patch_genai, fake_response_factory
):
    response = fake_response_factory(text="my-output", prompt=11, candidates=22)
    patch_genai(response=response)
    settings = ConfigSettings()
    settings.set("GEMINI_API_KEY", "k")
    iface = GeminiInterface(settings)

    result = iface._execute_prompt("hi there")

    assert result["text"] == "my-output"
    # NOTE: gemini_interface.py maps prompt_token_count -> token_count_out and
    # candidates_token_count -> token_count_in (looks swapped but is the
    # current behavior; this test pins it).
    assert result["token_count_in"] == 22
    assert result["token_count_out"] == 11


def test_execute_prompt_handles_missing_usage_metadata(
    tmp_config_file, patch_genai
):
    class _Resp:
        text = "ok"
        # no usage_metadata attr at all

    patch_genai(response=_Resp())
    settings = ConfigSettings()
    settings.set("GEMINI_API_KEY", "k")
    iface = GeminiInterface(settings)

    result = iface._execute_prompt("hi")
    assert result == {"text": "ok", "token_count_in": 0, "token_count_out": 0}


def test_generate_command_embeds_os_shell_and_description(
    tmp_config_file, patch_genai
):
    patch_genai()
    settings = ConfigSettings()
    settings.set("GEMINI_API_KEY", "k")
    settings.set("OS", "macOS")
    settings.set("SHELL", "zsh")
    iface = GeminiInterface(settings)

    iface.generate_command("list hidden files")

    call = iface.client.models.calls[-1]
    assert call["model"] == iface.model
    assert "macOS" in call["contents"]
    assert "zsh" in call["contents"]
    assert "list hidden files" in call["contents"]


def test_generate_command_falls_back_to_unknown_when_os_missing(
    tmp_config_file, patch_genai
):
    patch_genai()
    settings = ConfigSettings()
    settings.set("GEMINI_API_KEY", "k")
    iface = GeminiInterface(settings)

    iface.generate_command("do a thing")

    contents = iface.client.models.calls[-1]["contents"]
    assert "Unknown" in contents


def test_explain_command_includes_command_in_prompt(
    tmp_config_file, patch_genai
):
    patch_genai()
    settings = ConfigSettings()
    settings.set("GEMINI_API_KEY", "k")
    iface = GeminiInterface(settings)

    iface.explain_command("ls -la")

    contents = iface.client.models.calls[-1]["contents"]
    assert "ls -la" in contents


def test_ask_question_includes_question_in_prompt(
    tmp_config_file, patch_genai
):
    patch_genai()
    settings = ConfigSettings()
    settings.set("GEMINI_API_KEY", "k")
    iface = GeminiInterface(settings)

    iface.ask_question("how do I tar a directory?")

    contents = iface.client.models.calls[-1]["contents"]
    assert "how do I tar a directory?" in contents
