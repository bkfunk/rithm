

from dataclasses import dataclass
from typing import Dict


@dataclass
class Namespace:
    values: Dict
    enclosing: "Namespace" = None

