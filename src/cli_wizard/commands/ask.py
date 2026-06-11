import click
from cli_wizard.commands._utils import display_token_usage
from cli_wizard.state import gemini_interface
from cli_wizard.core.gemini_interface import NoClientError

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
    try:
        response = gemini_interface.ask_question(question)
        answer = response.get("text")
        token_count_in = response.get("token_count_in", 0)
        token_count_out = response.get("token_count_out", 0)
    except NoClientError:
        click.secho("No Gemini API Key configured...", fg='red')
        click.secho("Use `wiz config` to configure your Gemini API Key.", fg='red')
        return

    click.secho(f"\nAnswer:", bold=True)
    click.echo(answer)

    if token_usage:
        display_token_usage(token_count_in, token_count_out)
