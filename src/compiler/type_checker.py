
from compiler import ast
from compiler.types import Bool, FunType, Int, Type, Unit


def typecheck(node: ast.Expression) -> Type:
    predefined_functions = {
        "print_int": FunType([Int], Unit),
        "print_bool": FunType([Bool], Unit),
        "read_int": FunType([], Int)
    }

    match node:
        case ast.Literal():
            if isinstance(node.value, bool):
                return Bool
            elif isinstance(node.value, int):
                return Int
            else:
                raise Exception(f"Don't know type of literal: {node.value}")

        case ast.BinaryOp():
            t1 = typecheck(node.left)
            t2 = typecheck(node.right)
            if node.op in ['+', '-', '*', '/']:
                if t1 is not Int or t2 is not Int:
                    raise Exception(f"Operator '{node.op}' expected two Ints, got '{t1}' and '{t2}'")
                return Int
            elif node.op in ['<']:
                if t1 is not Int or t2 is not Int:
                    raise Exception(f"Operator '{node.op}' expected two Ints, got '{t1}' and '{t2}'")
                return Bool
            else:
                raise Exception(f"Unknown operator: {node.op}")

        case ast.IfExpression():
            t1 = typecheck(node.cond)
            if t1 is not Bool:
                raise Exception(f"'if' condition was '{t1}'")
            t2 = typecheck(node.then_clause)
            if node.else_clause is None:
                return Unit
            t3 = typecheck(node.else_clause)
            if t2 != t3:
                raise Exception(f"'then' and 'else' had different types: {t2} and {t3}")
            return t2

        case ast.FunctionCall():
            if node.name not in predefined_functions:
                raise Exception(f"Unknown function: {node.name}")

            func = predefined_functions[node.name]
            expected_args = func.arg_types
            given_args = []
            for arg in node.arguments:
                given_args.append(typecheck(arg))

            if expected_args != given_args:
                raise Exception(f"Unexpected argument type in '{node.name}'")

            return func.return_type

        case _:
            raise Exception(f"Unsupported AST node: {node}")
