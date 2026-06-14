from typing import Union
from dataclasses import dataclass
from litellm import completion, ModelResponse, APIConnectionError
from cli_wizard.state import config_settings
from rich.console import Console

import logging
import litellm

litellm.suppress_debug_info = True
logging.getLogger("LiteLLM").setLevel(logging.CRITICAL)
logging.getLogger("litellm").setLevel(logging.CRITICAL)


class ConfigError(Exception):
    pass


@dataclass
class LLMResponse:
    """
    Standardized response returned by every LLM helper in this module.

    Attributes:
        model (str): Identifier of the model that produced the response
        message (str | None): The text content returned by the model, or
            `None` when the provider did not return any content
        tokens_input (int): Number of prompt tokens billed for the call
        tokens_output (int): Number of completion tokens billed for the call
        tokens_total (int): Sum of input and output tokens reported by the
            provider
    """
    model: str
    message: str | None
    tokens_input: int
    tokens_output: int
    tokens_total: int


def handle_config_error(exception: ConfigError):
    """
    Print a user-facing error message for a `ConfigError` exception.

    Renders the exception message in red and suggests the `wizard config`
    subcommands the user can run to recover.

    Args:
        exception (ConfigError): The configuration error to surface to the
            user.
    """
    console = Console()
    error_message = str(exception)
    console.print(f"[bold red]Error: {error_message}[/bold red]")
    console.print("[red]  > Use `wizard config --edit` to edit configuration settings.[/red]")
    console.print("[red]  > Use `wizard config --init` to setup new configuration settings.[/red]")


def _execute_prompt(prompt: str) -> LLMResponse:
    """
    Send `prompt` to the configured LLM and return a normalised response.

    Reads `LLM_MODEL` and `LLM_API_KEY` from the persisted configuration
    and invokes `litellm.completion`. Network or authentication failures
    surfaced by litellm are converted into `ConfigError` so callers can
    route them through `handle_config_error`.

    Args:
        prompt (str): The fully assembled user message to send to the model.

    Returns:
        LLMResponse: The model's reply along with token usage metadata.

    Raises:
        ConfigError: If `LLM_MODEL` or `LLM_API_KEY` is missing, or if
            litellm raises :class:`APIConnectionError` (typically signalling
            a key/model mismatch).
    """
    model = config_settings.get("LLM_MODEL", None)
    api_key = config_settings.get("LLM_API_KEY", None)

    if not model:
        raise ConfigError("LLM_MODEL is not set in the config")
    if not api_key:
        raise ConfigError("LLM_API_KEY is not set in the config")
    try:
        response = completion(
            model=model,
            api_key=api_key,
            messages=[{"role": "user", "content": prompt}],
        )
        return LLMResponse(
            model=model,
            message=response.choices[0].message.content,
            tokens_input=response.usage.prompt_tokens,
            tokens_output=response.usage.completion_tokens,
            tokens_total=response.usage.total_tokens
        )
    except APIConnectionError as e:
        raise ConfigError("Mismatch between LLM_API_KEY and LLM_MODEL")


def ask_question(question:str) -> LLMResponse:
    """
    Ask the LLM a free-form terminal-related question.

    Wraps `question` in a short system prompt instructing the model to
    answer concisely and in a terminal-friendly format, then dispatches via
    `_execute_prompt`.

    Args:
        question (str): The user's question.

    Returns:
        LLMResponse: The model's answer along with token usage metadata.

    Raises:
        ConfigError: Propagated from `_execute_prompt` when the LLM
            configuration is missing or invalid.
    """
    default_instructions = """
    You are an expert in using the terminal. The user will ask a question and you will answer it.

    Your answer should be short, concise, and to the point; its meant to be displayed in a terminal, 
    keep that in mind when writing your answer.

    This is the user's question:
    """
    return _execute_prompt(f"{default_instructions}\n\n{question}")


def generate_command(description: str) -> LLMResponse:
    """
    Generate a single-line terminal command for the user's described task.

    Builds a prompt that includes the configured `OS` and `SHELL` values so
    the model can tailor the command to the user's environment, then dispatches
    via `_execute_prompt`. The model is instructed to return the command
    by itself, with no surrounding explanation.

    Args:
        description (str): A natural-language description of the task the user
            wants to achieve

    Returns:
        LLMResponse: A response, whose `message` field holds the generated
        command.

    Raises:
        ConfigError: Propagated from `_execute_prompt` when the LLM
            configuration is missing or invalid.
    """
    default_instructions = f"""
    You are an agent that helps users come up with terminal commands.

    You are specifically meant to help new users navigate the terminal.  

    The user will provide you with a task they want to complete. Your job is
    to generate the correct CLI command to run.

    The command should be a single line, only return the command, nothing else.

    The user is using this Operating System: {config_settings.get('OS', 'Unknown')}
    The user is using this Shell/Terminal: {config_settings.get('SHELL', 'Unknown')}

    The user's input is: 
    """.strip()

    prompt = f"{default_instructions}\n\n{description}"
    return _execute_prompt(prompt)


def explain_command(command: str) -> LLMResponse:
    """
    Ask the LLM to break a terminal command down into its parts.

    The model is instructed to return a JSON object whose keys are segments
    of the command (keywords, flags, arguments, etc.) and whose values are
    one-or-two-sentence explanations. The returned `message` is the raw
    string emitted by the model; callers are responsible for parsing it (the
    model does not always produce strictly valid JSON).

    Args:
        command (str): The terminal command to explain.

    Returns:
        LLMResponse: A response whose `message` field holds the JSON-formatted
        explanation string.

    Raises:
        ConfigError: Propagated from `_execute_prompt` when the LLM
            configuration is missing or invalid.
    """
    default_instructions = """
    You are an expert in using the terminal. The user will provide a command and you will explain what it does.

    For each part of the command (key word, argument, flag, etc.), explain what it does specifically in one or two sentences.

    Keep your answer short, concise, and to the point. Return your answer as JSON output (only JSON code, no markdown fluff around it). The keys should be the parts of the command, the values the explanation of said command.

    Example input: ls -a

    Example output: {"ls": "List files in the current directory", "-a": "Show hidden files"}
    Incorrect output: ``json {...}``

    This is the command:
    """.strip()

    prompt = f"{default_instructions}\n\n{command}"
    return _execute_prompt(prompt)