from compiler.tokenizer import Token, tokenize, SourceLocation
import pytest


def test_tokenizer_basics() -> None:
    L = SourceLocation(file="arbitrary_file", line=-99, column=-99)

    assert tokenize("hello") == [
        Token(loc=L, type='identifier', text='hello')
    ]

    assert tokenize("  \n  hi  \n\n") == [
        Token(loc=L, type='identifier', text="hi")
    ]

    assert tokenize(" hi number 1 ") == [
        Token(loc=L, type='identifier', text="hi"),
        Token(loc=L, type='identifier', text="number"),
        Token(loc=L, type='int_literal', text="1")
    ]

    assert tokenize("3 + -5") == [
        Token(loc=L, type="int_literal", text='3'),
        Token(loc=L, type="operator", text='+'),
        Token(loc=L, type="operator", text='-'),
        Token(loc=L, type="int_literal", text='5'),
    ]

    assert tokenize("3 + -(1 + 2)") == [
        Token(loc=L, type='int_literal', text='3'),
        Token(loc=L, type='operator', text='+'),
        Token(loc=L, type='operator', text='-'),
        Token(loc=L, type='punctuation', text='('),
        Token(loc=L, type='int_literal', text='1'),
        Token(loc=L, type='operator', text='+'),
        Token(loc=L, type='int_literal', text='2'),
        Token(loc=L, type='punctuation', text=')'),
    ]

    assert tokenize("3-1") == [
        Token(loc=L, type="int_literal", text='3'),
        Token(loc=L, type="operator", text='-'),
        Token(loc=L, type="int_literal", text='1'),
    ]

    assert tokenize("n >= 1") == [
        Token(loc=L, type="identifier", text='n'),
        Token(loc=L, type="operator", text='>='),
        Token(loc=L, type="int_literal", text='1'),
    ]

    assert tokenize("print_int(3 * x);") == [
        Token(loc=L, type="identifier", text='print_int'),
        Token(loc=L, type="punctuation", text='('),
        Token(loc=L, type="int_literal", text='3'),        
        Token(loc=L, type="operator", text='*'),
        Token(loc=L, type="identifier", text='x'),
        Token(loc=L, type="punctuation", text=')'),
        Token(loc=L, type="punctuation", text=';'),
    ]

    assert tokenize("x = x / 2") == [
        Token(loc=L, type="identifier", text='x'),
        Token(loc=L, type="operator", text='='),
        Token(loc=L, type="identifier", text='x'),
        Token(loc=L, type="operator", text='/'),
        Token(loc=L, type="int_literal", text='2'),       
    ]

    assert tokenize("if x == 22 then {") == [
        Token(loc=L, type="identifier", text='if'),
        Token(loc=L, type="identifier", text='x'),
        Token(loc=L, type="operator", text='=='),
        Token(loc=L, type="int_literal", text='22'),
        Token(loc=L, type="identifier", text='then'),
        Token(loc=L, type="punctuation", text='{'),
    ]

    assert tokenize("// x < 11 \n x < 11") == [
        Token(loc=L, type="identifier", text='x'),
        Token(loc=L, type="operator", text='<'),
        Token(loc=L, type="int_literal", text='11'),       
    ]

    assert tokenize("#\nx > 1") == [
        Token(loc=L, type="identifier", text='x'),
        Token(loc=L, type="operator", text='>'),
        Token(loc=L, type="int_literal", text='1'),       
    ]

    assert tokenize("x % 2") == [
        Token(loc=L, type="identifier", text='x'),
        Token(loc=L, type="operator", text='%'),
        Token(loc=L, type="int_literal", text='2'),
    ]

    assert tokenize("true") == [
        Token(loc=L, type="bool_literal", text="true")
    ]

    assert tokenize("false") == [
        Token(loc=L, type="bool_literal", text="false")
    ]

    assert tokenize("var x: Int = 1") == [
        Token(loc=L, type="identifier", text="var"),
        Token(loc=L, type="identifier", text="x"),
        Token(loc=L, type="punctuation", text=":"),
        Token(loc=L, type="identifier", text="Int"),
        Token(loc=L, type="operator", text="="),
        Token(loc=L, type="int_literal", text="1"),
    ]

    with pytest.raises(Exception):
        tokenize("a@")

def test_tokenizer_location() -> None:

    loc = SourceLocation(file="file_name", line=0, column=0)
    assert tokenize("hello") == [
        Token(loc=loc, type='identifier', text='hello')
    ]

    loc1 = SourceLocation(file="file_name", line=0, column=0)
    loc2 = SourceLocation(file="file_name", line=2, column=0)
    assert tokenize("hello\n\nworld") == [
        Token(loc=loc1, type='identifier', text="hello"),
        Token(loc=loc2, type='identifier', text="world"),
    ]

    loc1 = SourceLocation(file="file_name", line=0, column=0)
    loc2 = SourceLocation(file="file_name", line=1, column=2)
    assert tokenize("hello  \n  world") == [
        Token(loc=loc1, type='identifier', text="hello"),
        Token(loc=loc2, type='identifier', text="world"),
    ]

    loc1 = SourceLocation(file="file_name", line=0, column=0)
    loc2 = SourceLocation(file="file_name", line=0, column=2)
    loc3 = SourceLocation(file="file_name", line=0, column=4)
    assert tokenize("1 + 2") == [
        Token(loc=loc1, type='int_literal', text="1"),
        Token(loc=loc2, type='operator', text="+"),
        Token(loc=loc3, type='int_literal', text="2"),
    ]

    loc1 = SourceLocation(file="file_name", line=0, column=0)
    loc2 = SourceLocation(file="file_name", line=0, column=1)
    loc3 = SourceLocation(file="file_name", line=0, column=2)
    loc4 = SourceLocation(file="file_name", line=0, column=7)
    loc5 = SourceLocation(file="file_name", line=0, column=9)
    assert tokenize("3-name + 1") == [
        Token(loc=loc1, type='int_literal', text="3"),
        Token(loc=loc2, type='operator', text="-"),
        Token(loc=loc3, type='identifier', text="name"),
        Token(loc=loc4, type='operator', text="+"),
        Token(loc=loc5, type='int_literal', text="1"),
    ]
