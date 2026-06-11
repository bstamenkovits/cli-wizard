import click


def display_token_usage(token_count_in, token_count_out) -> None:
    """
    Displays the usage of input and output tokens in a styled format in the terminal.

    This function provides a formatted output for the count of tokens used as input
    and the count of tokens generated as output. It utilizes styled text for enhanced
    readability in the terminal.

    Args:
        token_count_in: Number of input tokens used.
        token_count_out: Number of output tokens generated.

    Returns:
        None
    """
    click.secho(f"\n\nToken Usage:", bold=True)
    click.echo(f"{click.style(token_count_in, fg='cyan')} input tokens used, {click.style(token_count_out, fg='cyan')} output tokens used.")