import core.ast_gen.goast as gopygo

from abc import ABC

from typing import Any
from core.ast_gen.model import AstImpl


class GoAst(AstImpl, ABC):
    _ast: Any

    def __init__(self, code: str):
        super().__init__()
        self.code = code

    def parse(self):
        """
        go ast parser
        :return:
        """
        self._ast = gopygo.parse(self.code)


"""
以下部分为测试代码
"""
if __name__ == "__main__":
    program = """
    package main
    
    import "fmt"
    
    func main() {
        fmt.Println("Hello, World!")
    }
    """
    program = program.lstrip()
    tree = gopygo.parse(program)

    text = gopygo.unparse(tree)
    print(text)
