import ast
from abc import ABC
import astpretty
from typing import Any,List
from core.ast_gen.model import AstImpl
from core.context import MatchResult
from core.rules import Rule


def getAttribute(f:ast.Attribute):
    if isinstance(f.value,ast.Name):
        return getName(f.value)+'.'+f.attr
    elif isinstance(f.value,ast.Attribute):
        return getAttribute(f.value)+'.'+f.attr
    elif isinstance(f.value,ast.Call):
        return getCall(f.value)+'.'+f.attr
    else:
        return f.attr

def getName(f:ast.Name):
    return f.id

def getCall(f:ast.Call):
    if isinstance(f.func,ast.Name):
        return getName(f.func)+'()'
    elif isinstance(f.func,ast.Attribute):
        return getAttribute(f.func)+'()'

class PythonAst(AstImpl, ABC):
    _ast: Any

    def __init__(self, code: str):
        super().__init__()
        self.code = code

    def parse(self):
        self._ast = ast.parse(self.code)
        return self._ast

    def get_functions(self) -> List[dict]:
        program = self.code.lstrip()
        tree = ast.parse(program)

        funcList = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                # astpretty.pprint(node.func)
                info = {}
                info['lineno'] = node.func.lineno
                info['func'] = getCall(node)
                funcList.append(info)
                # print(info)
        return funcList

    def do_match(self,rule: Rule) -> List[MatchResult]:
        funcList=self.get_functions()
        result: List[MatchResult] = []
        for r in rule.complied:
            print(r)
        return result

if __name__ == "__main__":
    code=open('../rules.py','r').read()
    aaaast=PythonAst(code)
    print(aaaast.get_functions())
    print('yes')