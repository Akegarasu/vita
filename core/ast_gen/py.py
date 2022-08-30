import ast
from abc import ABC
import astpretty
from typing import Any,List
from core.ast_gen.model import AstImpl
from core.context import MatchResult


class PythonAst(AstImpl, ABC):
    _ast: Any

    def __init__(self, code: str):
        super().__init__()
        self.code = code

    def parse(self):
        self._ast = ast.parse(self.code)

    def get_functions(self) -> List[str]:
        pass
    def do_match(self) -> List[MatchResult]:
        pass

if __name__ == "__main__":
    program = """import os\na=input()\nos.system(a)\nprint('hello f0')
    """
    program = program.lstrip()
    tree = ast.parse(program)
    print(ast.dump(tree))