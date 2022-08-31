import ast
from abc import ABC

from typing import Any, List
from core.ast_gen.model import AstImpl
from core.context import MatchResult, Context, Severity
from core.rules import Rule


def getAttribute(f: ast.Attribute):
    if isinstance(f.value, ast.Name):
        return getName(f.value) + '.' + f.attr
    elif isinstance(f.value, ast.Attribute):
        return getAttribute(f.value) + '.' + f.attr
    elif isinstance(f.value, ast.Call):
        return getCall(f.value) + '.' + f.attr
    else:
        return f.attr


def getName(f: ast.Name):
    return f.id


def getCall(f: ast.Call):
    if isinstance(f.func, ast.Name):
        return getName(f.func) + '()'
    elif isinstance(f.func, ast.Attribute):
        return getAttribute(f.func) + '()'


class PythonAst(AstImpl, ABC):
    _ast: Any

    def __init__(self, code: str):
        super().__init__()
        self.code = code

    def parse(self):
        print(type(self.code))
        print(self.code)
        self._ast = ast.parse(self.code)
        return self

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

    def do_match(self, rule: Rule) -> List[MatchResult]:
        funcList = self.get_functions()
        result: List[MatchResult] = []
        for f in funcList:
            for r in rule.complied:
                if r.match(f['func']) != 0:
                    result.append(
                        MatchResult(
                            context=Context(code=[(0, "占位符")]),
                            match_type="ast",
                            match_rule=r.pattern,
                            description=rule.description,
                            file_path='',
                            severity=Severity.calculate(rule.danger),
                            language=rule.language
                        )
                    )
        return result


if __name__ == "__main__":
    code = open('../rules.py', 'r').read()
    aaaast = PythonAst(code)
    print(aaaast.get_functions())
    print(aaaast.do_match())
    print('yes')
