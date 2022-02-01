from typing import Any, List, Optional
import re
from rithm.parser import ParseError
from rithm.token import Token, TokenType as TT

# from __future__ import annotations
IDENTIFIER_START = r"[^\W0-9]"
IDENTIFIER_MIDDLE = r"[^\W]"


class ScanningException(SyntaxError):
    pass


class UnmatchedTokenException(ScanningException):
    pass


class UnmatchedQuoteException(UnmatchedTokenException):
    pass


class Scanner:
    def __init__(self, source: str):
        self.source = source
        self.current = 0
        self.start = 0
        self.line = 1
        self.column = 1

        self.tokens = []

    def __str__(self) -> str:
        return (
            f"Scanner(source={self.source!r}, current={self.current}, line={self.line})"
        )

    @property
    def current_lexeme(self) -> str:
        return self.source[self.start : self.current]

    @property
    def is_at_end(self) -> bool:
        return self.current >= len(self.source)

    def raise_exception(self, exception):
        # TODO: Do a better thing here. This hides the line location info in the parent exception.
        raise exception from ScanningException(
            f"Scanning exception occurred at line {self.line}"
        )

    def scan_tokens(self) -> List[Token]:
        while not self.is_at_end:
            self.start = self.current
            self.scan_token()

        self.tokens.append(
            Token(
                token_type=TT.EOF,
                lexeme="",
                literal=None,
                line_no=self.line,
                column=self.column,  # current_lexeme will be the LAST lexeme, since we don't update self.start
                                     # So, we just use the column, which is the end of the last lexeme
            )
        )
        return self.tokens

    def scan_token(self):
        char = self.advance_and_get_char()

        match char:
            # Single characters
            case "@":
                self.add_token(TT.AT_SIGN)
            case "#":
                self.add_token(TT.OCTOTHORPE)
            case ",":
                self.add_token(TT.COMMA)
            case ".":
                self.add_token(TT.DOT)
            case ";":
                self.add_token(TT.SEMICOLON)
            case ":":
                self.add_token(TT.COLON)
            case "!":
                self.add_token(TT.BANG)
            case "*":
                self.add_token(TT.STAR)
            case "/":
                self.add_token(TT.SLASH)
            case "+":
                self.add_token(TT.PLUS)
            case "-":
                if self.match(">"):
                    self.advance_and_get_char()
                    self.add_token(TT.ARROW_RIGHT)
                else:
                    self.add_token(TT.MINUS)
            case "?":
                self.add_token(TT.QUESTION_MARK)
            
            # Whitespace
            case " ":
                while self.match(" "):
                    char += self.advance_and_get_char()
                self.add_token(TT.SPACE)
            case "\t":
                while self.match("\t"):
                    char += self.advance_and_get_char()
                self.add_token(TT.TAB)
            case "\n":
                self.add_token(TT.NEWLINE)
                self.column = 1
                self.line += 1
            
            # Comparisons and arrows
            case "=":
                if self.match("="):
                    char += self.advance_and_get_char()
                    if self.match(">"):
                        char += self.advance_and_get_char()
                        self.add_token(TT.DBL_ARROW_RIGHT)
                    else:
                        self.add_token(TT.EQUAL_EQUAL)
                elif self.match(">"):
                    char += self.advance_and_get_char()
                    self.add_token(TT.DBL_ARROW_RIGHT)
                # elif self.match(">"):
                #     char += self.advance_and_get_char()
                #     self.add_token(TT.GREATER_EQUAL)
                else:
                    self.add_token(TT.EQUAL)
            case ">":
                if self.match("="):
                    char += self.advance_and_get_char()
                    self.add_token(TT.GREATER_EQUAL)
                else:
                    self.add_token(TT.GREATER_THAN)
            case "<":
                if self.match("="):
                    char += self.advance_and_get_char
                    self.add_token(TT.LESS_EQUAL)
                elif self.match("-"):
                    char += self.advance_and_get_char()
                    self.add_token(TT.ARROW_LEFT)
                else:
                    self.add_token(TT.LESS_THAN)

            # Delimiters
            case "(":
                self.add_token(TT.PAREN_OPEN)
            case ")":
                self.add_token(TT.PAREN_CLOSE)
            case "[":
                self.add_token(TT.BRACKET_OPEN)
            case "]":
                self.add_token(TT.BRACKET_CLOSE)
            case "{":
                self.add_token(TT.BRACE_OPEN)
            case "}":
                self.add_token(TT.BRACE_CLOSE)
            case "`":
                self.add_token(TT.TICK_OPEN)
            case "'":
                self.add_token(TT.TICK_CLOSE)
            
            # Literals
            case '"':
                self.add_string()
            case d if re.match(r"\d", d):
                self.add_number()

            # Reserved words
            case c if re.match(IDENTIFIER_START, c):  # Variable name / identifier
                self.add_identifier()


    def advance(self):
        self.current += 1
        self.column += 1

    def advance_and_get_char(self) -> str:
        self.advance()
        return self.source[self.current - 1]

    def _peek(self, chars: int = 1) -> str:
        # if self.is_at_end:
        #     return None
        return self.source[self.current - 1 + chars]

    def peek(self) -> str:
        return self._peek()

    def peek_two(self) -> str:
        return self._peek(2)

    def match(self, expected: str, regex: bool = False) -> bool:
        if self.is_at_end:
            return False
        if regex:
            return re.match(expected, self.peek())
        return self.peek() == expected

    def add_token(self, token_type: TT, literal: Any = None):
        """Add token at current location"""
        self.tokens.append(
            Token(
                token_type=token_type,
                lexeme=self.current_lexeme,
                literal=literal,
                line_no=self.line,
                column=self.column - len(self.current_lexeme),
            )
        )

    def add_string(self):
        try:
            while self.peek() != '"':
                self.advance()
            else:
                # Advance to consume ending quote
                self.advance()
        except IndexError:
            self.raise_exception(UnmatchedQuoteException("No closing quote found"))

        self.add_token(TT.STRING, literal=self.current_lexeme)

    def add_number(self):
        is_decimal = False
        try:
            while re.match(r"\d", self.peek()):
                self.advance()

            if self.match("."):
                is_decimal = True
                self.advance()
                try:
                    has_digit = False
                    while re.match(r"\d", self.peek()):
                        has_digit = True
                        self.advance()

                except IndexError:
                    if not has_digit:
                        self.raise_exception(
                            ScanningException("Trailing decimal not allowed")
                        )
                self.add_token(TT.FLOAT, literal=float(self.current_lexeme))
                return

        except IndexError:
            pass

        self.add_token(TT.INTEGER, literal=int(self.current_lexeme))

    def add_identifier(self):
        try:
            while self.match(IDENTIFIER_MIDDLE, regex=True):
                self.advance()
        except IndexError:
            pass

        match self.current_lexeme:
            case "class":
                self.add_token(TT.CLASS)
            case "and":
                self.add_token(TT.AND)
            case "or":
                self.add_token(TT.OR)
            case "True":
                self.add_token(TT.TRUE)
            case "False":
                self.add_token(TT.FALSE)
            case _:
                self.add_token(TT.IDENTIFIER)

    # def add_colname(self):
    #     try:
    #         if not self.match(VARNAME_START, regex=True):
    #             raise ScanningException("Colname must start with valid character")
    #     except IndexError:
    #         raise ScanningException("Colname cannot have length 0")

    #     try:
    #         self.advance()

    #         while self.match(VARNAME_MIDDLE, regex=True):
    #             self.advance()

    #     except IndexError:
    #         pass

    #     self.add_token(TT.COLNAME)
