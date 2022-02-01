import pytest
from rithm.rithm import Rithm
from rithm.scanner import ScanningException
from rithm.token import TokenType as TT, token_types

rtm = Rithm()


def test_basic_scan():
    tokens = rtm().scan("x =  3")
    assert token_types(tokens, ignore=None) == [
        TT.IDENTIFIER,
        TT.SPACE,
        TT.EQUAL,
        TT.SPACE,
        TT.INTEGER,
        TT.EOF,
    ]
    assert token_types(tokens) == [
        TT.IDENTIFIER,
        TT.EQUAL,
        TT.INTEGER,
    ]

    assert token_types(rtm().scan("foo >= 10 + -1.5")) == [
        TT.IDENTIFIER,
        TT.GREATER_EQUAL,
        TT.INTEGER,
        TT.PLUS,
        TT.MINUS,
        TT.FLOAT,
    ]

    with pytest.raises(ScanningException):
        rtm().scan('"foo')

def test_scan_arrows():
    arrow_with_spaces = rtm().scan("x -> foo")
    assert token_types(
        arrow_with_spaces,
        ignore=None
    ) == [
        TT.IDENTIFIER, TT.SPACE, TT.ARROW_RIGHT, TT.SPACE, TT.IDENTIFIER
    ]

    arrow_without_spaces = rtm().scan("x->foo")
    assert token_types(arrow_without_spaces) == token_types(arrow_with_spaces)


