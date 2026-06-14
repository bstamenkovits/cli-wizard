import click
import json
import pyperclip
from cli_wizard.commands._utils import display_token_usage
from cli_wizard.core import llm



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

    if explain:
        output = llm.explain_command(command)
        token_count_in += output.tokens_input
        token_count_out += output.tokens_output
        explanation = output.message

    response = f"\n{click.style('Command', bold=True)}: \n{click.style(command, fg='cyan')}"
    click.echo(response)
    click.secho(f"(copied to clipboard)")

    if explain:
        click.secho(f"\n\nExplanation:", bold=True)

        # The LLM is instructed to return JSON, but this does not always work. If
        # the response is not valid JSON, it will be displayed as plain text
        try:
            explanation_dict = json.loads(explanation)
            output = ""
            for key, value in explanation_dict.items():
                output += f"{click.style(key, fg='cyan')} \n\t{value}\n"
            click.secho(output)
        except:
            click.secho(explanation)

    if token_usage:
        display_token_usage(token_count_in, token_count_out)