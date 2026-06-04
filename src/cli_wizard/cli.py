import click
import json
from pyperclip import copy

from cli_wizard.gemini_interface import GeminiInterface
from cli_wizard.config import load_config, save_config, Config


config_data = Config()
gem = GeminiInterface(config_data)

# entry point for the CLI
@click.group()
def cli():
    pass


def display_config() -> None:
    # get config values
    api_key = config_data.get("GEMINI_API_KEY")
    os_line = config_data.get("OS")
    shell_line = config_data.get("SHELL")

    # format values for display
    api_key_line = f"{'Gemini API Key':<18}: {api_key}"
    os_line = f"{'Operating System':<18}: {os_line}"
    shell_line = f"{'Shell/Terminal':<18}: {shell_line}"

    # display config values in terminal
    click.secho("\nCurrent config", fg="cyan", bold=True)
    click.secho("─" * max(len(api_key_line), len(os_line), len(shell_line)), fg="cyan")
    click.secho(api_key_line, fg="magenta")
    click.secho(os_line, fg="magenta")
    click.secho(shell_line, fg="magenta")
    click.echo('\n')


@click.command()
def config():
    display_config()

    if click.confirm("Edit Config?"):
        # prompts for new values
        click.echo("\n")
        new_api_key = click.prompt("Gemini API Key (leave blank to keep current value)", default=config_data.get('GEMINI_API_KEY', ""), type=str)
        new_os = click.prompt("Operating System - e.g. macOS (leave blank to keep current value)", default=config_data.get('OS', ""), type=str)
        new_shell = click.prompt("Shell/Terminal - e.g. zsh (leave blank to keep current value)", default=config_data.get('SHELL', ""), type=str)
        click.echo("\n")

        # update config with new values (if no value is provided, keep using current value)
        if new_api_key!="":
            config_data.set("GEMINI_API_KEY", new_api_key)
        if new_os!="":
            config_data.set("OS", new_os)
        if new_shell!="":
            config_data.set("SHELL", new_shell)

        # display updated config
        click.secho("Config saved!\n", fg="green")
        display_config()

        # update Gemini client with new api key from config
        gem.update_client()


@click.command()
@click.argument('question')
@click.option('--explain', '-e', is_flag=True, help='Explain the generated command')
def ask(question, explain=False):
    output = gem.generate_command(question)
    command = output.get("command")
    token_count_in = output.get("token_count_in", 0)
    token_count_out = output.get("token_count_out", 0)

    if command == 0:
        click.secho("No Gemini API Key configured...", fg='red')
        click.secho("Use `wiz config` to configure your Gemini API Key.", fg='red')

    command = command if command else ""

    if explain:
        output = gem.explain_command(command)
        token_count_in += output.get("token_count_in", 0)
        token_count_out += output.get("token_count_out", 0)
        explanation = output.get("explanation")

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

    click.echo(f"\n\n{token_count_in} input tokens used, {token_count_out} output tokens used.")


cli.add_command(config)
cli.add_command(ask)
