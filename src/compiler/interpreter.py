from dataclasses import dataclass, field
from typing import Any, Optional, Callable
from compiler import ast


UNDEFINED = object()

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
        return UNDEFINED

    def get_local(self, name: str) -> Any:
        if name in self.locals:
            return self.locals[name]
        return UNDEFINED

    def find_scope(self, name: str) -> Any:
        if name in self.locals:
            return self
        if self.parent:
            return self.parent.find_scope(name)
        return UNDEFINED

def build_toplevel_symtab() -> SymTab:
    symtab = SymTab()

    symtab.set('+', lambda a, b: a + b)
    symtab.set('-', lambda a, b: a - b)
    symtab.set('*', lambda a, b: a * b)
    symtab.set('/', lambda a, b: a // b if b != 0 else zero_division_exception())
    symtab.set('%', lambda a, b: a % b)
    symtab.set('==', lambda a, b: a == b)
    symtab.set('!=', lambda a, b: a != b)
    symtab.set('<', lambda a, b: a < b)
    symtab.set('<=', lambda a, b: a <= b)
    symtab.set('>', lambda a, b: a > b)
    symtab.set('>=', lambda a, b: a >= b)
    symtab.set('and', lambda a, b: a and b)
    symtab.set('or', lambda a, b: a or b)
    symtab.set('unary_-', lambda a: -a)
    symtab.set('unary_not', lambda a: not a)
    symtab.set('read_int', lambda: int(input()))
    symtab.set('print_int', lambda a: print(a))
    symtab.set('print_bool', lambda a: print('true') if a else print('false'))

    return symtab

def zero_division_exception() -> None:
    raise Exception("Can't divide by zero")

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
                scope = symtab.find_scope(name)
                if scope is UNDEFINED:
                    raise Exception(f'Variable "{name}" is not set')
                scope.set(name, value)
                return value

            a: Any = interpret(node.left, symtab)
            if node.op == "and":
                if not a:
                    return False

            elif node.op == "or":
                if a:
                    return True
            
            b: Any = interpret(node.right, symtab)
            binaryop = symtab.get(node.op)
            return binaryop(a, b)

        case ast.VarDeclaration():
            if symtab.get_local(node.name) is not UNDEFINED:
                raise Exception(f'Value for "{node.name}" already exists')
            value = interpret(node.value, symtab)
            symtab.set(node.name, value)
            return None

        case ast.Identifier():
            value = symtab.get(node.name)
            if value is UNDEFINED:
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

        case ast.WhileExpression():
            while True:
                cond_value = interpret(node.cond, symtab)
                if not cond_value:
                    return None
                interpret(node.do_clause, symtab)

        case ast.Block():
            inner_scope = SymTab(parent=symtab)
            result = None
            for argument in node.arguments:
                result = interpret(argument, inner_scope)
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
            value = interpret(node.expr, symtab)
            unaryop = symtab.get(f'unary_{node.op}')
            return unaryop(value)

        case _:
            raise Exception(f'Unsupported AST node: {node}')
