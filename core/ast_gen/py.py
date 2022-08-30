import ast
from abc import ABC

from typing import Any
from core.ast_gen.model import AstImpl


class PythonAst(AstImpl, ABC):
    _ast: Any

    def __init__(self, code: str):
        super().__init__()
        self.code = code

    def parse(self):
        self._ast = ast.parse(self.code)
