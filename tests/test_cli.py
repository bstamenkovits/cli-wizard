"""Smoke tests for the top-level CLI entry point."""
from terminal_wizard import __version__
from terminal_wizard.main import cli


def test_version_constant_is_set():
    assert isinstance(__version__, str)
    assert __version__ != ""


def test_cli_is_a_click_group():
    import click

    assert isinstance(cli, click.Group)


def test_cli_registers_expected_commands():
    assert set(cli.commands.keys()) == {"config", "generate", "ask"}


def test_cli_help_runs_cleanly(runner):
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "Usage" in result.output


def test_cli_no_args_shows_help_or_exits_nonzero(runner):
    # Click groups exit 2 with usage info when invoked without a subcommand.
    result = runner.invoke(cli, [])
    assert result.exit_code in (0, 2)
