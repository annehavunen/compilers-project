
from compiler.tokenizer import tokenize
from compiler.parser import parse
from compiler.type_checker import typecheck, build_type_symtab, TypeSymTab
from compiler.types import Bool, Int, Unit


def test_type_checker() -> None:
    t = build_type_symtab()

    assert typecheck(parse(tokenize('1 + 2')), t) == Int
    assert typecheck(parse(tokenize('1 - 2')), t) == Int
    assert typecheck(parse(tokenize('1 * 2')), t) == Int
    assert typecheck(parse(tokenize('4 / 2')), t) == Int
    assert typecheck(parse(tokenize('4 % 2')), t) == Int
    assert typecheck(parse(tokenize('1 + 2 < 3')), t) == Bool
    assert typecheck(parse(tokenize('2 > 3 + 1')), t) == Bool
    assert typecheck(parse(tokenize('2 >= 3 or 1 <= 2')), t) == Bool
    assert typecheck(parse(tokenize('true and false')), t) == Bool
    assert typecheck(parse(tokenize('if 1 < 2 then 3')), t) == Unit
    assert typecheck(parse(tokenize('1 + if 1 < 2 then 3 else 4')), t) == Int
    assert typecheck(parse(tokenize('if 1 < 2 then 3 < 4 else 4 < 5')), t) == Bool
    assert typecheck(parse(tokenize('1 + if 1 < 2 then 3 else 4')), t) == Int
    assert typecheck(parse(tokenize('print_int(1 * 2)')), t) == Unit
    assert typecheck(parse(tokenize('print_bool(3 == 1)')), t) == Unit
    assert typecheck(parse(tokenize('read_int()')), t) == Int
    assert typecheck(parse(tokenize('var x = 1')), t) == Unit
    assert typecheck(parse(tokenize('var y = -1 + 2')), t) == Unit
    assert typecheck(parse(tokenize('var z = 2; z')), t) == Int
    assert typecheck(parse(tokenize('var a = if true then 1; a')), t) == Unit
    assert typecheck(parse(tokenize('var b = if true then 1 else 2; b')), t) == Int
    assert typecheck(parse(tokenize('-2')), t) == Int
    assert typecheck(parse(tokenize('not (1 < 2)')), t) == Bool
    assert typecheck(parse(tokenize('- if 1 < 2 then 3 else 4')), t) == Int
    assert typecheck(parse(tokenize('1 == 2')), t) == Bool
    assert typecheck(parse(tokenize('1 < 2 != 2 < 3')), t) == Bool
    assert typecheck(parse(tokenize('1;')), t) == Unit
    assert typecheck(parse(tokenize('1;2')), t) == Int
    assert typecheck(parse(tokenize('{}')), t) == Unit
    t = build_type_symtab()
    assert typecheck(parse(tokenize('{var a = 1} var a = 2')), t) == Unit
    assert typecheck(parse(tokenize('var a = 1; {var a = 2}')), t) == Unit
    assert typecheck(parse(tokenize('var b = {var c = true; c}; b')), t) == Bool
    assert typecheck(parse(tokenize('var c = 2; c = 3')), t) == Int
    assert typecheck(parse(tokenize('var x = {}; x = if true then 2')), t) == Unit
    assert typecheck(parse(tokenize('var y = while true do y + 1; y')), t) == Unit
    assert typecheck(parse(tokenize('while {var z = 1 > 2; z} do 1')), t) == Unit
    t = build_type_symtab()
    assert typecheck(parse(tokenize('var a: Int = 2; a')), t) == Int
    assert typecheck(parse(tokenize('var b: Bool = false; b')), t) == Bool
    assert typecheck(parse(tokenize('var c: Unit = if true then 2; c')), t) == Unit
    assert typecheck(parse(tokenize('var x: Int = 1 + 1; var y = x = 3; x')), t) == Int

    expr = parse(tokenize('1 + 2'))
    assert expr.type == Unit
    assert typecheck(expr, t) == Int
    assert expr.type == Int

    expr = parse(tokenize('var z: Bool = 2 != 3'))
    assert typecheck(expr, t) == Unit
    assert expr.type == Unit

    t = build_type_symtab()
    assert_fails_typecheck('(1 < 3) + 3', t)
    assert_fails_typecheck('true < 3', t)
    assert_fails_typecheck('true and 3', t)
    assert_fails_typecheck('1 or 3', t)
    assert_fails_typecheck('-false', t)
    assert_fails_typecheck('not 1', t)
    assert_fails_typecheck('true == 1', t)
    assert_fails_typecheck('if 1 then 3 else 4', t)
    assert_fails_typecheck('if 1 < 2 then 3 else 4 < 5', t)
    assert_fails_typecheck('1 + if true then 2', t)
    assert_fails_typecheck('print_int(true)', t)
    assert_fails_typecheck('print_bool(1)', t)
    assert_fails_typecheck('read_int(1)', t)
    assert_fails_typecheck('var x = 1; var x = 2', t)
    assert_fails_typecheck('var y = {}; var y = 2', t)
    assert_fails_typecheck('z = 2', t)
    assert_fails_typecheck('1 = 2', t)
    assert_fails_typecheck('while 2 do 1', t)
    assert_fails_typecheck('var a: Bool = 2', t)
    assert_fails_typecheck('var b: bool = true', t)
    assert_fails_typecheck('var c: something = 1', t)
    assert_fails_typecheck('var x: Int = 2; var y = x = true', t)

def assert_fails_typecheck(code: str, t: TypeSymTab) -> None:
    expr = parse(tokenize(code))
    failed = False
    try:
        typecheck(expr, t)
    except Exception:
        failed = True
    assert failed, f"Type-checking succeeded for: {code}"
