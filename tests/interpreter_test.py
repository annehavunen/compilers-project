import pytest
from compiler.interpreter import interpret, SymTab
from compiler.parser import parse
from compiler.tokenizer import tokenize


def test_interpreter() -> None:
    s = SymTab()
    assert interpret(parse(tokenize('1 + 2')), s) == 3
    assert interpret(parse(tokenize('1 + 2 * 3')), s) == 7
    assert interpret(parse(tokenize('if 1 < 2 then 3 else 4')), s) == 3
    assert interpret(parse(tokenize('if 2 < 1 then 3 else 4')), s) == 4
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
    assert interpret(parse(tokenize('var x = 1; {var x = 1; x}; var y = 2')), s) == None

    s = SymTab()
    with pytest.raises(Exception):
        interpret(parse(tokenize('var x = 1; var x = 2')), s)
    s = SymTab()
    with pytest.raises(Exception):
        interpret(parse(tokenize('x')), s)
