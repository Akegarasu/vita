import gopygo

from abc import ABC

from .model import AstImpl


class GoAst(AstImpl, ABC):

    def __init__(self, code: str):
        super().__init__()
        self.code = code

    def parse(self):
        """
        impl go ast parser method here
        :return:
        """
        pass


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
