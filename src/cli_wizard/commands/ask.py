import click
from rich.console import Console
from cli_wizard.commands._utils import display_token_usage
from cli_wizard.state import gemini_interface
from cli_wizard.core.gemini.gemini_interface import NoClientError
from cli_wizard.core import llm


@click.command()
@click.argument('question')
@click.option('--token_usage', '-t', is_flag=True, help='Display token usage')
def ask(question, token_usage=False):
    """
    Handles the `ask` command to query the Gemini API with a given question. Displays the
    retrieved answer and optionally shows token usage statistics if the respective flag is
    provided.

    Args:
        question (str): The question to query the Gemini API with.
        token_usage (bool, optional): If set to True, displays details about the token
            usage for the query. Default is False.

    Raises:
        NoClientError: Indicates that the Gemini API key is not configured.
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
