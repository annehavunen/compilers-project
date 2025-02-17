
from compiler.tokenizer import tokenize
from compiler.parser import parse
from compiler.type_checker import typecheck
from compiler.types import Bool, Int, Unit


def test_type_checker() -> None:
    assert typecheck(parse(tokenize('1 + 2'))) == Int
    assert typecheck(parse(tokenize('1 + 2 < 3'))) == Bool
    assert typecheck(parse(tokenize('if 1 < 2 then 3'))) == Unit
    assert typecheck(parse(tokenize('if 1 < 2 then 3 else 4'))) == Int
    assert typecheck(parse(tokenize('if 1 < 2 then 3 < 4 else 4 < 5'))) == Bool
    assert typecheck(parse(tokenize('print_int(1)'))) == Unit
    assert typecheck(parse(tokenize('print_bool(false)'))) == Unit
    assert typecheck(parse(tokenize('read_int()'))) == Int

    assert_fails_typecheck('(1 < 3) + 3')
    assert_fails_typecheck('if 1 then 3 else 4')
    assert_fails_typecheck('if 1 < 2 then 3 else 4 < 5')
    assert_fails_typecheck('print_int(true)')
    assert_fails_typecheck('print_bool(1)')
    assert_fails_typecheck('read_int(1)')

def assert_fails_typecheck(code: str) -> None:
    expr = parse(tokenize(code))
    failed = False
    try:
        typecheck(expr)
    except Exception:
        failed = True
    assert failed, f"Type-checking succeeded for: {code}"
