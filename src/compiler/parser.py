from compiler import ast
from compiler.tokenizer import Token


def parse(tokens: list[Token]) -> ast.Expression:
    allow_var = True
    pos = 0

    def peek() -> Token:
        if len(tokens) == 0:
            raise Exception("Input was empty")
        if pos < len(tokens):
            return tokens[pos]
        else:
            return Token(loc=tokens[-1].loc, type='end', text='')

    def consume(expected: str | None = None) -> Token:
        token = peek()
        if expected is not None and token.text != expected:
            raise Exception(f'Expected "{expected}", got "{token.text}"')
        nonlocal pos
        pos += 1
        return token

    def parse_literal() -> ast.Literal:
        token = peek()
        if token.type == 'int_literal':
            consume()
            return ast.Literal(value=int(token.text))
        else:
            raise Exception(f'{peek().loc}: excepted literal, found "{token.text}')

    def parse_identifier() -> ast.Identifier:
        token = peek()
        if token.type == 'identifier':
            consume()
            return ast.Identifier(name=token.text)
        else:
            raise Exception(f'{peek().loc}: excepted identifier, found "{token.text}') 

    def parse_expression() -> ast.Expression:
        return parse_assignment()

    def parse_assignment() -> ast.Expression:
        left: ast.Expression = parse_left_associative_operator(0)
        while peek().text == '=':
            op_token = consume()
            right = parse_assignment()
            return ast.BinaryOp(left=left, op=op_token.text, right=right)
        return left

    left_associative_operators = [
        ['or'],
        ['and'],
        ['==', '!='],
        ['<', '<=', '>', '>='],
        ['+', '-'],
        ['*', '/', '%'],
    ]

    def parse_left_associative_operator(precedence_level: int) -> ast.Expression:
        if precedence_level >= len(left_associative_operators) - 1:
            left = parse_unary()
        else:
            left = parse_left_associative_operator(precedence_level + 1)
        if precedence_level < len(left_associative_operators):
            while peek().text in left_associative_operators[precedence_level]:
                op_token = consume()
                right = parse_left_associative_operator(precedence_level + 1)
                left = ast.BinaryOp(left=left, op=op_token.text, right=right)
        return left

    def parse_unary() -> ast.Expression:
        while peek().text in ['-', 'not']:
            op_token = consume()
            exp = parse_unary()
            return ast.UnaryOp(op=op_token.text, exp=exp)
        return parse_factor()

    def parse_factor() -> ast.Expression:
        if peek().text == '(':
            return parse_parenthesized_expression()
        elif peek().text == '{':
            return parse_block()
        elif peek().text == 'if':
            return parse_if_expression()
        elif peek().text == 'while':
            return parse_while_expression()
        elif peek().text == 'var' and allow_var:
            return parse_var_declaration()
        elif peek().type == 'int_literal':
            return parse_literal()
        elif peek().type == 'identifier':
            identifier = parse_identifier()
            if peek().text == "(":
                return parse_function_call(identifier.name)
            else:
                return identifier
        else:
            raise Exception(f'Unexpected "{peek().text}"')

    def parse_parenthesized_expression() -> ast.Expression:
        consume('(')
        nonlocal allow_var
        allow_var = False
        expr = parse_expression()
        consume(')')
        return expr

    def parse_block() -> ast.Expression:
        consume('{')
        arguments = []
        nonlocal allow_var
        allow_var = True

        if peek().text != '}':
            while True:
                arguments.append(parse_expression())

                if peek().text == '}':
                    break

                elif peek().text == ';':
                    consume(';')
                    if peek().text == '}':
                        arguments.append(ast.Literal(value=None))
                        break

                else:
                    was_block = ends_with_block(arguments[-1])
                    if not was_block:
                        raise Exception(f'Unexpected "{peek().text}"')

        consume('}')
        return ast.Block(arguments)

    def ends_with_block(expression: ast.Expression) -> bool:
        if isinstance(expression, ast.Block):
            return True

        if isinstance(expression, ast.IfExpression):
            if not expression.else_clause:
                return ends_with_block(expression.then_clause)
            return ends_with_block(expression.else_clause)

        if isinstance(expression, ast.WhileExpression):
            return ends_with_block(expression.do_clause)

        if isinstance(expression, ast.VarDeclaration):
            return ends_with_block(expression.value)

        return False

    def parse_if_expression() -> ast.Expression:
        nonlocal allow_var
        allow_var = False
        consume('if')
        cond = parse_expression()
        consume('then')
        then_clause = parse_expression()
        if peek().text == 'else':
            consume('else')
            else_clause = parse_expression()
        else:
            else_clause = None
        return ast.IfExpression(cond, then_clause, else_clause)

    def parse_while_expression() -> ast.Expression:
        nonlocal allow_var
        allow_var = False
        consume('while')
        cond = parse_expression()
        consume('do')
        do_clause = parse_expression()
        return ast.WhileExpression(cond, do_clause)

    def parse_var_declaration() -> ast.Expression:
        consume('var')
        identifier = parse_identifier()
        consume('=')
        value = parse_expression()
        return ast.VarDeclaration(identifier.name, value)

    def parse_function_call(name: str) -> ast.FunctionCall:
        consume('(')
        arguments = []
        nonlocal allow_var
        allow_var = False

        if peek().text != ')':
            while True:
                arguments.append(parse_expression())
                if peek().text == ')':
                    break
                consume(',')

        consume(')')
        return ast.FunctionCall(name=name, arguments=arguments)

    result = parse_expression()
    if pos < len(tokens):
        raise Exception(f'{tokens[pos].loc}: unexpected "{tokens[pos].text}"')

    return result
