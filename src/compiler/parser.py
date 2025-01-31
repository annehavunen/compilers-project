from compiler import ast
from compiler.tokenizer import Token


def parse(tokens: list[Token]) -> ast.Expression:
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
        left: ast.Expression = parse_or()
        while peek().text == '=':
            op_token = consume()
            right = parse_assignment()
            return ast.BinaryOp(left=left, op=op_token.text, right=right)
        return left

    def parse_or() -> ast.Expression:
        left: ast.Expression = parse_and()
        while peek().text == 'or':
            op_token = consume()
            right = parse_and()
            left = ast.BinaryOp(left=left, op=op_token.text, right=right)
        return left

    def parse_and() -> ast.Expression:
        left: ast.Expression = parse_equality()
        while peek().text == 'and':
            op_token = consume()
            right = parse_equality()
            left = ast.BinaryOp(left=left, op=op_token.text, right=right)
        return left

    def parse_equality() -> ast.Expression:
        left: ast.Expression = parse_comparison()
        while peek().text in ['==', '!=']:
            op_token = consume()
            right = parse_comparison()
            left = ast.BinaryOp(left=left, op=op_token.text, right=right)
        return left

    def parse_comparison() -> ast.Expression:
        left: ast.Expression = parse_addition()
        while peek().text in ['<', '>', '<=', '>=']:
            op_token = consume()
            right = parse_addition()
            left = ast.BinaryOp(left=left, op=op_token.text, right=right)
        return left

    def parse_addition() -> ast.Expression:
        left: ast.Expression = parse_multiplication()
        while peek().text in ['+', '-']:
            op_token = consume()
            right = parse_multiplication()
            left = ast.BinaryOp(left=left, op=op_token.text, right=right)
        return left

    def parse_multiplication() -> ast.Expression:
        left: ast.Expression = parse_unary()
        while peek().text in ['*', '/', '%']:
            op_token = consume()
            right = parse_unary()
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
        elif peek().text == 'var':
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
        expr = parse_expression()
        consume(')')
        return expr

    def parse_block() -> ast.Expression:
        consume('{')
        arguments = []

        if peek().text != '}':
            while True:
                arguments.append(parse_expression())
                if peek().text == '}':
                    break
                if peek().text == ';':
                    consume(';')
                    if peek().text == '}':
                        break

        consume('}')
        return ast.Block(arguments)

    def parse_if_expression() -> ast.Expression:
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
