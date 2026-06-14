import click
import json
import pyperclip
from rich.console import Console
from rich.padding import Padding
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from terminal_wizard.core import llm
from terminal_wizard.theme import THEME


def display_result(
        command:str,
        explanation:str|None=None,
        token_count_in:int|None=None,
        token_count_out:int|None=None
) -> None:
    console = Console()

    highlight_color = THEME.primary.color
    muted_color = THEME.muted.color

    command_panel = Panel(
        Text(command, style=f"bold {highlight_color}"),
        title=f"[bold {highlight_color}]Command[/]",
        title_align="left",
        subtitle=f"[dim italic {muted_color}]copied to clipboard[/]",
        subtitle_align="left",
        border_style=muted_color,
        padding=(1, 2),
    )
    console.print()
    console.print(command_panel)

    if explanation:
        try:
            explanation_dict = json.loads(explanation)
            table = Table(
                show_header=False,
                box=None,
                padding=(0, 2),
                expand=False,
            )
            table.add_column(style=f"bold {highlight_color}", no_wrap=True)
            table.add_column(style="white")
            for key, value in explanation_dict.items():
                table.add_row(key, str(value))
            body = table
        except (json.JSONDecodeError, TypeError):
            body = Text(explanation, style="white")

        explanation_panel = Panel(
            body,
            title=f"[bold {highlight_color}]Explanation[/]",
            title_align="left",
            border_style=muted_color,
            padding=(1, 2),
        )
        console.print()
        console.print(explanation_panel)

    if token_count_in and token_count_out:
        usage = Text.assemble(
            ("Token Usage: ", f"bold {highlight_color}"),
            ("    ", ""),
            ("▲ ", muted_color),
            (f"{token_count_in}", f"bold {highlight_color}"),
            ("  in", f"dim {muted_color}"),
            ("    ", ""),
            ("▼ ", muted_color),
            (f"{token_count_out}", f"bold {highlight_color}"),
            ("  out", f"dim {muted_color}"),
            ("    ", ""),
            ("● ", muted_color),
            (f"{token_count_in + token_count_out}", f"bold {highlight_color}"),
            ("  total", f"dim {muted_color}"),

        )
        console.print()
        console.print(Padding(usage, (0, 2)))


@click.command()
@click.argument('description')
@click.option('--explain', '-e', is_flag=True, help='Explain the generated command')
@click.option('--token_usage', '-t', is_flag=True, help='Display token usage')
def generate(description, explain=False, token_usage=False):
    """
    Generate a shell command from a natural-language description.

    Sends `description` to the configured LLM, prints the resulting command,
    and copies it to the system clipboard. With `--explain`, also asks the
    LLM to break the command down and prints the explanation (rendered as
    key/value pairs when the response is valid JSON, otherwise as plain text).
    With `--token_usage`, prints token usage totals after the output.

    Args:
        description (str): A textual description of the command to generate.
        explain (bool): If True, also generate and print an explanation of the
            command. Defaults to False.
        token_usage (bool): If True, print token usage details for all LLM
            calls made by this invocation. Defaults to False.
    """
    try:
        response = llm.generate_command(description)
        command = response.message
        token_count_in = response.tokens_input
        token_count_out = response.tokens_output
    except llm.ConfigError as e:
        llm.handle_config_error(e)
        return

    command = command or ""
    pyperclip.copy(command)

    explanation = None
    if explain:
        response = llm.explain_command(command)
        token_count_in += response.tokens_input
        token_count_out += response.tokens_output
        explanation = response.message

    token_count_in = token_count_in if token_usage else None
    token_count_out = token_count_out if token_usage else None

    display_result(command, explanation, token_count_in, token_count_out)