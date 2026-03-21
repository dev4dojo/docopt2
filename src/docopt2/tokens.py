from dataclasses import dataclass
from enum import Enum, auto


class TokenType(Enum):
    # Structural Tokens
    START_OPTIONAL = auto()  # [
    END_OPTIONAL = auto()  # ]
    START_REQUIRED = auto()  # (
    END_REQUIRED = auto()  # )
    PIPE = auto()  # |
    ELLIPSIS = auto()  # ...
    EQUALS = auto()  # = (for long options like --option=value)

    # Content Tokens
    SHORT_OPTION = auto()  # -v
    LONG_OPTION = auto()  # --verbose
    ARGUMENT = auto()  # <file> or UPPERCASE
    COMMAND = auto()  # keyword
    EOF = auto()


@dataclass(frozen=True)
class Token:
    type: TokenType
    value: str | None = None
    line: int = 0
    column: int = 0
