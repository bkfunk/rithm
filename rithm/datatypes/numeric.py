from rithm.datatypes.literal import Literal
from dataclasses import dataclass


class Numeric(Literal):
    pass


@dataclass
class Integer(Numeric):
    value: int


@dataclass
class Float(Numeric):
    value: float
