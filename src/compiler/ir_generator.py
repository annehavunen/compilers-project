
from compiler import ast, ir
from compiler.tokenizer import SourceLocation
from compiler.ir import IRVar
from compiler.types import Bool, Int, Unit, FunType, Type
from compiler.symtab import SymTab, UNDEFINED


def generate_ir(root_types: dict[IRVar, Type], root_node: ast.Expression) -> list[ir.Instruction]:
    var_types: dict[IRVar, Type] = root_types.copy()
    var_unit = IRVar('unit')
    var_types[var_unit] = Unit

    next_var_number = 1
    next_label_number = 1

    def new_var(t: Type) -> IRVar:
        nonlocal next_var_number
        var = IRVar(f'x{next_var_number}')
        var_types[var] = t
        next_var_number += 1
        return var

    def new_label(loc: SourceLocation) -> ir.Label:
        nonlocal next_label_number
        label = ir.Label(loc, f'L{next_label_number}')
        next_label_number += 1
        return label

    instructions: list[ir.Instruction] = []

    def visit(st: SymTab, node: ast.Expression) -> IRVar:
        loc = node.location

        match node:
            case ast.Literal():
                match node.value:
                    case bool():
                        var = new_var(Bool)
                        instructions.append(ir.LoadBoolConstant(loc, node.value, var))
                    case int():
                        var = new_var(Int)
                        instructions.append(ir.LoadIntConstant(loc, node.value, var))
                    case None:
                        var = var_unit
                    case _:
                        raise Exception(f"{loc}: unsupported literal: {type(node.value)}")
                return var

            case ast.BinaryOp():
                if node.op == "=":
                    if not isinstance(node.left, ast.Identifier):
                        raise Exception(f"{loc}: left of assignment must be an identifier")

                    var_name = node.left.name
                    scope = st.find_scope(var_name)
                    if scope is UNDEFINED:
                        raise Exception(f"{loc}: variable '{var_name}' is not set")

                    var_left = scope.get_local(var_name)
                    var_right = visit(scope, node.right)

                    instructions.append(ir.Copy(
                        location=loc,
                        source=var_right,
                        dest=var_left
                    ))

                    return var_left

                elif node.op == 'and':
                    l_right = new_label(loc)
                    l_skip = new_label(loc)
                    l_end = new_label(loc)

                    var_left = visit(st, node.left)
                    instructions.append(ir.CondJump(loc, var_left, l_right, l_skip))

                    instructions.append(l_right)
                    var_right = visit(st, node.right)
                    var_result = new_var(Bool)
                    instructions.append(ir.Copy(loc, var_right, var_result))
                    instructions.append(ir.Jump(loc, l_end))

                    instructions.append(l_skip)
                    instructions.append(ir.LoadBoolConstant(loc, False, var_result))
                    instructions.append(ir.Jump(loc, l_end))

                    instructions.append(l_end)
                    return var_result

                elif node.op == 'or':
                    l_right = new_label(loc)
                    l_skip = new_label(loc)
                    l_end = new_label(loc)

                    var_left = visit(st, node.left)
                    instructions.append(ir.CondJump(loc, var_left, l_skip, l_right))

                    instructions.append(l_right)
                    var_right = visit(st, node.right)
                    var_result = new_var(Bool)
                    instructions.append(ir.Copy(loc, var_right, var_result))
                    instructions.append(ir.Jump(loc, l_end))

                    instructions.append(l_skip)
                    instructions.append(ir.LoadBoolConstant(loc, True, var_result))
                    instructions.append(ir.Jump(loc, l_end))

                    instructions.append(l_end)
                    return var_result

                var_left = visit(st, node.left)
                var_right = visit(st, node.right)

                if node.op in ['==', '!=']:
                    var_result = new_var(Bool)
                    instructions.append(ir.Call(
                        location=loc,
                        fun=IRVar(node.op),
                        args=[var_left, var_right],
                        dest=var_result
                    ))
                    return var_result

                var_op = st.get(node.op)
                var_result = new_var(node.type)
                instructions.append(ir.Call(
                    location=loc,
                    fun=var_op,
                    args=[var_left, var_right],
                    dest=var_result
                ))
                return var_result

            case ast.UnaryOp():
                var_expr = visit(st, node.expr)
                var_op = st.get(f'unary_{node.op}')
                var_result = new_var(node.type)
                instructions.append(ir.Call(
                    location=loc,
                    fun=var_op,
                    args=[var_expr],
                    dest=var_result
                ))
                return var_result

            case ast.IfExpression():
                if node.else_clause is None:
                    l_then = new_label(loc)
                    l_end = new_label(loc)

                    var_cond = visit(st, node.cond)
                    instructions.append(ir.CondJump(loc, var_cond, l_then, l_end))

                    instructions.append(l_then)
                    visit(st, node.then_clause)

                    instructions.append(l_end)
                    return var_unit
                else:
                    l_then = new_label(loc)
                    l_else = new_label(loc)
                    l_end = new_label(loc)

                    var_cond = visit(st, node.cond)
                    instructions.append(ir.CondJump(loc, var_cond, l_then, l_else))

                    instructions.append(l_then)
                    var_result = visit(st, node.then_clause)
                    instructions.append(ir.Jump(loc, l_end))

                    instructions.append(l_else)
                    var_else_result = visit(st, node.else_clause)
                    instructions.append(ir.Copy(loc, var_else_result, var_result))

                    instructions.append(l_end)
                    return var_result

            case ast.WhileExpression():
                l_start = new_label(loc)
                l_body = new_label(loc)
                l_end = new_label(loc)

                instructions.append(l_start)
                var_cond = visit(st, node.cond)
                instructions.append(ir.CondJump(loc, var_cond, l_body, l_end))

                instructions.append(l_body)
                visit(st, node.do_clause)
                instructions.append(ir.Jump(loc, l_start))

                instructions.append(l_end)
                return var_unit

            case ast.VarDeclaration():
                var = visit(st, node.value)
                var_result = new_var(node.value.type)
                st.set(node.name, var_result)
                instructions.append(ir.Copy(loc, var, var_result))
                return var_unit

            case ast.Identifier():
                var = st.get(node.name)
                if var is UNDEFINED:
                    raise Exception(f"{loc}: variable '{node.name}' is not set")
                return var

            case ast.Block():
                inner_scope = SymTab(parent=st)
                result = var_unit
                for expr in node.arguments:
                    result = visit(inner_scope, expr)
                return result

            case ast.FunctionCall():
                func = st.get(node.name)
                if func is UNDEFINED:
                    raise Exception(f"{loc}: function '{node.name}' is not defined")

                var_args = [visit(st, arg) for arg in node.arguments]

                fun_type = var_types[func]
                if isinstance(fun_type, FunType):
                    var_result = new_var(fun_type.return_type)
                else:
                    raise Exception(f"{loc}: unexpected function type")

                instructions.append(ir.Call(
                    location=loc,
                    fun=func,
                    args=var_args,
                    dest=var_result
                ))

                return var_result

            case _:
                raise Exception(f"Unsupported AST node: {node}")

    root_symtab = SymTab()
    for v in root_types.keys():
        root_symtab.set(v.name, v)

    var_result = visit(root_symtab, root_node)

    if var_types[var_result] == Int:
        instructions.append(ir.Call(
            root_node.location,
            IRVar('print_int'),
            [var_result],
            new_var(Unit)
        ))
    elif var_types[var_result] == Bool:
        instructions.append(ir.Call(
            root_node.location,
            IRVar('print_bool'),
            [var_result],
            new_var(Unit)
        ))

    return instructions
