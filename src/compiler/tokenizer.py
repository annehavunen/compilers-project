from dataclasses import dataclass
import re
from typing import Literal


@dataclass
class SourceLocation:
    file: str
    line: int
    column: int

# for testing purposes
L = SourceLocation(file="arbitrary_file", line=-99, column=-99)

TokenType = Literal["int_literal", "identifier", "operator", "punctuation", "end"]

@dataclass(frozen=True)
class Token:
    loc: SourceLocation
    type: TokenType
    text: str
    
    def __eq__(self, other: object) -> bool:
        if self is other:
            return True

        if not isinstance(other, Token):
            return False

        if ((self.loc == other.loc or self.loc == L or other.loc == L) and
            self.type == other.type and
            self.text == other.text):            
            return True

        return False

def tokenize(source_code: str, file_name: str = "file_name") -> list[Token]:
    whitespace_re = re.compile(r'\s+')
    integer_re = re.compile(r'[0-9]+')
    identifier_re = re.compile(r'[a-zA-Z_][a-zA-Z0-9_]*')
    operator_re = re.compile(r'==|!=|<=|>=|[-+*/=<>%]')
    punctuation_re = re.compile(r'[(){},;]')
    comment_re = re.compile(r'//.*|#.*')

    position = 0
    line = 0
    column = 0
    result: list[Token] = []

    def append_token(token_type: TokenType, text: str) -> None:
        nonlocal position, column

        location = SourceLocation(file_name, line, column)
        result.append(Token(
            loc=location,
            type=token_type,
            text=text
        ))

        column += len(text)
        position += len(text)

    while position < len(source_code):
        match = comment_re.match(source_code, position)
        if match is not None:
            position = match.end()
            continue

        match = whitespace_re.match(source_code, position)
        if match is not None:
            whitespaces = match.group()
            for whitespace in whitespaces:
                if whitespace == "\n":
                    line += 1
                    column = 0
                elif whitespace == "\t":
                    column += 8
                else:
                    column += 1

            position = match.end()
            continue

        match = identifier_re.match(source_code, position)
        if match is not None:
            append_token("identifier", source_code[position:match.end()])
            continue

        match = integer_re.match(source_code, position)
        if match is not None:
            append_token("int_literal", source_code[position:match.end()])
            continue

        match = operator_re.match(source_code, position)
        if match is not None:
            append_token("operator", source_code[position:match.end()])
            continue

        match = punctuation_re.match(source_code, position)
        if match is not None:
            append_token("punctuation", source_code[position:match.end()])
            continue
        
        raise Exception(f'Tokenization failed near {source_code[position:(position + 10)]}...')

    return result
