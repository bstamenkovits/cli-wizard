import click
import json
import pyperclip

from cli_wizard.state import config_settings, gemini_interface
from cli_wizard.commands import config, generate

# entry point for the CLI
@click.group()
def cli():
    pass

cli.add_command(config)
cli.add_command(generate)
