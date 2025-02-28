
from compiler import ast, ir
from compiler.ir import IRVar
from compiler.types import Bool, Int, Unit, Type
from compiler.symtab import SymTab


def generate_ir(root_types: dict[IRVar, Type], root_node: ast.Expression) -> list[ir.Instruction]:
    var_types: dict[IRVar, Type] = root_types.copy()
    var_unit = IRVar('unit')
    var_types[var_unit] = Unit

    next_var_number = 1
    next_label_number = 1

    def new_var() -> IRVar:
        nonlocal next_var_number
        var = IRVar(f'x{next_var_number}')
        next_var_number += 1
        return var

    def new_label() -> ir.Label:
        nonlocal next_label_number
        label = ir.Label(f'L{next_label_number}')
        next_label_number += 1
        return label

    instructions: list[ir.Instruction] = []

    def visit(st: SymTab, node: ast.Expression) -> IRVar:
        loc = node.location

        match node:
            case ast.Literal():
                match node.value:
                    case bool():
                        ...
                    case int():
                        var = new_var()
                        instructions.append(ir.LoadIntConstant(node.value, var))
                    case None:
                        ...
                    case _:
                        raise Exception(f"{loc}: unsupported literal: {type(node.value)}")
                return var

            case ast.BinaryOp():
                var_op = st.get(node.op)
                var_left = visit(st, node.left)
                var_right = visit(st, node.right)
                var_result = new_var()
                instructions.append(ir.Call(
                    fun=var_op,
                    args=[var_left, var_right],
                    dest=var_result
                ))
                return var_result

            case ast.IfExpression():
                if node.else_clause is None:
                    raise Exception("TODO: if without else")
                else:
                    l_then = new_label()
                    l_else = new_label()
                    l_end = new_label()

                    var_cond = visit(st, node.cond)
                    instructions.append(ir.CondJump(var_cond, l_then, l_else))

                    instructions.append(l_then)
                    var_result = visit(st, node.then_clause)
                    instructions.append(ir.Jump(l_end))

                    instructions.append(l_else)
                    var_else_result = visit(st, node.else_clause)
                    instructions.append(ir.Copy(var_else_result, var_result))

                    instructions.append(l_end)
                    return var_result

            case _:
                raise Exception(f"Unsupported AST node: {node}")

    root_symtab = SymTab()
    for v in root_types.keys():
        root_symtab.set(v.name, v)

    var_result = visit(root_symtab, root_node)

    # TODO: handle boolean and unit results
    instructions.append(ir.Call(
        IRVar('print_int'),
        [var_result],
        new_var()
    ))

    return instructions
