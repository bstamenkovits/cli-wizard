import click
import questionary
from cli_wizard.state import config_settings, gemini_interface
from cli_wizard.theme import custom_questionary_style, THEME
from rich.console import Console


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
    model = config_settings.get("GEMINI_MODEL")
    os_line = config_settings.get("OS")
    shell_line = config_settings.get("SHELL")


    # format values for display
    api_key_line = f"{'Gemini API Key':<18}: {api_key}"
    model_line = f"{'Gemini Model':<18}: {model}"
    os_line = f"{'Operating System':<18}: {os_line}"
    shell_line = f"{'Shell/Terminal':<18}: {shell_line}"

    # display config values in terminal
    click.secho("\nCurrent config", fg="cyan", bold=True)
    click.secho("─" * max(len(api_key_line), len(model_line), len(os_line), len(shell_line)), fg="cyan")
    click.secho(api_key_line, fg="magenta")
    click.secho(model_line, fg="magenta")
    click.secho(os_line, fg="magenta")
    click.secho(shell_line, fg="magenta")
    click.echo('\n')


def display_config_v2() -> None:
    console = Console()

    items = [
        ("LLM API Key", config_settings.get("LLM_API_KEY")),
        ("LLM Model", config_settings.get("LLM_MODEL")),
        ("Operating System", config_settings.get("OS")),
        ("Shell/Terminal", config_settings.get("SHELL")),
    ]

    label_width = max(len(label) for label, _ in items)
    title = "CONFIGURATION"

    console.print()
    console.print(f"  [bold {THEME.primary.color}]{title}[/bold {THEME.primary.color}]   [dim]cli-wizard[/dim]")
    console.print(f"  [{THEME.primary.color}]{'▔' * len(title)}[/{THEME.primary.color}]")
    console.print()

    for label, value in items:
        padded_label = f"{label:<{label_width}}"
        if value in (None, ""):
            rendered_value = "[dim italic]not set[/dim italic]"
        else:
            rendered_value = f"[{THEME.primary.color}]{value}[/{THEME.primary.color}]"
        console.print(
            f"  [bright_white]{padded_label}[/bright_white]  [dim]›[/dim]  {rendered_value}"
        )

    console.print()


def edit_config():
    click.echo("")
    while True:
        action = questionary.select(
            "Config Edittor",
            choices=[
                "LLM API Key",
                "LLM Model",
                "Operating System",
                "Shell/Terminal",
                "Exit",
            ],
            qmark="☰",
            style=custom_questionary_style,
        ).ask()

        if action == "LLM API Key":
            api_key = questionary.text(
                "Gemini API Key:",
                default=config_settings.get("LLM_API_KEY", ""),
            ).ask()

            config_settings.set("LLM_API_KEY", api_key)
            print(f"Saved API key: {api_key}\n")
            display_config_v2()

        elif action == "LLM Model":
            model = questionary.text(
                "Model name:",
                default=config_settings.get("LLM_MODEL", ""),
            ).ask()

            config_settings.set("MODEL", model)
            print(f"Saved model: {model}\n")
            display_config_v2()

        elif action == "Operating System":
            os = questionary.select(
                "Operating System:",
                choices=["macOS", "Linux", "Windows"],
                default=config_settings.get("OS", ""),
            ).ask()

            config_settings.set("OS", os)
            print(f"Saved OS: {os}\n")
            display_config_v2()

        elif action == "Shell/Terminal":
            shell = questionary.text(
                "Shell/Terminal:",
                default=config_settings.get("SHELL", ""),
            ).ask()

            config_settings.set("SHELL", shell)
            print(f"Saved Shell/Terminal: {shell}\n")
            display_config_v2()
        elif action == "Exit":
            break


@click.command()
# @click.option('--edit', is_flag=True, help='Summarize day for a different date than today.')
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
    display_config_v2()

    # action = questionary.select(
    #     "Config menu",
    #     choices=[
    #         "View config",
    #         "Edit API key",
    #         "Edit model",
    #         "Back",
    #     ],
    # ).ask()


    #
    if questionary.confirm("Edit Config?", qmark=">").ask():
        edit_config()
        display_config_v2()
    #     # prompts for new values
    #     click.echo("\n")
    #     new_api_key = click.prompt("Gemini API Key (leave blank to keep current value)", default=config_settings.get('GEMINI_API_KEY', ""), type=str)
    #     # new_model
    #     new_os = click.prompt("Operating System - e.g. macOS (leave blank to keep current value)", default=config_settings.get('OS', ""), type=str)
    #     new_shell = click.prompt("Shell/Terminal - e.g. zsh (leave blank to keep current value)", default=config_settings.get('SHELL', ""), type=str)
    #     click.echo("\n")
    #
    #     # update config with new values (if no value is provided, keep using current value)
    #     if new_api_key!="":
    #         config_settings.set("GEMINI_API_KEY", new_api_key)
    #     if new_os!="":
    #         config_settings.set("OS", new_os)
    #     if new_shell!="":
    #         config_settings.set("SHELL", new_shell)
    #
    #     # display updated config
    #     click.secho("Config saved!\n", fg="green")
    #     display_config()
    #
    #     # update Gemini client with new api key from config
    #     gemini_interface.update()
