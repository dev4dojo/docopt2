import re
from typing import Final, Iterator

from .exceptions import DocoptLanguageError
from .tokens import Token, TokenType

# PATTERN ORDER MATTERS: Most specific first to avoid shadowing.
PATTERNS: Final[dict[TokenType, str]] = {
    TokenType.ELLIPSIS: r"\.\.\.",
    TokenType.START_OPTIONAL: r"\[",
    TokenType.END_OPTIONAL: r"\]",
    TokenType.START_REQUIRED: r"\(",
    TokenType.END_REQUIRED: r"\)",
    TokenType.EQUALS: r"=",
    TokenType.PIPE: r"\|",
    TokenType.LONG_OPTION: r"--[a-zA-Z0-9-]+",
    TokenType.SHORT_OPTION: r"-[a-zA-Z0-9]",
    # ARGUMENT is strictly Uppercase or <brackets>
    TokenType.ARGUMENT: r"<[^>]+>|[A-Z][A-Z0-9_-]*",
    # COMMAND is strictly Lowercase
    TokenType.COMMAND: r"[a-z][a-z0-9_-]*",
}


class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.cursor = 0
        self.line = 1
        self.column = 1

        # REMOVED: re.IGNORECASE to respect docopt semantics
        self._master_regex = re.compile("|".join(f"(?P<{t.name}>{p})" for t, p in PATTERNS.items()))

    def tokenize(self) -> Iterator[Token]:
        while self.cursor < len(self.source):
            # 1. Skip Whitespace & Track Position
            ws_match = re.compile(r"\s+").match(self.source, self.cursor)
            if ws_match:
                content = ws_match.group(0)
                self._update_position(content)
                self.cursor = ws_match.end()
                continue

            # 2. Match the next Semantic Token
            match = self._master_regex.match(self.source, self.cursor)
            if not match:
                char = self.source[self.cursor]
                raise DocoptLanguageError(f"Unexpected character '{char}' at line {self.line}, col {self.column}")

            token_type_name = match.lastgroup
            assert token_type_name is not None

            token_type = TokenType[token_type_name]
            value = match.group(0)

            yield Token(type=token_type, value=value, line=self.line, column=self.column)

            self._update_position(value)
            self.cursor = match.end()

        yield Token(type=TokenType.EOF, line=self.line, column=self.column)

    def _update_position(self, text: str) -> None:
        """Correctly handles newlines and standard 8-char tab stops."""
        for char in text:
            if char == "\n":
                self.line += 1
                self.column = 1
            elif char == "\t":
                # Standard tab stop logic: jump to next multiple of 8 + 1
                self.column += 8 - (self.column - 1) % 8
            else:
                self.column += 1
