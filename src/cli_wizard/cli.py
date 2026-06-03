import argparse
from rich.console import Console

from cli_wizard import __version__

console = Console()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="wiz",
        description="CLI Wizard",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    parser.add_argument(
        "args",
        nargs="*",
        help="Arguments to echo back",
    )
    return parser


def main() -> None:
    parser = build_parser()
    ns = parser.parse_args()
    console.print(" ".join(ns.args))
