from dataclasses import dataclass
from typing import Any, List
from rithm.datatypes.docs import Doc

from rithm.stmt import Stmt


@dataclass
class Algo:
    """
    An algorithm, consisting of multiple steps
    """

    name: str
    docs: Doc
    steps: List[Stmt]

    def __getitem__(self, item):
        pass

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        pass
