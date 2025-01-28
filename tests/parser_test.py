
from compiler import ast
from compiler.parser import parse
from compiler.tokenizer import tokenize
import pytest


def test_parser() -> None:
    assert parse(tokenize("1 + 2")) == ast.BinaryOp(
        left=ast.Literal(1),
        op="+",
        right=ast.Literal(2),
    )

    assert parse(tokenize("11 - 3")) == ast.BinaryOp(
        left=ast.Literal(11),
        op="-",
        right=ast.Literal(3),
    )

    assert parse(tokenize("1 + 2 + 3")) == ast.BinaryOp(
        left=ast.BinaryOp(
            left=ast.Literal(1),
            op="+",
            right=ast.Literal(2)
        ),
        op="+",
        right=ast.Literal(3)
    )

    assert parse(tokenize("1 + 2 * 3")) == ast.BinaryOp(
        left=ast.Literal(1),
        op="+",
        right=ast.BinaryOp(
            left=ast.Literal(2),
            op="*",
            right=ast.Literal(3)
        ),
    )

    assert parse(tokenize("1 * 5 + 2 * 3")) == ast.BinaryOp(
        left=ast.BinaryOp(
            left=ast.Literal(1),
            op="*",
            right=ast.Literal(5)
        ),
        op="+",
        right=ast.BinaryOp(
            left=ast.Literal(2),
            op="*",
            right=ast.Literal(3)
        ),
    )

    assert parse(tokenize("1")) == ast.Literal(1)

    assert parse(tokenize("a")) == ast.Identifier("a")

    assert parse(tokenize("1 * (2 + 3)")) == ast.BinaryOp(
        left=ast.Literal(1),
        op="*",
        right=ast.BinaryOp(
            left=ast.Literal(2),
            op="+",
            right=ast.Literal(3),
        ),
    )

    assert parse(tokenize("(2 + 3) * 4")) == ast.BinaryOp(
        left=ast.BinaryOp(
            left=ast.Literal(2),
            op="+",
            right=ast.Literal(3),
        ),
        op="*",
        right=ast.Literal(4),
    )

    assert parse(tokenize("1 * (2 + 3) / 4")) == ast.BinaryOp(
        left=ast.BinaryOp(
            left=ast.Literal(1),
            op="*",
            right=ast.BinaryOp(
                left=ast.Literal(2),
                op="+",
                right=ast.Literal(3),
            ),
        ),
        op="/",
        right=ast.Literal(4),
    )

    assert parse(tokenize("1 < 2 + 3")) == ast.BinaryOp(
        left=ast.Literal(1),
        op="<",
        right=ast.BinaryOp(
            left=ast.Literal(2),
            op="+",
            right=ast.Literal(3),
        ),
    )

    assert parse(tokenize("x + 2")) == ast.BinaryOp(
        left=ast.Identifier("x"),
        op="+",
        right=ast.Literal(2),
    )

    assert parse(tokenize("if 1 then 2")) == ast.IfExpression(
        cond=ast.Literal(1),
        then_clause=ast.Literal(2),
        else_clause=None,
    )

    assert parse(tokenize("if if_ then 2")) == ast.IfExpression(
        cond=ast.Identifier("if_"),
        then_clause=ast.Literal(2),
        else_clause=None,
    )

    assert parse(tokenize("if a then b + c")) == ast.IfExpression(
        cond=ast.Identifier("a"),
        then_clause=ast.BinaryOp(
            left=ast.Identifier("b"),
            op="+",
            right=ast.Identifier("c"),
        ),
        else_clause=None,
    )

    assert parse(tokenize("if 1 then 2 else 3")) == ast.IfExpression(
        cond=ast.Literal(1),
        then_clause=ast.Literal(2),
        else_clause=ast.Literal(3),
    )

    assert parse(tokenize("if 1 + 2 then 2 * 3 else 3 / 4")) == ast.IfExpression(
        cond=ast.BinaryOp(ast.Literal(1), "+", ast.Literal(2)),
        then_clause=ast.BinaryOp(ast.Literal(2), "*", ast.Literal(3)),
        else_clause=ast.BinaryOp(ast.Literal(3), "/", ast.Literal(4)),
    )

    assert parse(tokenize("0 + if 1 then 2 else 3")) == ast.BinaryOp(
        left=ast.Literal(0),
        op="+",
        right=ast.IfExpression(
            cond=ast.Literal(1),
            then_clause=ast.Literal(2),
            else_clause=ast.Literal(3),
        )
    )

    assert parse(tokenize("if 1 then (if a then b) else 3")) == ast.IfExpression(
        cond=ast.Literal(1),
        then_clause=ast.IfExpression(
            cond=ast.Identifier("a"),
            then_clause=ast.Identifier("b"),
            else_clause=None,
        ),
        else_clause=ast.Literal(3),
    )

    assert parse(tokenize("if 1 then if a then b else 3")) == ast.IfExpression(
        cond=ast.Literal(1),
        then_clause=ast.IfExpression(
            cond=ast.Identifier("a"),
            then_clause=ast.Identifier("b"),
            else_clause=ast.Literal(3),
        ),
        else_clause=None,
    )

    with pytest.raises(Exception):
        parse(tokenize(""))

    with pytest.raises(Exception):
        parse(tokenize("1 * (2 + 3("))

    with pytest.raises(Exception):
        parse(tokenize("1 - "))

    with pytest.raises(Exception):
        parse(tokenize("a + b c"))
    
    with pytest.raises(Exception):
        parse(tokenize("if"))
