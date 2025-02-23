
from compiler import ast
from compiler.types import Bool, FunType, Int, Type, Unit
from dataclasses import dataclass, field
from typing import Optional, Any


UNDEFINED = object()

@dataclass
class TypeSymTab:
    locals: dict = field(default_factory=dict)
    parent: Optional['TypeSymTab'] = None

    def set(self, name: str, type: Type) -> None:
        self.locals[name] = type

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

def build_type_symtab() -> TypeSymTab:
    symtab = TypeSymTab()

    symtab.set('+', FunType([Int, Int], Int))
    symtab.set('-', FunType([Int, Int], Int))
    symtab.set('*', FunType([Int, Int], Int))
    symtab.set('/', FunType([Int, Int], Int))
    symtab.set('%', FunType([Int, Int], Int))
    symtab.set('<', FunType([Int, Int], Bool))
    symtab.set('<=', FunType([Int, Int], Bool))
    symtab.set('>', FunType([Int, Int], Bool))
    symtab.set('>=', FunType([Int, Int], Bool))
    symtab.set('and', FunType([Bool, Bool], Bool))
    symtab.set('or', FunType([Bool, Bool], Bool))
    symtab.set('unary_-', FunType([Int], Int))
    symtab.set('unary_not', FunType([Bool], Bool))
    symtab.set('print_int', FunType([Int], Unit))
    symtab.set('print_bool', FunType([Bool], Unit))
    symtab.set('read_int', FunType([], Int))

    return symtab


def typecheck(node: ast.Expression, symtab: TypeSymTab) -> Type:
    match node:
        case ast.Literal():
            if isinstance(node.value, bool):
                return Bool
            elif isinstance(node.value, int):
                return Int
            elif node.value is None:
                return Unit
            else:
                raise Exception(f"Don't know type of literal: {node.value}")

        case ast.BinaryOp():
            t1 = typecheck(node.left, symtab)
            t2 = typecheck(node.right, symtab)

            if node.op in ['==', '!=']:
                if t1 != t2:
                    raise Exception(f"Operator '{node.op} had different types: {t1} and {t2}")
                return Bool

            elif node.op == '=':
                if t1 != t2:
                    raise Exception(f"Operator '{node.op} had different types: {t1} and {t2}")
                elif not isinstance(node.left, ast.Identifier):
                    raise Exception("Left of assignment must be an identifier")
                name = node.left.name
                scope = symtab.find_scope(name)
                if scope is UNDEFINED:
                    raise Exception(f'Variable "{name}" is not set')
                scope.set(name, t2)
                return t2

            binaryop = symtab.get(node.op)
            if binaryop is UNDEFINED:
                raise Exception(f"Unknown operator: {node.op}")

            elif t1 != binaryop.arg_types[0] or t2 != binaryop.arg_types[1]:
                raise Exception(f"Unexpected types with operator '{node.op}', got '{t1}' and '{t2}'")
            return binaryop.return_type

        case ast.UnaryOp():
            type = typecheck(node.expr, symtab)
            unaryop = symtab.get(f'unary_{node.op}')
            if type != unaryop.arg_types[0]:
                raise Exception(f"Unary operator '{node.op}' expected type '{unaryop.arg_types[0]}', got '{type}'")
            return type         

        case ast.VarDeclaration():
            if symtab.get_local(node.name) is not UNDEFINED:
                raise Exception(f"Value for '{node.name}' already exists")
            type = typecheck(node.value, symtab)
            symtab.set(node.name, type)
            return Unit

        case ast.Identifier():
            type = symtab.get(node.name)
            if type is UNDEFINED:
                raise Exception(f"Variable '{node.name}' is not set")
            return type

        case ast.Block():
            inner_scope = TypeSymTab(parent=symtab)
            return_type: Any = Unit
            for argument in node.arguments:
                return_type = typecheck(argument, inner_scope)
            return return_type

        case ast.IfExpression():
            t1 = typecheck(node.cond, symtab)
            if t1 is not Bool:
                raise Exception(f"'if' condition was '{t1}'")
            t2 = typecheck(node.then_clause, symtab)
            if node.else_clause is None:
                return Unit
            t3 = typecheck(node.else_clause, symtab)
            if t2 != t3:
                raise Exception(f"'then' and 'else' had different types: {t2} and {t3}")
            return t2

        case ast.WhileExpression():
            cond_type = typecheck(node.cond, symtab)
            if cond_type is not Bool:
                raise Exception(f"'while' condition was '{cond_type}'")
            return Unit

        case ast.FunctionCall():
            func = symtab.get(node.name)
            expected_args = func.arg_types
            given_args = [typecheck(arg, symtab) for arg in node.arguments]
            if expected_args != given_args:
                raise Exception(f"Unexpected argument type in '{node.name}'")
            return func.return_type

        case _:
            raise Exception(f"Unsupported AST node: {node}")
