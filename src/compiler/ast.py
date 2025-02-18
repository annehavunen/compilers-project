
from dataclasses import dataclass
from compiler.tokenizer import SourceLocation


@dataclass
class Expression:
    """Base class for AST nodes representing expressions"""
    location: SourceLocation


@dataclass
class Identifier(Expression):
    name: str


@dataclass
class Literal(Expression):
    value: int | bool | None


@dataclass
class BinaryOp(Expression):
    left: Expression
    op: str
    right: Expression


@dataclass
class IfExpression(Expression):
    cond: Expression
    then_clause: Expression
    else_clause: Expression | None


@dataclass
class WhileExpression(Expression):
    cond: Expression
    do_clause: Expression


@dataclass
class FunctionCall(Expression):
    name: str
    arguments: list[Expression]


@dataclass
class Block(Expression):
    arguments: list[Expression]


@dataclass
class UnaryOp(Expression):
    op: str
    exp: Expression


@dataclass
class VarDeclaration(Expression):
    name: str
    value: Expression
