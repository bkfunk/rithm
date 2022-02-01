from dataclasses import Field, dataclass, field
from functools import wraps
from typing import Callable, Container, List, Sequence, Tuple, Optional, Union
from rithm.expr import Assignment, Binary, Expr, Grouping, Identifier, Literal, Unary
from rithm.logging import get_logger
from rithm.stmt import ExpressionStmt, IfStmt, Stmt
import logging
from rithm.logging import get_logger

from rithm.token import Token, TokenType as TT
from rich import print
from rich.pretty import pretty_repr

WHITESPACE = (TT.SPACE, TT.TAB)

parse_logger = get_logger(__name__)


class ParseError(Exception):
    pass


def logged(fn):
    @wraps(fn)
    def log_fn(parser, *args, **kwargs):
        # tokens = parser.tokens[parser.current:]
        # tokens_str = ''.join([token.lexeme for token in tokens])
        # token_types = [token.token_type.name for token in tokens]

        indent = parser.depth * " "
        parse_logger.debug(
            f"{indent}{fn.__name__}"
        )  # with tokens: {tokens_str!r} {token_types}")

        parser.depth += 1
        result = fn(parser, *args, **kwargs)
        parser.depth -= 1
        return result

    return log_fn


@dataclass
class Parser:
    tokens: List[Token]
    current: int = field(default=0, init=False)
    depth: int = field(default=0, init=False)

    CLOSING_TOKENS = {
        TT.BRACKET_OPEN: TT.BRACKET_CLOSE,
        TT.PAREN_OPEN: TT.PAREN_CLOSE,
        TT.BRACE_OPEN: TT.BRACE_CLOSE,
    }

    @property
    def is_at_end(self) -> bool:
        # TODO: Should we check for EOF? Or just length of tokens?
        return self.current >= len(self.tokens)

    @property
    def prev_token(self) -> Token:
        return self.tokens[self.current - 1]

    @property
    def current_token(self) -> Token:
        return self.tokens[self.current]

    @property
    def next_token(self) -> Token:
        return self.tokens[self.current + 1]

    # def peek(self) -> Token:
    #     return self.tokens[self.current]

    def consume_and_advance(
        self, ignore: Optional[Container[TT]] = WHITESPACE
    ) -> Token:
        # Return current token, then move cursor
        # (or, equivalently, move cursor and return previous token)
        if ignore is not None:
            parse_logger.debug(f"Ignoring: {ignore}")
            try:
                while self.current_token.token_type in ignore:
                    parse_logger.debug(f"Ignored {self.current}: {self.current_token}")
                    self.current += 1
            except IndexError:
                pass
        parse_logger.debug(f"Consuming {self.current}: {self.current_token}")
        self.current += 1
        if not self.is_at_end:
            parse_logger.debug(
                f"New current token {self.current}: {self.current_token}"
            )
        return self.prev_token

    def match(
        self, *token_types: TT, ignore: Optional[Container[TT]] = WHITESPACE
    ) -> bool:
        if self.is_at_end:
            return False

        _old_current = self.current

        if ignore is not None:
            while self.current_token.token_type in ignore:
                self.current += 1
                if self.is_at_end:
                    self.current = _old_current
                    return False

        if self.current_token.token_type in token_types:
            parse_logger.debug(f"Matched: {self.current_token}")
            self.current = _old_current
            return True
        self.current = _old_current
        return False

    def synchronize(self):
        pass

    def parse(self) -> List[Stmt]:
        parse_logger.debug(f"Parsing tokens: {pretty_repr(self.tokens)}")
        # parse_logger.debug(self.tokens)
        stmts = []
        while not self.is_at_end:
            try:
                stmts.append(self.parse_declaration())
            except ParseError:
                self.synchronize()
        return stmts

    def parse_declaration(self) -> Stmt:
        parsed = self.parse_statement()
        return parsed

    @logged
    def parse_statement(self) -> Stmt:
        self.depth = 0

        if self.match(TT.IF):
            return self.parse_if_statement()

        # if self.match(TT.IDENTIFIER):

        parsed = self.parse_expression()

        # if self.match(TT.EQUAL):
        #     return self.parse_assigment_stmt()
        #     self.consume_and_advance()
        #     return AssignmentStmt(expr.token.lexeme, None)

        if self.match(TT.NEWLINE, TT.EOF):
            self.consume_and_advance()
            if isinstance(parsed, Expr):
                return ExpressionStmt(parsed)
            return parsed
        raise ParseError("Statements must end in newline")

    @logged
    def parse_if_statement(self) -> IfStmt:
        # TODO: What should delimit the if statement?
        return IfStmt()

    # @logged
    # def parse_assigment_or_higher(self) -> Union[Expr, Stmt]:

    @logged
    def parse_expression(self) -> Expr:
        # return self.parse_equality_or_higher()
        return self.parse_assignment_or_higher()

    @logged
    def parse_assignment_or_higher(self) -> Expr:
        expr = self.parse_equality_or_higher()

        if self.match(TT.EQUAL):
            equals = self.consume_and_advance()
            value = self.parse_assignment_or_higher()

            if isinstance(expr, Identifier):
                return self.log_and_parse(Assignment(expr.token, value))
        return expr

    def _parse_binary(
        self,
        higher_method: Callable,
        matching_tokens: Sequence[TT],
        ignore: Optional[Container[TT]] = WHITESPACE,
    ):
        next_expr = higher_method()

        while self.match(*matching_tokens, ignore=ignore):
            operator = self.consume_and_advance(ignore=ignore)
            right = higher_method()
            next_expr = self.log_and_parse(
                Binary(left=next_expr, operator=operator, right=right)
            )

        return next_expr

    @logged
    def parse_equality_or_higher(self) -> Expr:
        return self._parse_binary(
            higher_method=self.parse_comparison_or_higher,
            matching_tokens=(TT.EQUAL_EQUAL,),
        )

    @logged
    def parse_comparison_or_higher(self) -> Expr:
        return self._parse_binary(
            higher_method=self.parse_add_sub_or_higher,
            matching_tokens=(
                TT.LESS_THAN,
                TT.LESS_EQUAL,
                TT.GREATER_THAN,
                TT.GREATER_EQUAL,
            ),
        )
        # next_expr = self.parse_add_sub_or_higher()

        # while self.match(TT.PLUS, TT.MINUS):
        #     comparison_operator = self.consume_and_advance()
        #     right = self.parse_add_sub_or_higher()
        #     next_expr = Binary(left=next_expr, operator=comparison_operator, right=right)

        # return next_expr

    @logged
    def parse_add_sub_or_higher(self) -> Expr:
        return self._parse_binary(
            higher_method=self.parse_mult_div_or_higher,
            matching_tokens=(TT.PLUS, TT.MINUS),
        )

    @logged
    def parse_mult_div_or_higher(self) -> Expr:
        return self._parse_binary(
            higher_method=self.parse_unary_or_higher,
            matching_tokens=(TT.STAR, TT.SLASH),
        )

    @logged
    def parse_unary_or_higher(self) -> Expr:
        if self.match(TT.BANG, TT.MINUS):
            operator = self.consume_and_advance()
            expr = self.parse_unary_or_higher()
            return self.log_and_parse(Unary(operator=operator, expr=expr))

        # If not a unary, than it must be a literal
        return self.parse_literal()

    @logged
    def parse_literal(self) -> Expr:
        literal_token = self.consume_and_advance()
        match literal_token.token_type:
            case TT.NEWLINE:
                # Ignore empty lines
                return None
            case TT.FALSE:
                return self.log_and_parse(
                    Literal(value=False, token_type=literal_token.token_type)
                )
            case TT.TRUE:
                return self.log_and_parse(
                    Literal(value=True, token_type=literal_token.token_type)
                )
            case TT.STRING | TT.INTEGER | TT.FLOAT:
                return self.log_and_parse(
                    Literal(literal_token.literal, token_type=literal_token.token_type)
                )
            case TT.PAREN_OPEN | TT.BRACE_OPEN | TT.BRACKET_OPEN:
                expr = self.parse_expression()
                if self.match(self.CLOSING_TOKENS[literal_token.token_type]):
                    close_paren = self.consume_and_advance()
                    return self.log_and_parse(
                        Grouping(
                            expr,
                            open_token_type=literal_token.token_type,
                            close_token_type=close_paren.token_type,
                        )
                    )

                self.raise_error(
                    f"Opening delimiter {literal_token.token_type.value} has no closing delimiter"
                )
            case TT.IDENTIFIER:
                return self.log_and_parse(Identifier(literal_token))

        self.raise_error(f"Could not parse {literal_token}")

    def raise_error(self, msg: str):
        parse_logger.error(msg)
        raise ParseError(msg)

    def log_and_parse(self, expr: Expr) -> Expr:
        parse_logger.debug(f"Parsed {expr}")
        return expr
