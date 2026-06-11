import click
from cli_wizard.state import config_settings, gemini_interface


def display_config() -> None:
    """
    Displays the current configuration settings in the terminal.

    This function retrieves critical configuration values such as the Gemini API Key, Operating System,
    and Shell/Terminal from the application configuration settings. These values are formatted for
    readability and displayed in the terminal using styled text for better clarity.

    Raises:
        KeyError: If any of the required configuration values ('GEMINI_API_KEY', 'OS', 'SHELL')
        are missing in the application configuration.

    """
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
    """
    Handles configuration updates and displays current configuration settings.

    This function interacts with the user to optionally edit specific configuration fields, such
    as the Gemini API Key, Operating System, and Shell/Terminal preferences. Updated settings
    are applied and displayed to the user.

    Raises:
        Unexpected behaviors or exceptions raised by external calls (such as `config_settings`
        or `gemini_interface`) are not handled explicitly by this function.
    """
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
