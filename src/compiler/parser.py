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
        left: ast.Expression = parse_polynomial()
        while peek().text in ['<']:
            op_token = consume()
            right = parse_polynomial()
            left = ast.BinaryOp(left=left, op=op_token.text, right=right)
        return left

    def parse_polynomial() -> ast.Expression:
        left: ast.Expression = parse_term()
        while peek().text in ['+', '-']:
            op_token = consume()
            right = parse_term()
            left = ast.BinaryOp(left=left, op=op_token.text, right=right)
        return left

    def parse_term() -> ast.Expression:
        left: ast.Expression = parse_factor()
        while peek().text in ['*', '/']:
            op_token = consume()
            right = parse_factor()
            left = ast.BinaryOp(left=left, op=op_token.text, right=right)
        return left    

    def parse_factor() -> ast.Expression:
        if peek().text == '(':
            return parse_parenthesized_expression()
        elif peek().text == 'if':
            return parse_if_expression()
        elif peek().type == 'int_literal':
            return parse_literal()
        elif peek().type == 'identifier':
            return parse_identifier()
        else:
            raise Exception(f'Unexpected "{peek().text}"')

    def parse_parenthesized_expression() -> ast.Expression:
        consume('(')
        expr = parse_expression()
        consume(')')
        return expr

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

    result = parse_expression()
    if pos < len(tokens):
        raise Exception(f'{tokens[pos].loc}: unexpected "{tokens[pos].text}"')

    return result
