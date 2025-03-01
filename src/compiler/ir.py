
from typing import Any
from dataclasses import dataclass
import dataclasses
from compiler.tokenizer import SourceLocation


@dataclass(frozen=True)
class IRVar:
    name: str

    def __str__(self) -> str:
        return self.name

@dataclass(frozen=True)
class Instruction():
    """Base class for IR instructions"""
    location: SourceLocation

    def __str__(self) -> str:
        """Returns a string representation similar to
        our IR code examples, e.g. 'LoadIntConst(3, x1)'"""
        def format_value(v: Any) -> str:
            if isinstance(v, list):
                return f'[{", ".join(format_value(e) for e in v)}]'
            else:
                return str(v)
        args = ', '.join(
            format_value(getattr(self, field.name))
            for field in dataclasses.fields(self)
            if field.name != 'location'
        )
        return f'{type(self).__name__}({args})'

@dataclass(frozen=True)
class Call(Instruction):
    fun: IRVar
    args: list[IRVar]
    dest: IRVar


@dataclass(frozen=True)
class LoadIntConstant(Instruction):
    value: int
    dest: IRVar

@dataclass(frozen=True)
class LoadBoolConstant(Instruction):
    value: bool
    dest: IRVar

@dataclass(frozen=True)
class Copy(Instruction):
    source: IRVar
    dest: IRVar


@dataclass(frozen=True)
class Label(Instruction):
    name: str


@dataclass(frozen=True)
class Jump(Instruction):
    label: Label


@dataclass(frozen=True)
class CondJump(Instruction):
    cond: IRVar
    then_label: Label
    else_label: Label
