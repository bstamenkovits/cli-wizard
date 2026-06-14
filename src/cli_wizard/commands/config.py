import click
import questionary
import litellm

from rapidfuzz import fuzz, process
from rich.console import Console

from cli_wizard.state import config_settings, gemini_interface
from cli_wizard.theme import custom_questionary_style, THEME



def display_config_() -> None:
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


def display_config() -> None:
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


def set_config(key: str, value: str, description:str) -> None:
    config_settings.set(key, value)
    print(f"Saved {description}: {value}\n")
    display_config()
    

def search_for_model() -> str:
    while True:
        query = questionary.text("Search for model:").ask()
        results = process.extract(query, litellm.model_list, limit=30)
        results = [r[0] for r in results]
        results.append("...Search Again...")

        print(results)
    
        model = questionary.select(
            "LLM Model:",
            choices=results,
        ).ask()
        
        if model == "...Search Again...":
            continue
        return model
    

def edit_config():
    print()
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
            set_config("LLM_API_KEY", api_key, "LLM API Key")

        elif action == "LLM Model":
            model = search_for_model()
            set_config("LLM_MODEL", model, "LLM Model")

        elif action == "Operating System":
            os = questionary.select(
                "Operating System:",
                choices=["macOS", "Linux", "Windows"],
                default=config_settings.get("OS", ""),
            ).ask()
            set_config("OS", os, "Operating System")

        elif action == "Shell/Terminal":
            shell = questionary.text(
                "Shell/Terminal:",
                default=config_settings.get("SHELL", ""),
            ).ask()
            set_config("SHELL", shell, "Shell/Terminal")

        elif action == "Exit":
            display_config()
            break


def init_config():
    api_key = questionary.text("Gemini API Key:").ask()
    set_config("LLM_API_KEY", api_key, "LLM API Key")

    model = search_for_model()
    set_config("LLM_MODEL", model, "LLM Model")

    os = questionary.select("Operating System:", choices=["macOS", "Linux", "Windows"]).ask()
    set_config("OS", os, "Operating System")

    shell = questionary.text("Shell/Terminal:").ask()
    set_config("SHELL", shell, "Shell/Terminal")


@click.command()
@click.option('--edit', is_flag=True, help='Edit individual config settings')
@click.option('--init', is_flag=True, help='Initialize new config settings')
def config(edit, init):
    """
    Handles configuration updates and displays current configuration settings.

    This function interacts with the user to optionally edit specific configuration fields, such
    as the Gemini API Key, Operating System, and Shell/Terminal preferences. Updated settings
    are applied and displayed to the user.

    Raises:
        Unexpected behaviors or exceptions raised by external calls (such as `config_settings`
        or `gemini_interface`) are not handled explicitly by this function.
    """
    if init:
        config_settings.reset()
        display_config()
        init_config()
        return

    if edit:
        display_config()
        edit_config()
        return

    display_config()




