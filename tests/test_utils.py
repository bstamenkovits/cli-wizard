from click.testing import CliRunner
import click

from cli_wizard.commands._utils import display_token_usage


def _capture(fn, *args, **kwargs):
    """Run a Click-printing function inside an isolated CLI invocation."""

    @click.command()
    def _wrapper():
        fn(*args, **kwargs)

    return CliRunner().invoke(_wrapper, [])


def test_display_token_usage_prints_both_counts():
    result = _capture(display_token_usage, 42, 7)
    assert result.exit_code == 0
    assert "42" in result.output
    assert "7" in result.output
    assert "Token Usage" in result.output


def test_display_token_usage_handles_zero_values():
    result = _capture(display_token_usage, 0, 0)
    assert result.exit_code == 0
    assert "0 input tokens used" in result.output
    assert "0 output tokens used" in result.output
