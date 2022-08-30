import ast
from abc import ABC

from core.ast_gen.model import AstImpl


class PythonAst(AstImpl, ABC):

    def __init__(self, code: str):
        super().__init__()
        self.code = code

    def parse(self):
        return ast.parse(self.code)
