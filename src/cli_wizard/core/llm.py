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
    A standardized response format for LLM responses.
    """
    model: str
    message: str | None
    tokens_input: int
    tokens_output: int
    tokens_total: int


def handle_config_error(exception: ConfigError):
    console = Console()
    error_message = str(exception)
    console.print(f"[bold red]Error: {error_message}[/bold red]")
    console.print("[red]  > Use `wizard config --edit` to edit configuration settings.[/red]")
    console.print("[red]  > Use `wizard config --init` to setup new configuration settings.[/red]")


def _execute_prompt(prompt: str) -> LLMResponse:
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
    default_instructions = """
    You are an expert in using the terminal. The user will ask a question and you will answer it.

    Your answer should be short, concise, and to the point; its meant to be displayed in a terminal, 
    keep that in mind when writing your answer.

    This is the user's question:
    """
    return _execute_prompt(f"{default_instructions}\n\n{question}")


def generate_command(description: str) -> LLMResponse:
    """
    Generates a terminal command based on the provided task description.

    This method takes a user-provided task description and constructs a
    prompt by combining the description with default context instructions.
    It then generates the corresponding terminal command by invoking an
    internal method to process the prompt.

    Args:
        description (str): A textual description of the task for which a terminal command is needed.

    Returns:
        dict: A dictionary containing the generated command.
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
    Explains the functionality of a given terminal command and its components in a short
    and concise manner. The explanation for each part of the command, such as keywords,
    arguments, or flags, is returned as a JSON object with descriptions of their purpose.

    Args:
        command (str): The terminal command to be analyzed and explained.

    Returns:
        dict: A JSON-like dictionary where each key represents a segment of the command
        (e.g., keywords, flags, or arguments) and each value contains a brief explanation
        of the segment's function.
    """
    default_instructions = """
    You are an expert in using the terminal. The user will provide a command and you will explain what it does.

    For each part of the command (key word, argument, flag, etc.), explain what it does specifically in one or two sentences.

    Keep your answer short, concise, and to the point. Return your answer as JSON output (only JSON code, no markdown fluff around it). The keys should be the parts of the command, the values the explanation of said command.

    Example input: ls -a

    Example output: {"ls": "List files in the current directory", "-a": "Show hidden files"}
    Incorrect output: ```json {...}```

    This is the command:
    """.strip()

    prompt = f"{default_instructions}\n\n{command}"
    return _execute_prompt(prompt)