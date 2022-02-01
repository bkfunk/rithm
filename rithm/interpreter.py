from types import SimpleNamespace
from typing import Any, List
from rithm.expr import Expr, Literal, Binary
from rithm.stmt import ExpressionStmt, Stmt
from rithm.visitor import Visitor
from rithm.token import TokenType as TT


class Interpreter(Visitor):
    def __init__(self, **namespace):
        self.namespace = namespace

    def __eq__(self, other) -> bool:
        if isinstance(other, type(self)):
            return self.namespace == other.namespace
        return False

    def interpret(self, stmts: List[Stmt]):
        result = None
        try:
            for stmt in stmts:
                result = stmt.accept(self)
        except RuntimeError as e:
            pass

        return result

    # def execute(self, stmt: Stmt):
    #     stmt.accept(self)
    def evaluate(self, expr: Expr):
        return expr.accept(self)

    def visit_literal_expr(self, expr: Literal):
        return expr.value

    def visit_binary_expr(self, expr: Binary):
        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)

        match expr.operator.token_type:
            case TT.PLUS:
                return left + right
        raise Exception("Invalid binary")

    def visit_expression_stmt(self, stmt: ExpressionStmt):
        print(f"Interpreting expression statement: {stmt}")
        return self.evaluate(stmt.expr)

    # def visit_assignment_stmt(self, stmt: AssignmentStmt):
    #     self.namespace[stmt.name] = stmt.value
