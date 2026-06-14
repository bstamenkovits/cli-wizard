import click
import questionary
import litellm

from rapidfuzz import process
from rich.console import Console

from cli_wizard.state import config_settings
from cli_wizard.theme import custom_questionary_style, THEME


def display_config() -> None:
    """
    Render the current configuration to the terminal.

    Reads the LLM API key, LLM model, operating system, and shell values from
    `config_settings` and prints them in a styled table. Values that are unset
    or empty are displayed as `not set`.
    """
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
    """
    Persist a single configuration value and re-render the config view.

    Args:
        key (str): The configuration key to update (e.g. `"LLM_API_KEY"`).
        value (str): The new value to associate with `key`.
        description (str): Human-readable label for the setting, used in the
            confirmation message printed to the user.
    """
    config_settings.set(key, value)
    print(f"Saved {description}: {value}\n")
    display_config()
    

def search_for_model() -> str | None:
    """
    Interactively search the litellm model catalog and return the user's pick.

    Prompts the user for a query, fuzzy-matches it against `litellm.model_list`
    via `rapidfuzz`, and presents the top 30 results in a selection menu. A
    `"...Search Again..."` choice loops back to a new query so the user can
    refine until they pick a model.

    Returns:
        The model identifier selected by the user.
    """
    while True:
        query = questionary.text("Search for model:").ask()
        results = process.extract(query, litellm.model_list, limit=30)
        results = [str(r[0]) for r in results]
        results.append("...Search Again...")

        print(results)
    
        model = questionary.select(
            "LLM Model:",
            choices=results,
        ).ask()
        
        if model == "...Search Again...":
            continue
        return str(model)
    

def edit_config():
    """
    Run an interactive menu that lets the user edit individual config fields.

    Loops over a menu of editable settings (LLM API key, LLM model, operating
    system, shell/terminal) and writes each chosen value back via
    `set_config`. Selecting `Exit` re-renders the configuration and
    returns.
    """
    print()
    while True:
        action = questionary.select(
            "Config Editor",
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
            model = search_for_model() or ""
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
    """
    Walk the user through a first-time configuration of every setting.

    Prompts in sequence for the LLM API key, LLM model (via
    `search_for_model`), operating system, and shell/terminal, persisting
    each answer with `set_config`.
    """
    api_key = questionary.text("Gemini API Key:").ask()
    set_config("LLM_API_KEY", api_key, "LLM API Key")

    model = search_for_model() or ""
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
    Display, edit, or initialize the cli-wizard configuration.

    With no flags, prints the current configuration. With `--edit`, opens an
    interactive menu for changing individual fields (LLM API key, LLM model,
    operating system, shell/terminal). With `--init`, resets the stored
    configuration and walks the user through setting every field from scratch.

    Args:
        edit: When `True`, launch the interactive editor via `edit_config`.
        init: When `True`, reset existing settings and run the first-time
            setup wizard via `init_config`. Takes precedence over `edit`.
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




