from dataclasses import replace
from typing import List

from .exceptions import DocoptLanguageError
from .nodes import ArgumentNode, BaseNode, ChoiceGroup, CommandNode, LeafNode, OptionalGroup, OptionNode, RequiredGroup
from .tokens import Token, TokenType


class Parser:
    """
    A Recursive Descent Parser for the docopt DSL.
    """

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.cursor = 0

    def parse(self) -> BaseNode:
        """Entry point: parses the full token stream into a single AST root."""
        result = self._parse_choice()

        if not self._is_at_end() and self._peek().type != TokenType.EOF:
            token = self._peek()
            val = token.value if token.value is not None else token.type.name
            raise DocoptLanguageError(f"Unexpected token '{val}' at line {token.line}, col {token.column}")
        return result

    def _parse_sequence(self) -> BaseNode:
        """Handles a sequence of expressions."""
        nodes: List[BaseNode] = []

        while not self._is_at_end() and self._peek().type not in (
            TokenType.PIPE,
            TokenType.END_OPTIONAL,
            TokenType.END_REQUIRED,
            TokenType.EOF,
        ):
            nodes.append(self._parse_expression())

        if not nodes:
            token = self._peek()
            raise DocoptLanguageError(f"Empty group or sequence detected at line {token.line}, col {token.column}")

        return RequiredGroup(tuple(nodes)) if len(nodes) > 1 else nodes[0]

    def _parse_choice(self) -> BaseNode:
        """Handles the '|' operator for mutual exclusion."""
        branches: List[BaseNode] = [self._parse_sequence()]

        while self._match(TokenType.PIPE):
            branches.append(self._parse_sequence())

        return ChoiceGroup(tuple(branches)) if len(branches) > 1 else branches[0]

    def _parse_expression(self) -> BaseNode:
        """Handles an atom followed by an optional ellipsis (...) for repetition."""
        node = self._parse_atom()

        if self._match(TokenType.ELLIPSIS):
            if isinstance(node, LeafNode):
                return self._update_repeats(node)

        return node

    def _parse_atom(self) -> BaseNode:
        """
        Handles the smallest units (Atoms) and recursive nested groups.
        """
        token = self._advance()
        val = token.value

        # 1. Handle Structural Tokens first
        if token.type == TokenType.START_OPTIONAL:
            inner = self._parse_choice()
            self._consume(TokenType.END_OPTIONAL, "Expected ']'")
            return OptionalGroup((inner,))

        if token.type == TokenType.START_REQUIRED:
            inner = self._parse_choice()
            self._consume(TokenType.END_REQUIRED, "Expected ')'")
            return RequiredGroup((inner,))

        # 2. Narrow 'val' for Content Tokens
        if val is None:
            raise DocoptLanguageError(
                f"Token {token.type.name} is missing a value at line {token.line}, col {token.column}"
            )

        # At this point, val is strictly 'str' for the analyzer
        match token.type:
            case TokenType.LONG_OPTION | TokenType.SHORT_OPTION:
                node = OptionNode(
                    name=val,
                    short=val if token.type == TokenType.SHORT_OPTION else None,
                    long=val if token.type == TokenType.LONG_OPTION else None,
                )

                if self._match(TokenType.EQUALS):
                    arg_token = self._consume(TokenType.ARGUMENT, "Expected argument after '='")
                    arg_val = arg_token.value
                    if arg_val is None:
                        raise DocoptLanguageError("Missing value after '='")

                    return replace(node, argcount=1, name=val)
                return node

            case TokenType.ARGUMENT:
                return ArgumentNode(name=val)

            case TokenType.COMMAND:
                return CommandNode(name=val)

            case _:
                raise DocoptLanguageError(f"Unexpected token '{val}' at line {token.line}, col {token.column}")

    def _update_repeats(self, node: LeafNode) -> LeafNode:
        """Reconstructs a LeafNode with repeats=True."""
        return replace(node, repeats=True)

    def _peek(self) -> Token:
        return self.tokens[self.cursor]

    def _advance(self) -> Token:
        if not self._is_at_end():
            self.cursor += 1
        return self.tokens[self.cursor - 1]

    def _match(self, *types: TokenType) -> bool:
        if self._is_at_end():
            return False
        if self._peek().type in types:
            self._advance()
            return True
        return False

    def _consume(self, token_type: TokenType, message: str) -> Token:
        if self._match(token_type):
            return self.tokens[self.cursor - 1]
        token = self._peek()
        raise DocoptLanguageError(f"{message} at line {token.line}, col {token.column}")

    def _is_at_end(self) -> bool:
        return self.cursor >= len(self.tokens) or self.tokens[self.cursor].type == TokenType.EOF
