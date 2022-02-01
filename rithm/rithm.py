from abc import ABCMeta
import logging
import sys
from types import SimpleNamespace
from typing import Any, Dict, List, TYPE_CHECKING
from rithm.parser import Parser
from rithm.interpreter import Interpreter
from rithm.scanner import Scanner
# from rich import print, pretty
from rich.pretty import Pretty, pretty_repr
from rithm.logging import get_logger

if TYPE_CHECKING:
    from rithm.token import Token
    from rithm.stmt import Stmt


rithm_logger = get_logger(__name__)

class Rithm:
    def __init__(self, **namespace):
        self.__instance = RithmInstance(**namespace)

    # @property
    # def __namespace(self) -> Dict:
    #     return {
    #         for k, v in self.__instance.namespace.items()
    #         if not k.startswith("__") and not k.startswith("_Rithm")
    #     }

    def __repr__(self):
        items = (f"{k}={v!r}" for k, v in self.__instance.namespace.items())
        return "{}({})".format(type(self).__name__, ", ".join(items))

    def __eq__(self, other):
        if isinstance(self, Rithm) and isinstance(other, Rithm):
            return self.__instance == other.__instance
        return NotImplemented

    def __getattr__(self, name: str) -> Any:
        return self.__instance.namespace[name]
        # return self.__instance.namespace.get(name)
        # if name in self.__instance.namespace:
        #     return self.__
        # if hasattr(self.__instance.namespace, name):
        #     return getattr(self.__instance, name)

    def __getitem__(self, key: Any) -> Any:
        return getattr(self, key)

    def __call__(self, input: str = None, file: str = None, debug: bool = False, result: bool = False):
        if input is None and file is None:
            return self.__instance
        elif input is not None:
            return self.__instance.run_input(input, debug=debug, result=result)
        elif file is not None:
            return self.__instance.run_file(file, debug=debug, result=result)


class RithmInstance:
    # INTERPRETER = Interpreter()

    def __init__(self, **namespace):
        self.interpreter = Interpreter(**namespace)
        self.had_error = False
        # self.interpreter.namespace.update(namespace)

    def __eq__(self, other) -> bool:
        if isinstance(other, type(self)):
            return self.interpreter == other.interpreter
        return False

    @property
    def namespace(self) -> Dict:
        return self.interpreter.namespace

    # def exec(self, command: str):
    #     pass

    def scan(self, source: str) -> List["Token"]:
        scanner = Scanner(source)
        return scanner.scan_tokens()

    def parse(self, tokens: List["Token"]) -> List["Stmt"]:
        parser = Parser(tokens)
        return parser.parse()

    def interpret(self, stmts: List["Stmt"]):
        return self.interpreter.interpret(stmts)

    def evaluate(self, input: str):
        tokens = self.scan(input)
        stmts = self.parse(tokens)
        return self.interpreter.interpret(stmts)

    def run_input(self, input: str, debug: bool = False, result: bool = False):
        try:
            tokens = self.scan(input)
            if debug:
                rithm_logger.debug(f"TOKENS for {input!r}:")
                rithm_logger.debug(pretty_repr(tokens))
            stmts = self.parse(tokens)

            if debug:
                rithm_logger.debug(f"STATEMENTS for {input!r}")
                rithm_logger.debug(pretty_repr(stmts))

            res = self.interpret(stmts)
            if result:
                return res
        except Exception as e:
            self.error(e)
            raise

    def run_file(self, file: str, debug: bool = False, result: bool = False):
        pass

    def error(self, exception: Exception):
        self.report_error(exception)

    def report_error(self, exception: Exception):
        rithm_logger.error(exception)
        self.had_error = True
