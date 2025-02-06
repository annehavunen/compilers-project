
from compiler import ast
from compiler.parser import parse
from compiler.tokenizer import tokenize, SourceLocation
import pytest


def test_parser() -> None:

    L = SourceLocation(file="arbitrary_file", line=-99, column=-99)

    assert parse(tokenize("a")) == ast.Identifier(L, "a")

    assert parse(tokenize("1")) == ast.Literal(L, 1)

    assert parse(tokenize("1 + 2")) == ast.BinaryOp(
        location=L,
        left=ast.Literal(L, 1),
        op="+",
        right=ast.Literal(L, 2),
    )

    assert parse(tokenize("11 - 3")) == ast.BinaryOp(
        location=L,
        left=ast.Literal(L, 11),
        op="-",
        right=ast.Literal(L, 3),
    )

    assert parse(tokenize("1 + 2 + 3")) == ast.BinaryOp(
        location=L,
        left=ast.BinaryOp(
            location=L,
            left=ast.Literal(L, 1),
            op="+",
            right=ast.Literal(L, 2)
        ),
        op="+",
        right=ast.Literal(L, 3)
    )

    assert parse(tokenize("1 + 2 * 3")) == ast.BinaryOp(
        location=L,
        left=ast.Literal(L, 1),
        op="+",
        right=ast.BinaryOp(
            location=L,
            left=ast.Literal(L, 2),
            op="*",
            right=ast.Literal(L, 3)
        ),
    )

    assert parse(tokenize("1 * 5 + 2 * 3")) == ast.BinaryOp(
        location=L,
        left=ast.BinaryOp(
            location=L,
            left=ast.Literal(L, 1),
            op="*",
            right=ast.Literal(L, 5)
        ),
        op="+",
        right=ast.BinaryOp(
            location=L,
            left=ast.Literal(L, 2),
            op="*",
            right=ast.Literal(L, 3)
        ),
    )

    assert parse(tokenize("1 * (2 + 3)")) == ast.BinaryOp(
        location=L,
        left=ast.Literal(L, 1),
        op="*",
        right=ast.BinaryOp(
            location=L,
            left=ast.Literal(L, 2),
            op="+",
            right=ast.Literal(L, 3),
        ),
    )

    assert parse(tokenize("(2 + 3) * 4")) == ast.BinaryOp(
        location=L,
        left=ast.BinaryOp(
            location=L,
            left=ast.Literal(L, 2),
            op="+",
            right=ast.Literal(L, 3),
        ),
        op="*",
        right=ast.Literal(L, 4),
    )

    assert parse(tokenize("1 * (2 + 3) / 4")) == ast.BinaryOp(
        location=L,
        left=ast.BinaryOp(
            location=L,
            left=ast.Literal(L, 1),
            op="*",
            right=ast.BinaryOp(
                location=L,
                left=ast.Literal(L, 2),
                op="+",
                right=ast.Literal(L, 3),
            ),
        ),
        op="/",
        right=ast.Literal(L, 4),
    )

    assert parse(tokenize("1 < 2 + 3")) == ast.BinaryOp(
        location=L,
        left=ast.Literal(L, 1),
        op="<",
        right=ast.BinaryOp(
            location=L,
            left=ast.Literal(L, 2),
            op="+",
            right=ast.Literal(L, 3),
        ),
    )

    assert parse(tokenize("x * (1 / (2 + 3))")) == ast.BinaryOp(
        location=L,
        left=ast.Identifier(L, "x"),
        op="*",
        right=ast.BinaryOp(
            location=L,
            left=ast.Literal(L, 1),
            op="/",
            right=ast.BinaryOp(
                location=L,
                left=ast.Literal(L, 2),
                op="+",
                right=ast.Literal(L, 3)
            )
        )
    )

    assert parse(tokenize("10 * 3 % 2")) == ast.BinaryOp(
        location=L,
        left=ast.BinaryOp(
            location=L,
            left=ast.Literal(L, 10),
            op="*",
            right=ast.Literal(L, 3)
        ),
        op="%",
        right=ast.Literal(L, 2)
    )

    assert parse(tokenize("n >= 4 + 12")) == ast.BinaryOp(
        location=L,
        left=ast.Identifier(L, "n"),
        op=">=",
        right=ast.BinaryOp(
            location=L,
            left=ast.Literal(L, 4),
            op="+",
            right=ast.Literal(L, 12)
        )
    )

    assert parse(tokenize("n != 1 / 2")) == ast.BinaryOp(
        location=L,
        left=ast.Identifier(L, "n"),
        op="!=",
        right=ast.BinaryOp(
            location=L,
            left=ast.Literal(L, 1),
            op="/",
            right=ast.Literal(L, 2)
        )
    )

    assert parse(tokenize("x = 1")) == ast.BinaryOp(
        location=L,
        left=ast.Identifier(L, "x"),
        op="=",
        right=ast.Literal(L, 1)
    )

    assert parse(tokenize("x = y = -1")) == ast.BinaryOp(
        location=L,
        left=ast.Identifier(L, "x"),
        op="=",
        right=ast.BinaryOp(
            location=L,
            left=ast.Identifier(L, "y"),
            op="=",
            right=ast.UnaryOp(L, op="-", exp=ast.Literal(L, 1))
        )
    )

    assert parse(tokenize("if 1 then 2")) == ast.IfExpression(
        location=L,
        cond=ast.Literal(L, 1),
        then_clause=ast.Literal(L, 2),
        else_clause=None,
    )

    assert parse(tokenize("if if_ then 2")) == ast.IfExpression(
        location=L,
        cond=ast.Identifier(L, "if_"),
        then_clause=ast.Literal(L, 2),
        else_clause=None,
    )

    assert parse(tokenize("if 1 then 2 else 3")) == ast.IfExpression(
        location=L,
        cond=ast.Literal(L, 1),
        then_clause=ast.Literal(L, 2),
        else_clause=ast.Literal(L, 3),
    )

    assert parse(tokenize("if 1 + 2 then 2 * 3 else 3 / 4")) == ast.IfExpression(
        location=L,
        cond=ast.BinaryOp(L, ast.Literal(L, 1), "+", ast.Literal(L, 2)),
        then_clause=ast.BinaryOp(L, ast.Literal(L, 2), "*", ast.Literal(L, 3)),
        else_clause=ast.BinaryOp(L, ast.Literal(L, 3), "/", ast.Literal(L, 4)),
    )

    assert parse(tokenize("0 + if 1 then 2 else 3")) == ast.BinaryOp(
        location=L,
        left=ast.Literal(L, 0),
        op="+",
        right=ast.IfExpression(
            location=L,
            cond=ast.Literal(L, 1),
            then_clause=ast.Literal(L, 2),
            else_clause=ast.Literal(L, 3),
        )
    )

    assert parse(tokenize("if 1 then (if a then b) else 3")) == ast.IfExpression(
        location=L,
        cond=ast.Literal(L, 1),
        then_clause=ast.IfExpression(
            location=L,
            cond=ast.Identifier(L, "a"),
            then_clause=ast.Identifier(L, "b"),
            else_clause=None,
        ),
        else_clause=ast.Literal(L, 3),
    )

    assert parse(tokenize("if 1 then if a then b else 3")) == ast.IfExpression(
        location=L,
        cond=ast.Literal(L, 1),
        then_clause=ast.IfExpression(
            location=L,
            cond=ast.Identifier(L, "a"),
            then_clause=ast.Identifier(L, "b"),
            else_clause=ast.Literal(L, 3),
        ),
        else_clause=None,
    )

    assert parse(tokenize("if a or b == 2 then 1")) == ast.IfExpression(
        location=L,
        cond=ast.BinaryOp(
            location=L,
            left=ast.Identifier(L, "a"),
            op="or",
            right=ast.BinaryOp(
                location=L,
                left=ast.Identifier(L, "b"),
                op="==",
                right=ast.Literal(L, 2)
            )
        ),
        then_clause=ast.Literal(L, 1),
        else_clause=None
    )

    assert parse(tokenize("if (a or b) == 2 then 1")) == ast.IfExpression(
        location=L,
        cond=ast.BinaryOp(
            location=L,
            left=ast.BinaryOp(
                location=L,
                left=ast.Identifier(L, "a"),
                op="or",
                right=ast.Identifier(L, "b")
            ),
            op="==",
            right=ast.Literal(L, 2)
        ),
        then_clause=ast.Literal(L, 1),
        else_clause=None
    )

    assert parse(tokenize("a == 1 or b <= 2 + 3")) == ast.BinaryOp(
        location=L,
        left=ast.BinaryOp(
            location=L,
            left=ast.Identifier(L, "a"),
            op="==",
            right=ast.Literal(L, 1)
        ),
        op="or",
        right=ast.BinaryOp(
            location=L,
            left=ast.Identifier(L, "b"),
            op="<=",
            right=ast.BinaryOp(
                location=L,
                left=ast.Literal(L, 2),
                op="+",
                right=ast.Literal(L, 3)
            )
        )
    )

    assert parse(tokenize("f()")) == ast.FunctionCall(
        location=L,
        name="f",
        arguments=[],
    )

    assert parse(tokenize("print_int(a - 1)")) == ast.FunctionCall(
        location=L,
        name="print_int",
        arguments=[ast.BinaryOp(
            location=L,
            left=ast.Identifier(L, "a"),
            op="-",
            right=ast.Literal(L, 1)
        )],
    )

    assert parse(tokenize("f(x, y + z, 1)")) == ast.FunctionCall(
        location=L,
        name="f",
        arguments=[ast.Identifier(L, "x"),
            ast.BinaryOp(
                location=L,
                left=ast.Identifier(L, "y"),
                op="+",
                right=ast.Identifier(L, "z")
            ),
            ast.Literal(L, 1)
        ],
    )

    assert parse(tokenize("f(if a then b, (2 + 3) * 4)")) == ast.FunctionCall(
        location=L,
        name="f",
        arguments=[ast.IfExpression(
            location=L,
            cond=ast.Identifier(L, "a"),
            then_clause=ast.Identifier(L, "b"),
            else_clause=None,
        ), ast.BinaryOp(
            location=L,
            left=ast.BinaryOp(
                location=L,
                left=ast.Literal(L, 2),
                op="+",
                right=ast.Literal(L, 3)
            ),
            op="*",
            right=ast.Literal(L, 4)
        )],
    )

    assert parse(tokenize("f(fun())")) == ast.FunctionCall(
        location=L,
        name="f",
        arguments=[ast.FunctionCall(
            location=L,
            name="fun",
            arguments=[]
        )],
    )

    assert parse(tokenize("10 * test()")) == ast.BinaryOp(
        location=L,
        left=ast.Literal(L, 10),
        op="*",
        right=ast.FunctionCall(
            location=L,
            name="test",
            arguments=[]
        )
    )

    assert parse(tokenize("if f() then a")) == ast.IfExpression(
        location=L,
        cond=ast.FunctionCall(location=L, name="f", arguments=[]),
        then_clause=ast.Identifier(L, "a"),
        else_clause=None
    )

    assert parse(tokenize("f(x = n != -2)")) == ast.FunctionCall(
        location=L,
        name="f",
        arguments=[ast.BinaryOp(
            location=L,
            left=ast.Identifier(L, "x"),
            op="=",
            right=ast.BinaryOp(
                location=L,
                left=ast.Identifier(L, "n"),
                op="!=",
                right=ast.UnaryOp(location=L, op="-", exp=ast.Literal(L, 2))
            )
        )]
    )

    assert parse(tokenize("-1")) == ast.UnaryOp(
        location=L,
        op="-",
        exp=ast.Literal(L, 1)
    )

    assert parse(tokenize("1 + -2")) == ast.BinaryOp(
        location=L,
        left=ast.Literal(L, 1),
        op="+",
        right=ast.UnaryOp(
            location=L,
            op="-",
            exp=ast.Literal(L, 2)
        )
    )

    assert parse(tokenize("not not x")) == ast.UnaryOp(
        location=L,
        op="not",
        exp=ast.UnaryOp(
            location=L,
            op="not",
            exp=ast.Identifier(L, "x")
        )
    )

    assert parse(tokenize("if not a then 1 else -2")) == ast.IfExpression(
        location=L,
        cond=ast.UnaryOp(
            location=L,
            op="not",
            exp=ast.Identifier(L, "a")
        ),
        then_clause=ast.Literal(L, 1),
        else_clause=ast.UnaryOp(
            location=L,
            op="-",
            exp=ast.Literal(L, 2)
        )
    )

    assert parse(tokenize("if while a do {b} then c")) == ast.IfExpression(
        location=L,
        cond=ast.WhileExpression(
            location=L,
            cond=ast.Identifier(L, "a"),
            do_clause=ast.Block(L, [ast.Identifier(L, "b")])
        ), then_clause=ast.Identifier(L, "c"),
        else_clause=None
    )

    assert parse(tokenize("while a do b")) == ast.WhileExpression(
        location=L,
        cond=ast.Identifier(L, "a"),
        do_clause=ast.Identifier(L, "b")
    )

    assert parse(tokenize("while not a do b")) == ast.WhileExpression(
        location=L,
        cond=ast.UnaryOp(location=L, op="not", exp=ast.Identifier(L, "a")),
        do_clause=ast.Identifier(L, "b")
    )

    assert parse(tokenize("while a do while b do c")) == ast.WhileExpression(
        location=L,
        cond=ast.Identifier(L, "a"),
        do_clause=ast.WhileExpression(
            location=L,
            cond=ast.Identifier(L, "b"),
            do_clause=ast.Identifier(L, "c")
        )
    )

    assert parse(tokenize("var a = 1")) == ast.VarDeclaration(
        location=L,
        name="a",
        value=ast.Literal(L, 1)
    )

    assert parse(tokenize("var x = if a then b")) == ast.VarDeclaration(
        location=L,
        name="x",
        value=ast.IfExpression(
            location=L,
            cond=ast.Identifier(L, "a"),
            then_clause=ast.Identifier(L, "b"),
            else_clause=None
        )
    )

    assert parse(tokenize("{}")) == ast.Block(
        location=L,
        arguments=[]
    )

    assert parse(tokenize("{a}")) == ast.Block(
        location=L,
        arguments=[ast.Identifier(L, "a")]
    )

    assert parse(tokenize("{a;}")) == ast.Block(
        location=L,
        arguments=[ast.Identifier(L, "a"), ast.Literal(L, None)]
    )

    assert parse(tokenize("{a;b;c;}")) == ast.Block(
        location=L,
        arguments=[ast.Identifier(L, "a"),
                   ast.Identifier(L, "b"),
                   ast.Identifier(L, "c"),
                   ast.Literal(L, None)]
    )

    assert parse(tokenize("{var x = 1 + 2; print_int(x)}")) == ast.Block(
        location=L,
        arguments=[
            ast.VarDeclaration(
                location=L,
                name="x",
                value=ast.BinaryOp(
                    location=L,
                    left=ast.Literal(L, 1),
                    op="+",
                    right=ast.Literal(L, 2)
                )
            ),
            ast.FunctionCall(
                location=L,
                name="print_int",
                arguments=[ast.Identifier(L, "x")]
            )
        ]
    )

    assert parse(tokenize("{a; {b}}")) == ast.Block(
        location=L,
        arguments=[
            ast.Identifier(L, "a"),
            ast.Block(location=L, arguments=[ast.Identifier(L, "b")])
        ]
    )

    assert parse(tokenize("{{a} {b}}")) == ast.Block(
        location=L,
        arguments=[
            ast.Block(location=L, arguments=[ast.Identifier(L, "a")]),
            ast.Block(location=L, arguments=[ast.Identifier(L, "b")])
        ]
    )

    assert parse(tokenize("{if true then {a} b}")) == ast.Block(
        location=L,
        arguments=[
            ast.IfExpression(
                location=L,
                cond=ast.Literal(L, True),
                then_clause=ast.Block(location=L, arguments=[ast.Identifier(L, "a")]),
                else_clause=None
            ), ast.Identifier(L, "b")
        ]
    )

    assert parse(tokenize("{if false then {a} b; c}")) == ast.Block(
        location=L,
        arguments=[
            ast.IfExpression(
                location=L,
                cond=ast.Literal(L, False),
                then_clause=ast.Block(location=L, arguments=[ast.Identifier(L, "a")]),
                else_clause=None
            ), ast.Identifier(L, "b"),
            ast.Identifier(L, "c"),
        ]
    )

    assert parse(tokenize("if true then {a} else {b} c")) == ast.Block(
        location=L,
        arguments=[
            ast.IfExpression(
                location=L,
                cond=ast.Literal(L, True),
                then_clause=ast.Block(location=L, arguments=[ast.Identifier(L, "a")]),
                else_clause=ast.Block(location=L, arguments=[ast.Identifier(L, "b")])
            ), ast.Identifier(L, "c")
        ]
    )

    assert parse(tokenize("x = { { f(a) } { b } }")) == ast.BinaryOp(
        location=L,
        left=ast.Identifier(L, "x"),
        op="=",
        right=ast.Block(
            location=L,
            arguments=[ast.Block( location=L, arguments=[ast.FunctionCall(
                    location=L, name="f", arguments=[ast.Identifier(L, "a")]
                )]), ast.Block(location=L, arguments=[ast.Identifier(L, "b")])
            ]
        )
    )

    assert parse(tokenize("{while a do {b} c}")) == ast.Block(
        location=L,
        arguments=[ast.WhileExpression(
            location=L,
            cond=ast.Identifier(L, "a"),
            do_clause=ast.Block(location=L, arguments=[ast.Identifier(L, "b")])
        ), ast.Identifier(L, "c")]
    )

    assert parse(tokenize("{var x = {a} b}")) == ast.Block(
        location=L,
        arguments=[ast.VarDeclaration(location=L, name="x", value=ast.Block(
            location=L, arguments=[ast.Identifier(L, "a")]
        )), ast.Identifier(L, "b")]
    )

    assert parse(tokenize("{var x = if true then {a} b}")) == ast.Block(
        location=L,
        arguments=[ast.VarDeclaration(location=L, name="x", value=ast.IfExpression(
            location=L,
            cond=ast.Literal(L, True),
            then_clause=ast.Block(location=L, arguments=[ast.Identifier(L, "a")]),
            else_clause=None
        )), ast.Identifier(L, "b")]
    )

    assert parse(tokenize("if a then {var x = 1; var y = 2}")) == ast.IfExpression(
        location=L,
        cond=ast.Identifier(L, "a"),
        then_clause=ast.Block(
            location=L,
            arguments=[ast.VarDeclaration(location=L, name="x", value=ast.Literal(L, 1)),
                       ast.VarDeclaration(location=L, name="y", value=ast.Literal(L, 2))]
        ), else_clause=None
    )

    assert parse(tokenize("while {var x = 1} do a")) == ast.WhileExpression(
        location=L,
        cond=ast.Block(
            location=L,
            arguments=[ast.VarDeclaration(location=L, name="x", value=ast.Literal(L, 1))]
        ), do_clause=ast.Identifier(L, "a")
    )

    assert parse(tokenize("a;")) == ast.Block(
        location=L,
        arguments=[ast.Identifier(L, "a"),
                   ast.Literal(L, None)
        ]
    )

    assert parse(tokenize("a;b")) == ast.Block(
        location=L,
        arguments=[ast.Identifier(L, "a"),
                   ast.Identifier(L, "b")]
    )

    assert parse(tokenize("a;b;")) == ast.Block(
        location=L,
        arguments=[
            ast.Identifier(L, "a"),
            ast.Identifier(L, "b"),
            ast.Literal(L, None)
        ]
    )

    assert parse(tokenize("{a}{b};")) == ast.Block(
        location=L,
        arguments=[ast.Block(L, [ast.Identifier(L, "a")]),
                   ast.Block(L, [ast.Identifier(L, "b")]),
                   ast.Literal(L, None)
                ]
    )

    assert parse(tokenize("{{a}{b};}")) == ast.Block(
        location=L,
        arguments=[ast.Block(L, [ast.Identifier(L, "a")]),
                   ast.Block(L, [ast.Identifier(L, "b")]),
                   ast.Literal(L, None)
                ]
    )

    assert parse(tokenize("{} then")) == ast.Block(
        location=L,
        arguments=[ast.Block(L, []), ast.Identifier(L, "then")]
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
        parse(tokenize("f(1; 2)"))

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
        parse(tokenize(";"))

    with pytest.raises(Exception):
        parse(tokenize("{a b}"))

    with pytest.raises(Exception):
        parse(tokenize("{a {b}}"))

    with pytest.raises(Exception):
        parse(tokenize("{a, b}"))

    with pytest.raises(Exception):
        parse(tokenize("a {b}"))

    with pytest.raises(Exception):
        parse(tokenize("if a then var x = 1"))

    with pytest.raises(Exception):
        parse(tokenize("while var x = 1 do a"))

    with pytest.raises(Exception):
        parse(tokenize("f(var x = 1)"))

    with pytest.raises(Exception):
        parse(tokenize("{if true then {a} b c}"))


def test_parser_location() -> None:

    L = SourceLocation(file="arbitrary_file", line=-99, column=-99)
    loc1 = SourceLocation(file="other_file", line=0, column=0)
    loc2 = SourceLocation(file="other_file", line=1, column=2)

    assert ast.Identifier(L, "a") != ast.Identifier(L, "b")
    assert ast.Identifier(L, "a") == ast.Identifier(loc1, "a")
    assert ast.Identifier(loc1, "a") != ast.Identifier(loc2, "a")
    assert ast.Literal(L, 1) != ast.Literal(L, 2)
    assert ast.Identifier(L, "a") != ast.Literal(L, 1)

    loc = SourceLocation(file="file_name", line=0, column=0)
    assert parse(tokenize("a")) == ast.Identifier(loc, "a")

    loc1 = SourceLocation(file="file_name", line=0, column=0)
    loc2 = SourceLocation(file="file_name", line=0, column=2)
    loc3 = SourceLocation(file="file_name", line=0, column=4)
    assert parse(tokenize("1 + 2")) == ast.BinaryOp(
        location=loc2,
        left=ast.Literal(loc1, 1),
        op="+",
        right=ast.Literal(loc3, 2),
    )

    loc1 = SourceLocation(file="file_name", line=0, column=0)
    loc2 = SourceLocation(file="file_name", line=0, column=6)
    loc3 = SourceLocation(file="file_name", line=0, column=7)
    loc4 = SourceLocation(file="file_name", line=0, column=15)
    loc5 = SourceLocation(file="file_name", line=0, column=21)
    assert parse(tokenize("while {var x = 1} do a")) == ast.WhileExpression(
        location=loc1,
        cond=ast.Block(
            location=loc2,
            arguments=[ast.VarDeclaration(location=loc3, name="x", value=ast.Literal(loc4, 1))]
        ), do_clause=ast.Identifier(loc5, "a")
    )

    loc1 = SourceLocation(file="file_name", line=0, column=0)
    loc2 = SourceLocation(file="file_name", line=0, column=1)
    loc3 = SourceLocation(file="file_name", line=0, column=2)
    assert parse(tokenize("{a;}")) == ast.Block(
        location=loc1,
        arguments=[ast.Identifier(loc2, "a"), ast.Literal(loc3, None)]
    )

    loc1 = SourceLocation(file="file_name", line=0, column=0)
    loc2 = SourceLocation(file="file_name", line=0, column=4)
    loc3 = SourceLocation(file="file_name", line=0, column=6)
    assert parse(tokenize("fun(f(hello))")) == ast.FunctionCall(
        location=loc1,
        name="fun",
        arguments=[ast.FunctionCall(
            location=loc2,
            name="f",
            arguments=[ast.Identifier(loc3, "hello")]
        )]
    )
