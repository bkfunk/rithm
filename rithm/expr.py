from dataclasses import dataclass
from typing import Any
from rithm.token import Token, TokenType as TT
from abc import ABC

from rithm.visitor import Visitor


@dataclass
class Expr:
    def accept(self, visitor: Visitor):
        method_name = f"visit_{self.__class__.__name__.lower()}_expr"
        method = getattr(visitor, method_name)
        return method(self)


@dataclass
class Literal(Expr):
    value: Any
    token_type: TT


@dataclass
class Identifier(Expr):
    token: Token


@dataclass
class Assignment(Expr):
    name: Token
    value: Expr


@dataclass
class Binary(Expr):
    left: Expr
    operator: Token
    right: Expr


@dataclass
class Unary(Expr):
    operator: Token
    expr: Expr


@dataclass
class Grouping(Expr):
    expr: Expr
    open_token_type: TT
    close_token_type: TT
