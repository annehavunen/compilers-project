
from compiler import ast
from compiler.types import Bool, FunType, Int, Type, Unit
from dataclasses import dataclass, field
from typing import Optional, Any


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
        return None

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
            else:
                raise Exception(f"Don't know type of literal: {node.value}")

        case ast.BinaryOp():
            t1 = typecheck(node.left, symtab)
            t2 = typecheck(node.right, symtab)

            binaryop = symtab.get(node.op)
            if not binaryop:
                raise Exception(f"Unknown operator: {node.op}")

            if t1 != binaryop.arg_types[0] or t2 != binaryop.arg_types[1]:
                raise Exception(f"Unexpected types with operator '{node.op}', got '{t1}' and '{t2}'")
            return binaryop.return_type

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

        case ast.FunctionCall():
            func = symtab.get(node.name)
            expected_args = func.arg_types
            given_args = [typecheck(arg, symtab) for arg in node.arguments]
            if expected_args != given_args:
                raise Exception(f"Unexpected argument type in '{node.name}'")
            return func.return_type

        case _:
            raise Exception(f"Unsupported AST node: {node}")
