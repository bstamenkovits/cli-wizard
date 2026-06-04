import click


def display_token_usage(token_count_in, token_count_out):
    click.secho(f"\n\nToken Usage:", bold=True)
    click.echo(f"{click.style(token_count_in, fg='cyan')} input tokens used, {click.style(token_count_out, fg='cyan')} output tokens used.")