import subprocess
import sys

from cli_wizard import __version__
from cli_wizard.cli import build_parser


def test_parser_prog_name():
    parser = build_parser()
    assert parser.prog == "wiz"


def test_module_entry_point():
    result = subprocess.run(
        [sys.executable, "-m", "cli_wizard", "--version"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert __version__ in result.stdout
