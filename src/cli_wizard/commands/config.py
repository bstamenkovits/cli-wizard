import click
from cli_wizard.state import config_settings, gemini_interface


def display_config() -> None:
    # get config values
    api_key = config_settings.get("GEMINI_API_KEY")
    os_line = config_settings.get("OS")
    shell_line = config_settings.get("SHELL")

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
        new_api_key = click.prompt("Gemini API Key (leave blank to keep current value)", default=config_settings.get('GEMINI_API_KEY', ""), type=str)
        new_os = click.prompt("Operating System - e.g. macOS (leave blank to keep current value)", default=config_settings.get('OS', ""), type=str)
        new_shell = click.prompt("Shell/Terminal - e.g. zsh (leave blank to keep current value)", default=config_settings.get('SHELL', ""), type=str)
        click.echo("\n")

        # update config with new values (if no value is provided, keep using current value)
        if new_api_key!="":
            config_settings.set("GEMINI_API_KEY", new_api_key)
        if new_os!="":
            config_settings.set("OS", new_os)
        if new_shell!="":
            config_settings.set("SHELL", new_shell)

        # display updated config
        click.secho("Config saved!\n", fg="green")
        display_config()

        # update Gemini client with new api key from config
        gemini_interface.update_client()