import pytest

from docopt2.exceptions import DocoptLanguageError
from docopt2.lexer import Lexer
from docopt2.nodes import ArgumentNode, BaseNode, ChoiceGroup, CommandNode, OptionalGroup, OptionNode, RequiredGroup
from docopt2.parser import Parser


def parse_str(source: str) -> BaseNode:
    """Helper to convert a string directly to an AST for testing."""
    tokens = list(Lexer(source).tokenize())
    return Parser(tokens).parse()


def test_parser_simple_atoms() -> None:
    """Verifies that basic leaves are parsed correctly."""
    assert parse_str("<file>") == ArgumentNode("<file>")
    assert parse_str("move") == CommandNode("move")
    assert parse_str("--force") == OptionNode(name="--force", long="--force")
    assert parse_str("-v") == OptionNode(name="-v", short="-v")


def test_parser_sequence() -> None:
    """Verifies that space-separated tokens become a RequiredGroup."""
    ast = parse_str("move <file>")
    expected = RequiredGroup((CommandNode("move"), ArgumentNode("<file>")))
    assert ast == expected


def test_parser_optional_group() -> None:
    """Verifies that [ ] becomes an OptionalGroup."""
    ast = parse_str("[--verbose]")
    # Note: OptionalGroup wraps its content in a tuple
    expected = OptionalGroup((OptionNode(name="--verbose", long="--verbose"),))
    assert ast == expected


def test_parser_choice_group() -> None:
    """Verifies that | becomes a ChoiceGroup."""
    ast = parse_str("copy | move")
    expected = ChoiceGroup((CommandNode("copy"), CommandNode("move")))
    assert ast == expected


def test_parser_nested_structures() -> None:
    """Verifies complex nesting: [ (a | b) ]"""
    ast = parse_str("[ ( -a | -b ) ]")

    # Structure: OptionalGroup -> RequiredGroup -> ChoiceGroup
    expected = OptionalGroup(
        (RequiredGroup((ChoiceGroup((OptionNode("-a", short="-a"), OptionNode("-b", short="-b"))),)),)
    )
    assert ast == expected


def test_parser_repetition() -> None:
    """Verifies that ... sets the repeats flag."""
    ast = parse_str("<file>...")
    assert ast == ArgumentNode("<file>", repeats=True)


def test_parser_invalid_syntax() -> None:
    """Verifies that malformed usage strings raise LanguageError with correct messages."""

    with pytest.raises(DocoptLanguageError, match=r"Expected '\]' at line 1, col \d+"):
        parse_str("[ --missing-bracket")

    with pytest.raises(DocoptLanguageError, match=r"Empty group or sequence detected"):
        # Lone pipe results in an empty sequence on the left
        parse_str("|")

    with pytest.raises(DocoptLanguageError, match=r"Unexpected token '\)'"):
        # Unmatched closing parenthesis
        parse_str("move )")


def test_parser_precedence() -> None:
    """Verifies that '|' has lower precedence than sequence."""
    # Should be parsed as (move <file>) OR (remove <file>)
    ast = parse_str("move <file> | remove <file>")

    assert isinstance(ast, ChoiceGroup)
    assert len(ast.children) == 2
    assert isinstance(ast.children[0], RequiredGroup)
    assert isinstance(ast.children[1], RequiredGroup)
