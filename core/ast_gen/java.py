from abc import ABC

from .model import AstImpl


class JavaAst(AstImpl, ABC):

    def __init__(self, code: str):
        super().__init__()
        self.code = code

    def parse(self):
        """
        impl java ast parser method here
        :return:
        """
        pass
