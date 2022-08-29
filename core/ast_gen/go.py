import goast as gopygo

from abc import ABC

from .model import AstImpl


class GoAst(AstImpl, ABC):

    def __init__(self, code: str):
        super().__init__()
        self.code = code

    def parse(self):
        """
        go ast parser
        :return:
        """
        return gopygo.parse(self.code)


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
