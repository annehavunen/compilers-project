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
            return ast.Literal(location=token.loc, value=int(token.text))
        elif token.type == 'bool_literal':
            if token.text == 'true':
                consume()
                return ast.Literal(location=token.loc, value=True)
            else:
                consume()
                return ast.Literal(location=token.loc, value=False)
        else:
            raise Exception(f'{peek().loc}: excepted literal, found "{token.text}')

    def parse_identifier() -> ast.Identifier:
        token = peek()
        if token.type == 'identifier':
            consume()
            return ast.Identifier(location=token.loc, name=token.text)
        else:
            raise Exception(f'{peek().loc}: excepted identifier, found "{token.text}') 

    def parse_expression() -> ast.Expression:
        return parse_assignment()

    def parse_assignment() -> ast.Expression:
        left: ast.Expression = parse_left_associative_operator(0)
        while peek().text == '=':
            op_token = consume()
            right = parse_assignment()
            return ast.BinaryOp(location=op_token.loc, left=left, op=op_token.text, right=right)
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
                left = ast.BinaryOp(location=op_token.loc, left=left, op=op_token.text, right=right)
        return left

    def parse_unary() -> ast.Expression:
        while peek().text in ['-', 'not']:
            op_token = consume()
            expr = parse_unary()
            return ast.UnaryOp(location=op_token.loc, op=op_token.text, expr=expr)
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
        elif peek().type == 'int_literal' or peek().type == 'bool_literal':
            return parse_literal()
        elif peek().type == 'identifier':
            identifier = parse_identifier()
            if peek().text == "(":
                return parse_function_call(identifier)
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
        allow_var = True
        return expr

    def parse_block() -> ast.Expression:
        token = consume('{')
        arguments = []
        nonlocal allow_var
        allow_var = True

        if peek().text != '}':
            while True:
                arguments.append(parse_expression())

                if peek().text == '}':
                    break

                elif peek().text == ';':
                    semicolon_token = consume(';')
                    if peek().text == '}':
                        arguments.append(ast.Literal(location=semicolon_token.loc, value=None))
                        break
                    continue

                else:
                    was_block = ends_with_block(arguments[-1])
                    if not was_block:
                        raise Exception(f'Unexpected "{peek().text}"')

        consume('}')
        return ast.Block(location=token.loc, arguments=arguments)

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

        if isinstance(expression, ast.BinaryOp):
            return ends_with_block(expression.right)

        if isinstance(expression, ast.UnaryOp):
            return ends_with_block(expression.expr)

        return False

    def parse_if_expression() -> ast.Expression:
        nonlocal allow_var
        allow_var = False
        token = consume('if')
        cond = parse_expression()
        consume('then')
        then_clause = parse_expression()
        if peek().text == 'else':
            consume('else')
            else_clause = parse_expression()
        else:
            else_clause = None
        allow_var = True
        return ast.IfExpression(token.loc, cond, then_clause, else_clause)

    def parse_while_expression() -> ast.Expression:
        nonlocal allow_var
        allow_var = False
        token = consume('while')
        cond = parse_expression()
        consume('do')
        do_clause = parse_expression()
        allow_var = True
        return ast.WhileExpression(token.loc, cond, do_clause)

    def parse_var_declaration() -> ast.Expression:
        token = consume('var')
        identifier = parse_identifier()
        declaration = None
        if peek().text == ':':
            consume(':')
            type = parse_identifier()
            declaration = type.name
        consume('=')
        value = parse_expression()
        return ast.VarDeclaration(token.loc, declaration, identifier.name, value)

    def parse_function_call(identifier: ast.Identifier) -> ast.FunctionCall:
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
        allow_var = True
        return ast.FunctionCall(location=identifier.location, name=identifier.name, arguments=arguments)


    if len(tokens) == 0:
        raise Exception("Input was empty")
    tokens.insert(0, Token(loc=tokens[0].loc, type='punctuation', text='{'))
    tokens.append(Token(loc=tokens[-1].loc, type='punctuation', text='}'))

    result = parse_expression()

    if pos < len(tokens):
        raise Exception(f'{tokens[pos].loc}: unexpected "{tokens[pos].text}"')

    if isinstance(result, ast.Block) and len(result.arguments) == 1:
        return result.arguments[0]
    return result
