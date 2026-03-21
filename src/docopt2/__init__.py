import re
import sys
from typing import Any, Dict, List, Optional

from .engine import MatchContext, Matcher
from .lexer import Lexer
from .nodes import BaseNode, ChoiceGroup
from .parser import Parser
from .tokens import TokenType


def _extract_patterns(doc: str) -> List[str]:
    match = re.search(r"(?i)usage:(.*?)(\n\s*\n|$)", doc, re.DOTALL)
    if not match:
        return []
    return [line.strip() for line in match.group(1).strip().split("\n") if line.strip()]


def docopt(doc: str, argv: Optional[List[str]] = None) -> Dict[str, Any]:
    if argv is None:
        argv = sys.argv[1:]

    raw_patterns = _extract_patterns(doc)
    if not raw_patterns:
        raise ValueError("No Usage section found in docstring.")

    parsed_patterns: List[BaseNode] = []

    for pattern_text in raw_patterns:
        tokens = list(Lexer(pattern_text).tokenize())

        # Skip the program name (the first word)
        if tokens and tokens[0].type == TokenType.COMMAND:
            tokens = tokens[1:]

        parsed_patterns.append(Parser(tokens).parse())

    root_node = ChoiceGroup(tuple(parsed_patterns))
    ctx = MatchContext(tuple(argv))
    result_ctx = Matcher(ctx).match(root_node)

    if result_ctx is None:
        # Match the exact string expected by the tests
        raise ValueError("Arguments did not match usage string.")

    return result_ctx.to_dict()
