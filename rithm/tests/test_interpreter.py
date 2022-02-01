from rithm.rithm import Rithm

rtm = Rithm()


def test_rithm_repr():
    assert str(rtm) == "Rithm()"
    assert rtm == Rithm()
    assert str(Rithm(x=1)) == "Rithm(x=1)"


def test_basic_interpret():
    # breakpoint()
    assert rtm().evaluate("2 + 3") == 5
    rtm("x = 3 + 4")
    assert rtm.x == 7
    assert rtm["x"] == 7
