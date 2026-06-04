import click
from cli_wizard.commands import config, generate, ask


# entry point for the CLI
@click.group()
def cli():
    pass


cli.add_command(config)
cli.add_command(generate)
cli.add_command(ask)
