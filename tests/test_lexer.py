import pytest

from docopt2.exceptions import DocoptLanguageError
from docopt2.lexer import Lexer
from docopt2.tokens import Token, TokenType


def test_lexer_basic_tokens():
    """Verifies that individual atomic tokens are recognized correctly."""
    source = "move <file> --force -v [ ] ( ) | ..."
    lexer = Lexer(source)
    tokens = list(lexer.tokenize())

    expected_types = [
        TokenType.COMMAND,  # move
        TokenType.ARGUMENT,  # <file>
        TokenType.LONG_OPTION,  # --force
        TokenType.SHORT_OPTION,  # -v
        TokenType.START_OPTIONAL,  # [
        TokenType.END_OPTIONAL,  # ]
        TokenType.START_REQUIRED,  # (
        TokenType.END_REQUIRED,  # )
        TokenType.PIPE,  # |
        TokenType.ELLIPSIS,  # ...
        TokenType.EOF,
    ]

    assert [t.type for t in tokens] == expected_types
    assert tokens[0].value == "move"
    assert tokens[1].value == "<file>"


@pytest.mark.parametrize(
    "source, expected_type",
    [
        ("UPPERCASE", TokenType.ARGUMENT),
        ("<with-brackets>", TokenType.ARGUMENT),
        ("command-name", TokenType.COMMAND),
        ("--long-opt", TokenType.LONG_OPTION),
        ("-s", TokenType.SHORT_OPTION),
    ],
)
def test_lexer_content_types(source: str, expected_type: TokenType) -> None:
    """
    Verifies that various input strings are categorized into the
    correct TokenType by the Lexer.
    """
    lexer = Lexer(source)
    # Explicitly typing 'tokens' as list[Token] assists IDE autocompletion
    tokens: list[Token] = list(lexer.tokenize())

    assert tokens[0].type == expected_type


def test_lexer_position_tracking():
    """
    Ensures the lexer accurately reports where tokens are found.
    """
    source: str = "command\n  --option"
    lexer = Lexer(source)
    tokens: list[Token] = list(lexer.tokenize())

    # 'command' at 1:1
    token_cmd: Token = tokens[0]
    assert token_cmd.value == "command"
    assert token_cmd.line == 1
    assert token_cmd.column == 1

    # '--option' at 2:3
    token_opt: Token = tokens[1]
    assert token_opt.value == "--option"
    assert token_opt.line == 2
    assert token_opt.column == 3


def test_lexer_invalid_character():
    """
    Verifies that unknown characters raise a localized LanguageError.
    """
    lexer = Lexer("move $invalid")
    with pytest.raises(DocoptLanguageError) as excinfo:
        list(lexer.tokenize())

    # Now matches: "Unexpected character '$' at line 1, col 6"
    assert "line 1" in str(excinfo.value)
    assert "col 6" in str(excinfo.value)


def test_lexer_whitespace_handling():
    """
    Multiple spaces and tabs should be ignored but track columns.
    """
    # cmd(3) + 4 spaces(4) + tab(1) + 4 spaces(4) + <(1)
    # 3 + 4 = 7. Tab at 8 moves to 9. 9 + 4 = 13.
    source = "cmd    \t    <arg>"
    lexer = Lexer(source)
    tokens: list[Token] = list(lexer.tokenize())

    assert tokens[0].value == "cmd"
    assert tokens[1].value == "<arg>"
    assert tokens[1].column == 13  # Corrected to 13 based on 8-char tab stops


def test_lexer_case_sensitivity() -> None:
    """
    Verifies that case determines Token type (Shadowing fix).
    """
    # 'move' should be COMMAND, 'MOVE' should be ARGUMENT
    lexer = Lexer("move MOVE")
    tokens: list[Token] = list(lexer.tokenize())

    assert tokens[0].type == TokenType.COMMAND
    assert tokens[0].value == "move"

    assert tokens[1].type == TokenType.ARGUMENT
    assert tokens[1].value == "MOVE"


def test_lexer_tab_handling() -> None:
    """
    Verifies tab expansion logic for column tracking.
    """
    # "cmd" is col 1-3. Tab at col 4 jumps to 9.
    source = "cmd\t<arg>"
    lexer = Lexer(source)
    tokens = list(lexer.tokenize())

    assert tokens[0].value == "cmd"
    assert tokens[0].column == 1

    assert tokens[1].value == "<arg>"
    assert tokens[1].column == 9  # Jumped from 4 to 9 via Tab
