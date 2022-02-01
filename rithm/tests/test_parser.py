from rithm.rithm import Rithm
from rithm.stmt import ExpressionStmt
from rich import print

rtm = Rithm()


def test_parser():
    stmts = rtm().parse(
        rtm().scan(
            """ 
    2 + 9.2 + 19

    foo = 3
    """
        )
    )
    print("Statements: ", stmts)
    assert len(stmts) == 2
    assert isinstance(stmts[0], ExpressionStmt)
    assert isinstance(stmts[1], ExpressionStmt)
