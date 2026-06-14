import click
from rich.console import Console
from terminal_wizard.commands._utils import display_token_usage
from terminal_wizard.core import llm
from rich.console import Console
from rich.padding import Padding
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from terminal_wizard.theme import THEME


def display_result(
        answer:str,
        token_count_in:int|None=None,
        token_count_out:int|None=None
) -> None:
    console = Console()

    highlight_color = THEME.primary.color
    muted_color = THEME.muted.color

    command_panel = Panel(
        Text(answer),
        title=f"[bold {highlight_color}]Answer[/]",
        title_align="left",
        border_style=muted_color,
        padding=(1, 2),
    )
    console.print()
    console.print(command_panel)

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
@click.argument('question')
@click.option('--token_usage', '-t', is_flag=True, help='Display token usage')
def ask(question, token_usage=False):
    """
    Send a question to the configured LLM and print the answer.

    If the LLM configuration is missing or invalid, the underlying
    `terminal_wizard.core.llm.ConfigError` Exception is caught and a user-facing
    remediation message is printed via `terminal_wizard.core.llm.handle_config_error`.

    Args:
        question (str): The question to send to the LLM.
        token_usage (bool, optional): If True, print input/output token counts
            after the answer. Defaults to False.
    """
    console = Console()
    try:
        response = llm.ask_question(question)
    except llm.ConfigError as e:
        llm.handle_config_error(e)
        return

    # click.secho(f"\nAnswer:", bold=True)
    # click.echo(response.message)
    #
    # if token_usage:
    #     display_token_usage(response.tokens_input, response.tokens_output)
    answer = response.message or ""
    token_count_in = response.tokens_input if token_usage else None
    token_count_out = response.tokens_output if token_usage else None

    display_result(answer, token_count_in, token_count_out)
