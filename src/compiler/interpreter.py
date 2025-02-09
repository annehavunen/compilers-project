from dataclasses import dataclass, field
from typing import Any, Optional
from compiler import ast


@dataclass
class SymTab:
    locals: dict = field(default_factory=dict)
    parent: Optional['SymTab'] = None

    def set(self, name: str, value: Any) -> None:
        if name in self.locals:
            raise Exception(f'Variable "{name}" already exists')
        self.locals[name] = value

    def get(self, name: str) -> Any:
        if name in self.locals:
            return self.locals[name]
        elif self.parent:
            return self.parent.get(name)
        else:
            raise Exception(f'Variable "{name}" is not defined')


Value = int | bool | None

def interpret(node: ast.Expression, symtab: SymTab) -> Value:
    match node:
        case ast.Literal():
            return node.value

        case ast.BinaryOp():
            a: Any = interpret(node.left, symtab)
            b: Any = interpret(node.right, symtab)
            if node.op == '+':
                return a + b 
            elif node.op == '-':
                return a - b
            elif node.op == '*':
                return a * b
            elif node.op == '/':
                return a // b
            elif node.op == '<':
                return a < b
            else:
                raise Exception(f'Unsupported operator "{node.op}"')

        case ast.VarDeclaration():
            value = interpret(node.value, symtab)
            symtab.set(node.name, value)
            return None

        case ast.Identifier():
            return symtab.get(node.name)

        case ast.IfExpression():
            if node.else_clause is not None:
                if interpret(node.cond, symtab):
                    return interpret(node.then_clause, symtab)
                else:
                    return interpret(node.else_clause, symtab)
            else:
                if interpret(node.cond, symtab):
                    interpret(node.then_clause, symtab)
                return None

        case ast.Block():
            inner_scope = SymTab(parent=symtab)
            result = None
            for argument in node.arguments:
                result = interpret(argument, inner_scope)
            if isinstance(result, ast.Literal) and result.value is None:
                return None
            return result

        case _:
            raise Exception(f'Unsupported AST node: {node}')
