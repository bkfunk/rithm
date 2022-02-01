from typing import Any, Container, List, Optional, Sequence, Tuple
from enum import Enum, auto
from dataclasses import dataclass


class TokenType(Enum):
    # Delimiters
    PAREN_OPEN = "("
    PAREN_CLOSE = ")"
    BRACE_OPEN = "{"
    BRACE_CLOSE = "}"
    BRACKET_OPEN = "["
    BRACKET_CLOSE = "]"
    TICK_OPEN = "`"
    TICK_CLOSE = "'"

    # Single character
    QUESTION_MARK = "?"
    AT_SIGN = "@"
    OCTOTHORPE = "#"
    COMMA = ","
    DOT = "."
    SEMICOLON = ";"
    COLON = ":"
    BANG = "!"
    QUOTE = '"'
    STAR = "*"
    SLASH = "/"
    PLUS = "+"
    MINUS = "-"
    NEWLINE = "\n"

    # Literals
    TAB = "\t"
    SPACE = " "
    IDENTIFIER = auto()
    # COLNAME = auto()
    STRING = auto()
    INTEGER = auto()
    FLOAT = auto()

    # Operators
    EQUAL = "="
    EQUAL_EQUAL = "=="
    LESS_THAN = "<"
    LESS_EQUAL = "<="
    GREATER_THAN = ">"
    GREATER_EQUAL = ">="

    # Arrows
    ARROW_LEFT = "<-"
    ARROW_RIGHT = "->"
    DBL_ARROW_LEFT = "<=="
    DBL_ARROW_RIGHT = "==>"

    # Reserved Words
    IF = "if"
    AS = "as"
    TRUE = "True"
    FALSE = "False"
    CLASS = "class"
    ALGO = "algo"
    AND = "and"
    OR = "or"

    # Other
    EOF = auto()


@dataclass
class Token:
    token_type: TokenType
    lexeme: str
    literal: Any
    line_no: int
    column: int


def token_types(
    tokens: List[Token],
    ignore: Optional[Container[TokenType]] = (
        TokenType.SPACE,
        TokenType.NEWLINE,
        TokenType.TAB,
        TokenType.EOF,
    ),
) -> List[TokenType]:
    if ignore is None:
        ignore = []
    return [token.token_type for token in tokens if token.token_type not in ignore]
