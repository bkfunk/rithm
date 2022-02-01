from dataclasses import dataclass


@dataclass
class Doc:
    """
    A piece of documentation, which can be associated with different Rithm objects.
    """

    contents: str
