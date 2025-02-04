
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

    assert parse(tokenize("x * (1 / (2 + 3))")) == ast.BinaryOp(
        left=ast.Identifier("x"),
        op="*",
        right=ast.BinaryOp(
            left=ast.Literal(1),
            op="/",
            right=ast.BinaryOp(
                left=ast.Literal(2),
                op="+",
                right=ast.Literal(3)
            )
        )
    )

    assert parse(tokenize("10 * 3 % 2")) == ast.BinaryOp(
        left=ast.BinaryOp(
            left=ast.Literal(10),
            op="*",
            right=ast.Literal(3)
        ),
        op="%",
        right=ast.Literal(2)
    )

    assert parse(tokenize("n >= 4 + 12")) == ast.BinaryOp(
        left=ast.Identifier("n"),
        op=">=",
        right=ast.BinaryOp(
            left=ast.Literal(4),
            op="+",
            right=ast.Literal(12)
        )
    )

    assert parse(tokenize("n != 1 / 2")) == ast.BinaryOp(
        left=ast.Identifier("n"),
        op="!=",
        right=ast.BinaryOp(
            left=ast.Literal(1),
            op="/",
            right=ast.Literal(2)
        )
    )

    assert parse(tokenize("x = 1")) == ast.BinaryOp(
        left=ast.Identifier("x"),
        op="=",
        right=ast.Literal(1)
    )

    assert parse(tokenize("x = y = -1")) == ast.BinaryOp(
        left=ast.Identifier("x"),
        op="=",
        right=ast.BinaryOp(
            left=ast.Identifier("y"),
            op="=",
            right=ast.UnaryOp(op="-", exp=ast.Literal(1))
        )
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

    assert parse(tokenize("if a or b == 2 then 1")) == ast.IfExpression(
        cond=ast.BinaryOp(
            left=ast.Identifier("a"),
            op="or",
            right=ast.BinaryOp(
                left=ast.Identifier("b"),
                op="==",
                right=ast.Literal(2)
            )
        ),
        then_clause=ast.Literal(1),
        else_clause=None
    )

    assert parse(tokenize("if (a or b) == 2 then 1")) == ast.IfExpression(
        cond=ast.BinaryOp(
            left=ast.BinaryOp(
                left=ast.Identifier("a"),
                op="or",
                right=ast.Identifier("b")
            ),
            op="==",
            right=ast.Literal(2)
        ),
        then_clause=ast.Literal(1),
        else_clause=None
    )

    assert parse(tokenize("a == 1 or b <= 2 + 3")) == ast.BinaryOp(
        left=ast.BinaryOp(
            left=ast.Identifier("a"),
            op="==",
            right=ast.Literal(1)
        ),
        op="or",
        right=ast.BinaryOp(
            left=ast.Identifier("b"),
            op="<=",
            right=ast.BinaryOp(
                left=ast.Literal(2),
                op="+",
                right=ast.Literal(3)
            )
        )
    )

    assert parse(tokenize("f()")) == ast.FunctionCall(
        name="f",
        arguments=[],
    )

    assert parse(tokenize("print_int(1)")) == ast.FunctionCall(
        name="print_int",
        arguments=[ast.Literal(1)],
    )

    assert parse(tokenize("f(a - 1)")) == ast.FunctionCall(
        name="f",
        arguments=[ast.BinaryOp(
            left=ast.Identifier("a"),
            op="-",
            right=ast.Literal(1)
        )],
    )

    assert parse(tokenize("f(x, y + z, 1)")) == ast.FunctionCall(
        name="f",
        arguments=[ast.Identifier("x"),
            ast.BinaryOp(
                left=ast.Identifier("y"),
                op="+",
                right=ast.Identifier("z")
            ),
            ast.Literal(1)
        ],
    )

    assert parse(tokenize("f(if a then b, (2 + 3) * 4)")) == ast.FunctionCall(
        name="f",
        arguments=[ast.IfExpression(
            cond=ast.Identifier("a"),
            then_clause=ast.Identifier("b"),
            else_clause=None,
        ), ast.BinaryOp(
            left=ast.BinaryOp(
                left=ast.Literal(2),
                op="+",
                right=ast.Literal(3)
            ),
            op="*",
            right=ast.Literal(4)
        )],
    )

    assert parse(tokenize("f(fun())")) == ast.FunctionCall(
        name="f",
        arguments=[ast.FunctionCall(
            name="fun",
            arguments=[]
        )],
    )

    assert parse(tokenize("10 * test()")) == ast.BinaryOp(
        left=ast.Literal(10),
        op="*",
        right=ast.FunctionCall(
            name="test",
            arguments=[]
        )
    )

    assert parse(tokenize("if f() then a")) == ast.IfExpression(
        cond=ast.FunctionCall(name="f", arguments=[]),
        then_clause=ast.Identifier("a"),
        else_clause=None
    )

    assert parse(tokenize("f(x = n != -2)")) == ast.FunctionCall(
        name="f",
        arguments=[ast.BinaryOp(
            left=ast.Identifier("x"),
            op="=",
            right=ast.BinaryOp(
                left=ast.Identifier("n"),
                op="!=",
                right=ast.UnaryOp(op="-", exp=ast.Literal(2))
            )
        )]
    )

    assert parse(tokenize("-1")) == ast.UnaryOp(
        op="-",
        exp=ast.Literal(1)
    )

    assert parse(tokenize("1 + -2")) == ast.BinaryOp(
        left=ast.Literal(1),
        op="+",
        right=ast.UnaryOp(
            op="-",
            exp=ast.Literal(2)
        )
    )

    assert parse(tokenize("not not x")) == ast.UnaryOp(
        op="not",
        exp=ast.UnaryOp(
            op="not",
            exp=ast.Identifier("x")
        )
    )

    assert parse(tokenize("if not a then 1 else -2")) == ast.IfExpression(
        cond=ast.UnaryOp(
            op="not",
            exp=ast.Identifier("a")
        ),
        then_clause=ast.Literal(1),
        else_clause=ast.UnaryOp(
            op="-",
            exp=ast.Literal(2)
        )
    )

    assert parse(tokenize("while a do b")) == ast.WhileExpression(
        cond=ast.Identifier("a"),
        do_clause=ast.Identifier("b")
    )

    assert parse(tokenize("while not a do b")) == ast.WhileExpression(
        cond=ast.UnaryOp(op="not", exp=ast.Identifier("a")),
        do_clause=ast.Identifier("b")
    )

    assert parse(tokenize("while a do while b do c")) == ast.WhileExpression(
        cond=ast.Identifier("a"),
        do_clause=ast.WhileExpression(
            cond=ast.Identifier("b"),
            do_clause=ast.Identifier("c")
        )
    )

    assert parse(tokenize("var a = 1")) == ast.VarDeclaration(
        name="a",
        value=ast.Literal(1)
    )

    assert parse(tokenize("var x = if a then b")) == ast.VarDeclaration(
        name="x",
        value=ast.IfExpression(
            cond=ast.Identifier("a"),
            then_clause=ast.Identifier("b"),
            else_clause=None
        )
    )

    assert parse(tokenize("{}")) == ast.Block(
        arguments=[]
    )

    assert parse(tokenize("{a}")) == ast.Block(
        arguments=[ast.Identifier("a")]
    )

    assert parse(tokenize("{a;}")) == ast.Block(
        arguments=[ast.Identifier("a"), ast.Literal(None)]
    )

    assert parse(tokenize("{a;b;c;}")) == ast.Block(
        arguments=[ast.Identifier("a"),
                   ast.Identifier("b"),
                   ast.Identifier("c"),
                   ast.Literal(None)]
    )

    assert parse(tokenize("{x = y;}")) == ast.Block(
        arguments=[ast.BinaryOp(
            left=ast.Identifier("x"),
            op="=",
            right=ast.Identifier("y")
        ), ast.Literal(None)]
    )

    assert parse(tokenize("{var x = 1 + 2; print_int(x)}")) == ast.Block(
        arguments=[
            ast.VarDeclaration(
                name="x",
                value=ast.BinaryOp(
                    left=ast.Literal(1),
                    op="+",
                    right=ast.Literal(2)
                )
            ),
            ast.FunctionCall(
                name="print_int",
                arguments=[ast.Identifier("x")]
            )
        ]
    )

    assert parse(tokenize("{a; {b}}")) == ast.Block(
        arguments=[
            ast.Identifier("a"),
            ast.Block(
                arguments=[ast.Identifier("b")]
            )
        ]
    )

    assert parse(tokenize("{{a} {b}}")) == ast.Block(
        arguments=[
            ast.Block(arguments=[ast.Identifier("a")]),
            ast.Block(arguments=[ast.Identifier("b")])
        ]
    )

    assert parse(tokenize("{if true then {a} b}")) == ast.Block(
        arguments=[
            ast.IfExpression(
                cond=ast.Identifier("true"),
                then_clause=ast.Block(arguments=[ast.Identifier("a")]),
                else_clause=None
            ), ast.Identifier("b")
        ]
    )

    assert parse(tokenize("{if true then {a}; b}")) == ast.Block(
        arguments=[
            ast.IfExpression(
                cond=ast.Identifier("true"),
                then_clause=ast.Block(arguments=[ast.Identifier("a")]),
                else_clause=None
            ), ast.Identifier("b")
        ]
    )

    assert parse(tokenize("{if true then {a} b; c}")) == ast.Block(
        arguments=[
            ast.IfExpression(
                cond=ast.Identifier("true"),
                then_clause=ast.Block(arguments=[ast.Identifier("a")]),
                else_clause=None
            ), ast.Identifier("b"),
            ast.Identifier("c"),
        ]
    )

    assert parse(tokenize("{if true then {a} else {b} c}")) == ast.Block(
        arguments=[
            ast.IfExpression(
                cond=ast.Identifier("true"),
                then_clause=ast.Block(arguments=[ast.Identifier("a")]),
                else_clause=ast.Block(arguments=[ast.Identifier("b")])
            ), ast.Identifier("c")
        ]
    )

    assert parse(tokenize("x = { { f(a) } { b } }")) == ast.BinaryOp(
        left=ast.Identifier("x"),
        op="=",
        right=ast.Block(
            arguments=[ast.Block(
                arguments=[ast.FunctionCall(
                    name="f", arguments=[ast.Identifier("a")]
                )]
            ), ast.Block(
                arguments=[ast.Identifier("b")]
            )]
        )
    )

    assert parse(tokenize("{while a do {b} c}")) == ast.Block(
        arguments=[ast.WhileExpression(
            cond=ast.Identifier("a"),
            do_clause=ast.Block(arguments=[ast.Identifier("b")])
        ), ast.Identifier("c")]
    )

    assert parse(tokenize("{var x = {a} b}")) == ast.Block(
        arguments=[ast.VarDeclaration(name="x", value=ast.Block(
            arguments=[ast.Identifier("a")]
        )), ast.Identifier("b")]
    )

    assert parse(tokenize("{var x = if true then {a} b}")) == ast.Block(
        arguments=[ast.VarDeclaration(name="x", value=ast.IfExpression(
            cond=ast.Identifier("true"),
            then_clause=ast.Block(arguments=[ast.Identifier("a")]),
            else_clause=None
        )), ast.Identifier("b")]
    )

    assert parse(tokenize("if a then {var x = 1; var y = 2}")) == ast.IfExpression(
        cond=ast.Identifier("a"),
        then_clause=ast.Block(
            arguments=[ast.VarDeclaration(name="x", value=ast.Literal(1)),
                       ast.VarDeclaration(name="y", value=ast.Literal(2))]
        ), else_clause=None
    )

    assert parse(tokenize("while {var x = 1} do a")) == ast.WhileExpression(
        cond=ast.Block(
            arguments=[ast.VarDeclaration(name="x", value=ast.Literal(1))]
        ), do_clause=ast.Identifier("a")
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

    with pytest.raises(Exception):
        parse(tokenize("f(1,)"))

    with pytest.raises(Exception):
        parse(tokenize("f(1("))

    with pytest.raises(Exception):
        parse(tokenize("not"))

    with pytest.raises(Exception):
        parse(tokenize("while a"))

    with pytest.raises(Exception):
        parse(tokenize("var a"))

    with pytest.raises(Exception):
        parse(tokenize("{a, b}"))

    with pytest.raises(Exception):
        parse(tokenize("{;}"))

    with pytest.raises(Exception):
        parse(tokenize("{a b}"))

    with pytest.raises(Exception):
        parse(tokenize("{a {b}}"))

    with pytest.raises(Exception):
        parse(tokenize("if a then var x = 1"))

    with pytest.raises(Exception):
        parse(tokenize("while var x = 1 do a"))

    with pytest.raises(Exception):
        parse(tokenize("f(var x = 1)"))

    with pytest.raises(Exception):
        parse(tokenize("{if true then {a} b c}"))
