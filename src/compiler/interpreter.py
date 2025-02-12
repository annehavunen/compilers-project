from dataclasses import dataclass, field
from typing import Any, Optional, Callable
from compiler import ast


@dataclass
class SymTab:
    locals: dict = field(default_factory=dict)
    parent: Optional['SymTab'] = None

    def set(self, name: str, value: Any) -> None:
        self.locals[name] = value

    def get(self, name: str) -> Any:
        if name in self.locals:
            return self.locals[name]
        elif self.parent:
            return self.parent.get(name)
        return None
    
    def get_local(self, name: str) -> Any:
        if name in self.locals:
            return self.locals[name]
        return None

    def find_context(self, name: str) -> Optional['SymTab']:
        if name in self.locals:
            return self
        if self.parent:
            return self.parent.find_context(name)
        return None

def build_toplevel_symtab() -> SymTab:
    symtab = SymTab()

    symtab.set('+', add)
    symtab.set('-', subtract)
    symtab.set('*', multiply)
    symtab.set('/', divide)
    symtab.set('%', modulo)
    symtab.set('==', equals)
    symtab.set('!=', not_equals)
    symtab.set('<', less_than)
    symtab.set('<=', less_than_or_equal)
    symtab.set('>', greater_than)
    symtab.set('>=', greater_than_or_equal)
    symtab.set('print_int', print_int)
    symtab.set('print_bool', print_bool)
    symtab.set('read_int', read_int)
    symtab.set('unary_-', unary_minus)
    symtab.set('unary_not', unary_not)

    return symtab

def add(a: int, b: int) -> int:
    return a + b
def subtract(a: int, b: int) -> int:
    return a - b
def multiply(a: int, b: int) -> int:
    return a * b
def divide(a: int, b: int) -> int:
    if b == 0:
        raise Exception("Can't divide by zero")
    return a // b
def modulo(a: int, b: int) -> int:
    return a % b
def equals(a: int | bool | None, b: int | bool | None) -> bool:
    return a == b
def not_equals(a: int | bool | None, b: int | bool | None) -> bool:
    return a != b
def less_than(a: int | bool, b: int | bool) -> bool:
    return a < b
def less_than_or_equal(a: int | bool, b: int | bool) -> bool:
    return a <= b
def greater_than(a: int | bool, b: int | bool) -> bool:
    return a > b
def greater_than_or_equal(a: int | bool, b: int | bool) -> bool:
    return a >= b
def unary_minus(a: int) -> int:
    if type(a) != int:
        raise Exception(f'Value {a} was not integer')
    return -1 * a
def unary_not(a: bool) -> bool:
    if type(a) != bool:
        raise Exception(f'Value {a} was not boolean')
    return not a
def print_int(a: int) -> None:
    print(a)
    return None
def print_bool(a: bool) -> None:
    if a:
        print('true')
    else:
        print('false')
    return None
def read_int() -> int:
    return int(input())

Value = int | bool | None | Callable


def interpret(node: ast.Expression, symtab: SymTab) -> Value:
    match node:
        case ast.Literal():
            return node.value

        case ast.BinaryOp():
            if node.op == "=":
                if not isinstance(node.left, ast.Identifier):
                    raise Exception('Left of assignment must be an identifier')
                name = node.left.name
                value = interpret(node.right, symtab)
                context = symtab.find_context(name)
                if context is None:
                    raise Exception(f'Variable "{name}" is not set')
                context.set(name, value)
                return value

            a: Any = interpret(node.left, symtab)
            b: Any = interpret(node.right, symtab)
            binaryop = symtab.get(node.op)
            return binaryop(a, b)

        case ast.VarDeclaration():
            if symtab.get_local(node.name) is not None:
                raise Exception(f'Value for "{node.name}" already exists')
            value = interpret(node.value, symtab)
            symtab.set(node.name, value)
            return None

        case ast.Identifier():
            value = symtab.get(node.name)
            if value is None:
                raise Exception(f'Variable "{node.name}" is not set')
            return value

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

        case ast.FunctionCall():
            func = symtab.get(node.name)
            args = []
            for argument in node.arguments:
                args.append(interpret(argument, symtab))
            if node.name in ['print_int', 'print_bool'] and len(args) != 1:
                raise Exception(f'Wrong number of arguments in {node.name}')
            if node.name == 'read_int' and len(args) != 0:
                raise Exception(f'Wrong number of arguments in {node.name}')
            return func(*args)

        case ast.UnaryOp():
            value = interpret(node.exp, symtab)
            unaryop = symtab.get(f'unary_{node.op}')
            return unaryop(value)

        case _:
            raise Exception(f'Unsupported AST node: {node}')
