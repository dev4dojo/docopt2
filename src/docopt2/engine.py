from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from .nodes import (
    ArgumentNode,
    BaseNode,
    ChoiceGroup,
    CommandNode,
    LeafNode,
    NodeVisitor,
    OptionalGroup,
    OptionNode,
    RequiredGroup,
)


@dataclass(frozen=True)
class MatchContext:
    left: tuple[str, ...]
    collected: tuple[tuple[str, Any], ...] = ()

    def fork(self, consumed_count: int, key: str, value: Any) -> MatchContext:
        """Handles value aggregation for repeating arguments/options."""
        new_collected = dict(self.collected)

        if key in new_collected:
            existing = new_collected[key]
            if isinstance(existing, list):
                new_collected[key] = existing + [value]
            else:
                new_collected[key] = [existing, value]
        else:
            new_collected[key] = value

        return MatchContext(left=self.left[consumed_count:], collected=tuple(new_collected.items()))

    def to_dict(self) -> Dict[str, Any]:
        return dict(self.collected)


class Matcher(NodeVisitor[Optional[MatchContext]]):
    def __init__(self, context: MatchContext):
        self.initial_context = context

    def _match_leaf(self, node: LeafNode, match_func: Any) -> Optional[MatchContext]:
        current_ctx = self.initial_context
        match_found = False

        while True:
            res = match_func(current_ctx)
            if res is None:
                break
            current_ctx = res
            match_found = True
            if not node.repeats:
                break
        return current_ctx if match_found else None

    def visit_argument(self, node: ArgumentNode) -> Optional[MatchContext]:
        def logic(ctx: MatchContext) -> Optional[MatchContext]:
            if not ctx.left or ctx.left[0].startswith("-"):
                return None
            return ctx.fork(1, node.name, ctx.left[0])

        return self._match_leaf(node, logic)

    def visit_command(self, node: CommandNode) -> Optional[MatchContext]:
        def logic(ctx: MatchContext) -> Optional[MatchContext]:
            if ctx.left and ctx.left[0] == node.name:
                return ctx.fork(1, node.name, True)
            return None

        return self._match_leaf(node, logic)

    def visit_option(self, node: OptionNode) -> Optional[MatchContext]:
        def logic(ctx: MatchContext) -> Optional[MatchContext]:
            if not ctx.left:
                return None
            arg = ctx.left[0]

            # Handle flag match (-v or --verbose)
            # Support both --opt=val (one token) and --opt val (two tokens)
            if arg == node.long or arg == node.short:
                if node.argcount == 0:
                    return ctx.fork(1, node.name, True)
                if len(ctx.left) < 2:
                    return None
                return ctx.fork(2, node.name, ctx.left[1])

            # Handle the --opt=val case specifically if joined in a single token
            if node.long and arg.startswith(f"{node.long}="):
                _, val = arg.split("=", 1)
                return ctx.fork(1, node.name, val)

            return None

        return self._match_leaf(node, logic)

    def visit_required_group(self, node: RequiredGroup) -> Optional[MatchContext]:
        current_ctx = self.initial_context
        for child in node.children:
            res = Matcher(current_ctx).match(child)
            if res is None:
                return None
            current_ctx = res
        return current_ctx

    def visit_optional_group(self, node: OptionalGroup) -> Optional[MatchContext]:
        current_ctx = self.initial_context
        for child in node.children:
            res = Matcher(current_ctx).match(child)
            if res:
                current_ctx = res
        return current_ctx

    def visit_choice_group(self, node: ChoiceGroup) -> Optional[MatchContext]:
        for child in node.children:
            res = Matcher(self.initial_context).match(child)
            if res is not None:
                return res
        return None

    def match(self, node: BaseNode) -> Optional[MatchContext]:
        return node.accept(self)
