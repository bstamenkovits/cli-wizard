import click
from rich.console import Console
from terminal_wizard.commands._utils import display_token_usage
from terminal_wizard.core import llm


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

    click.secho(f"\nAnswer:", bold=True)
    click.echo(response.message)

    if token_usage:
        display_token_usage(response.tokens_input, response.tokens_output)
