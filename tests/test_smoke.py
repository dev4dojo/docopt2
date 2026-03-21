import pytest

from docopt2 import docopt

# A representative, complex usage string for integration testing
USAGE = """
Nav-CLI: A modern navigation tool.

Usage:
  nav-cli move <source> <dest> [--speed=<kn>]
  nav-cli ship (cargo | tanker) <id>...
  nav-cli -h | --help

Options:
  -h --help       Show this screen.
  --speed=<kn>    Speed in knots [default: 10].
"""


def test_integration_basic_move():
    """Tests a simple command with positional arguments."""
    argv = ["move", "Port_A", "Port_B"]
    result = docopt(USAGE, argv)

    assert result["move"] is True
    assert result["<source>"] == "Port_A"
    assert result["<dest>"] == "Port_B"
    assert "--speed" not in result


def test_integration_move_with_option():
    """Tests options that take additional arguments."""
    argv = ["move", "A", "B", "--speed", "25"]
    result = docopt(USAGE, argv)

    assert result["move"] is True
    assert result["--speed"] == "25"


def test_integration_choice_and_repetition():
    argv = ["ship", "cargo", "S1", "S2"]
    result = docopt(USAGE, argv)

    assert result["ship"] is True
    assert result["cargo"] is True
    # Update expectation to match our improved list aggregation
    assert result["<id>"] == ["S1", "S2"]


def test_integration_unmatched_usage():
    """Tests that invalid inputs raise a clear error."""
    # 'fly' is not in the USAGE string
    argv = ["fly", "to", "moon"]

    with pytest.raises(ValueError, match="Arguments did not match usage string"):
        docopt(USAGE, argv)


def test_integration_help_flag():
    """Tests basic flag matching."""
    argv = ["-h"]
    result = docopt(USAGE, argv)

    assert result["-h"] is True
    assert "--help" in result or "-h" in result
