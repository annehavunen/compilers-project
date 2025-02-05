
from dataclasses import dataclass
from compiler.tokenizer import SourceLocation


# for testing
L = SourceLocation(file="arbitrary_file", line=-99, column=-99)

@dataclass
class Expression:
    """Base class for AST nodes representing expressions"""
    location: SourceLocation

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Expression):
            return self.location == other.location or self.location == L or other.location == L
        return False

@dataclass
class Identifier(Expression):
    name: str

    def __eq__(self, other: object) -> bool:
        return (isinstance(other, Identifier) and
            self.name == other.name and
            super().__eq__(other))

@dataclass
class Literal(Expression):
    value: int | bool | None

    def __eq__(self, other: object) -> bool:
        return (isinstance(other, Literal) and
            self.value == other.value and
            super().__eq__(other))

@dataclass
class BinaryOp(Expression):
    left: Expression
    op: str
    right: Expression

    def __eq__(self, other: object) -> bool:
        return super().__eq__(other)

@dataclass
class IfExpression(Expression):
    cond: Expression
    then_clause: Expression
    else_clause: Expression | None

    def __eq__(self, other: object) -> bool:
        return (isinstance(other, IfExpression) and
            self.cond == other.cond and
            self.then_clause == other.then_clause and
            self.else_clause == other.else_clause and
            super().__eq__(other))

@dataclass
class WhileExpression(Expression):
    cond: Expression
    do_clause: Expression

    def __eq__(self, other: object) -> bool:
        return (isinstance(other, WhileExpression) and
            self.cond == other.cond and
            self.do_clause == other.do_clause and
            super().__eq__(other))

@dataclass
class FunctionCall(Expression):
    name: str
    arguments: list[Expression]

    def __eq__(self, other: object) -> bool:
        return (isinstance(other, FunctionCall) and
            self.name == other.name and
            self.arguments == other.arguments and
            super().__eq__(other))

@dataclass
class Block(Expression):
    arguments: list[Expression]

    def __eq__(self, other: object) -> bool:
        return (isinstance(other, Block) and
            self.arguments == other.arguments and
            super().__eq__(other))

@dataclass
class UnaryOp(Expression):
    op: str
    exp: Expression

    def __eq__(self, other: object) -> bool:
        return (isinstance(other, UnaryOp) and
            self.op == other.op and
            self.exp == other.exp and
            super().__eq__(other))

@dataclass
class VarDeclaration(Expression):
    name: str
    value: Expression

    def __eq__(self, other: object) -> bool:
        return (isinstance(other, VarDeclaration) and
            self.name == other.name and
            self.value == other.value and
            super().__eq__(other))
