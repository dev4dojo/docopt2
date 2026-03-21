from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Generic, Optional, TypeVar

T = TypeVar("T")


class NodeVisitor(Generic[T]):
    """The Visitor Pattern interface for the AST."""

    def visit_argument(self, node: ArgumentNode) -> T: ...
    def visit_command(self, node: CommandNode) -> T: ...
    def visit_option(self, node: OptionNode) -> T: ...
    def visit_required_group(self, node: RequiredGroup) -> T: ...
    def visit_optional_group(self, node: OptionalGroup) -> T: ...
    def visit_choice_group(self, node: ChoiceGroup) -> T: ...


@dataclass(frozen=True)
class BaseNode:
    def accept(self, visitor: NodeVisitor[T]) -> T:
        raise NotImplementedError


@dataclass(frozen=True)
class LeafNode(BaseNode):
    """Base for tokens that carry values (Arguments, Commands, Options)."""

    name: str
    repeats: bool = False


@dataclass(frozen=True)
class BranchNode(BaseNode):
    """Base for structural groups (Required, Optional, Choice)."""

    children: tuple[BaseNode, ...]


@dataclass(frozen=True)
class ArgumentNode(LeafNode):
    def accept(self, visitor: NodeVisitor[T]) -> T:
        return visitor.visit_argument(self)


@dataclass(frozen=True)
class CommandNode(LeafNode):
    def accept(self, visitor: NodeVisitor[T]) -> T:
        return visitor.visit_command(self)


@dataclass(frozen=True)
class OptionNode(LeafNode):
    short: Optional[str] = None
    long: Optional[str] = None
    argcount: int = 0
    value: Any = False

    def accept(self, visitor: NodeVisitor[T]) -> T:
        return visitor.visit_option(self)


@dataclass(frozen=True)
class RequiredGroup(BranchNode):
    def accept(self, visitor: NodeVisitor[T]) -> T:
        return visitor.visit_required_group(self)


@dataclass(frozen=True)
class OptionalGroup(BranchNode):
    def accept(self, visitor: NodeVisitor[T]) -> T:
        return visitor.visit_optional_group(self)


@dataclass(frozen=True)
class ChoiceGroup(BranchNode):
    def accept(self, visitor: NodeVisitor[T]) -> T:
        return visitor.visit_choice_group(self)
