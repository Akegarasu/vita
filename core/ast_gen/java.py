import javalang
from abc import ABC
from typing import Any
from core.ast_gen.model import AstImpl


class JavaAst(AstImpl, ABC):
    _ast: Any

    def __init__(self, code: str):
        super().__init__()
        self.code = code

    def parse(self):
        """
        java ast parser
        :return:
        """
        self._ast = javalang.parse.parse(self.code)
