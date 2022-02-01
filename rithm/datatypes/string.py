from dataclasses import dataclass
from rithm.datatypes.literal import Literal


@dataclass
class String(Literal):
    value: str
