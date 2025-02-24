
from dataclasses import dataclass, field
from typing import Any, Optional
from compiler.types import Bool, Int, Unit, FunType


UNDEFINED = object()

@dataclass
class SymTab:
    locals: dict = field(default_factory=dict)
    parent: Optional['SymTab'] = None

    def set(self, name: str, value: Any) -> None:
        self.locals[name] = value

    def get(self, name: str) -> Any:
        if name in self.locals:
            return self.locals[name]
        elif self.parent:
            return self.parent.get(name)
        return UNDEFINED

    def get_local(self, name: str) -> Any:
        if name in self.locals:
            return self.locals[name]
        return UNDEFINED

    def find_scope(self, name: str) -> Any:
        if name in self.locals:
            return self
        if self.parent:
            return self.parent.find_scope(name)
        return UNDEFINED

def build_interpreter_symtab() -> SymTab:
    symtab = SymTab()

    symtab.set('+', lambda a, b: a + b)
    symtab.set('-', lambda a, b: a - b)
    symtab.set('*', lambda a, b: a * b)
    symtab.set('/', lambda a, b: a // b if b != 0 else zero_division_exception())
    symtab.set('%', lambda a, b: a % b)
    symtab.set('==', lambda a, b: a == b)
    symtab.set('!=', lambda a, b: a != b)
    symtab.set('<', lambda a, b: a < b)
    symtab.set('<=', lambda a, b: a <= b)
    symtab.set('>', lambda a, b: a > b)
    symtab.set('>=', lambda a, b: a >= b)
    symtab.set('and', lambda a, b: a and b)
    symtab.set('or', lambda a, b: a or b)
    symtab.set('unary_-', lambda a: -a)
    symtab.set('unary_not', lambda a: not a)
    symtab.set('read_int', lambda: int(input()))
    symtab.set('print_int', lambda a: print(a))
    symtab.set('print_bool', lambda a: print('true') if a else print('false'))

    return symtab

def zero_division_exception() -> None:
    raise Exception("Can't divide by zero")

def build_type_symtab() -> SymTab:
    symtab = SymTab()

    symtab.set('+', FunType([Int, Int], Int))
    symtab.set('-', FunType([Int, Int], Int))
    symtab.set('*', FunType([Int, Int], Int))
    symtab.set('/', FunType([Int, Int], Int))
    symtab.set('%', FunType([Int, Int], Int))
    symtab.set('<', FunType([Int, Int], Bool))
    symtab.set('<=', FunType([Int, Int], Bool))
    symtab.set('>', FunType([Int, Int], Bool))
    symtab.set('>=', FunType([Int, Int], Bool))
    symtab.set('and', FunType([Bool, Bool], Bool))
    symtab.set('or', FunType([Bool, Bool], Bool))
    symtab.set('unary_-', FunType([Int], Int))
    symtab.set('unary_not', FunType([Bool], Bool))
    symtab.set('print_int', FunType([Int], Unit))
    symtab.set('print_bool', FunType([Bool], Unit))
    symtab.set('read_int', FunType([], Int))

    return symtab
