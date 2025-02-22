import pytest
from compiler.interpreter import interpret, build_toplevel_symtab
from compiler.parser import parse
from compiler.tokenizer import tokenize


def test_interpreter() -> None:
    s = build_toplevel_symtab()
    assert interpret(parse(tokenize('1 + 2')), s) == 3
    assert interpret(parse(tokenize('1 + 2 * 3')), s) == 7
    assert interpret(parse(tokenize('4 / -2')), s) == -2
    assert interpret(parse(tokenize('4 % 2')), s) == 0
    assert interpret(parse(tokenize('true == not false')), s) == True
    assert interpret(parse(tokenize('true != false')), s) == True
    assert interpret(parse(tokenize('(1 + 1) >= 2')), s) == True
    assert interpret(parse(tokenize('if 1 <= 2 then 3 else 4')), s) == 3
    assert interpret(parse(tokenize('if 1 > 2 then 3 else 4')), s) == 4
    assert interpret(parse(tokenize('10 + if 2 < 1 then 3 else 4')), s) == 14
    assert interpret(parse(tokenize('if 1 < 2 then 3')), s) == None
    assert interpret(parse(tokenize('if 2 < 1 then 3')), s) == None
    assert interpret(parse(tokenize('{}')), s) == None
    assert interpret(parse(tokenize('{1}{2}')), s) == 2
    assert interpret(parse(tokenize('{1}2')), s) == 2
    assert interpret(parse(tokenize('{1}{2};')), s) == None
    assert interpret(parse(tokenize('1 + 2;')), s) == None
    assert interpret(parse(tokenize('var x = 10; x + 1')), s) == 11
    assert interpret(parse(tokenize('var x = 10')), s) == None
    assert interpret(parse(tokenize('var x = 10; {x}')), s) == 10
    assert interpret(parse(tokenize('var x = 1; {var x = 2; x}')), s) == 2
    assert interpret(parse(tokenize('var x = 1; {x = 2}; x')), s) == 2
    assert interpret(parse(tokenize('var x = 1; x = 2; x')), s) == 2
    assert interpret(parse(tokenize('var x = 1; {var x = 2}; x')), s) == 1
    assert interpret(parse(tokenize('var x = {var y = 1; y}; x')), s) == 1
    assert interpret(parse(tokenize('var x = (1 + 2); var y = x; y')), s) == 3
    assert interpret(parse(tokenize('var x = {} x')), s) == None
    assert interpret(parse(tokenize('var x = if true then 2 else 3; x')), s) == 2
    assert interpret(parse(tokenize('var right = false; true or {right = true; true}; right')), s) == False
    assert interpret(parse(tokenize('var right = false; false or {right = true; true}; right')), s) == True
    assert interpret(parse(tokenize('var right = true; false and {right = false; false}; right')), s) == True
    assert interpret(parse(tokenize('var right = false; true and {right = true; true}; right')), s) == True
    assert interpret(parse(tokenize('false or false')), s) == False
    assert interpret(parse(tokenize('var i = 0; while i < 3 do i = i + 1; i')), s) == 3
    assert interpret(parse(tokenize('var i = 0; while false do i = i + 1; i')), s) == 0
    assert interpret(parse(tokenize('var i = 0; while i < 3 do i = i + 1')), s) == None

    s = build_toplevel_symtab()
    with pytest.raises(Exception):
        interpret(parse(tokenize('var x = 1; var x = 2')), s)
    s = build_toplevel_symtab()
    with pytest.raises(Exception):
        interpret(parse(tokenize('var x = if true then 1; var x = 2')), s)
    s = build_toplevel_symtab()
    with pytest.raises(Exception):
        interpret(parse(tokenize('x')), s)
    s = build_toplevel_symtab()
    with pytest.raises(Exception):
        interpret(parse(tokenize('{var x = 1}; x')), s)
    s = build_toplevel_symtab()
    with pytest.raises(Exception):
        interpret(parse(tokenize('{{var x = 1}; x}')), s)
    s = build_toplevel_symtab()
    with pytest.raises(Exception):
        interpret(parse(tokenize('{var x = 1}{x}')), s)
