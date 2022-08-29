import javalang
from abc import ABC

from .model import AstImpl


class JavaAst(AstImpl, ABC):

    def __init__(self, code: str):
        super().__init__()
        self.code = code

    def parse(self):
        """
        java ast parser
        :return:
        """
        return javalang.parse.parse(self.code)
