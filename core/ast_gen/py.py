import ast
import re
from abc import ABC
from typing import Any, List
from core.ast_gen.model import AstImpl
from core.context import MatchResult, Context, Severity, gen_context
from core.model import CodeFile
from core.rules import Rule

newline = re.compile(r'\n')

def get_attribute(f: ast.Attribute):
    if isinstance(f.value, ast.Name):
        return get_name(f.value) + '.' + f.attr
    elif isinstance(f.value, ast.Attribute):
        return get_attribute(f.value) + '.' + f.attr
    elif isinstance(f.value, ast.Call):
        return get_call(f.value) + '.' + f.attr
    else:
        return f.attr


def get_name(f: ast.Name):
    return f.id


def get_call(f: ast.Call):
    if isinstance(f.func, ast.Name):
        return get_name(f.func) + '()'
    elif isinstance(f.func, ast.Attribute):
        return get_attribute(f.func) + '()'


class PythonAst(AstImpl, ABC):
    _ast: Any

    def __init__(self, code: CodeFile):
        super().__init__()
        self.code = code

    def parse(self):
        self._ast = ast.parse(self.code.processed)
        return self

    def get_functions(self) -> List[dict]:
        program = self.code.processed.lstrip()
        tree = ast.parse(program)

        func_list = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                # astpretty.pprint(node.func)
                info = {'lineno': node.func.lineno, 'func': get_call(node)}
                func_list.append(info)
                # print(info)
        return func_list

    def do_match(self, rule: Rule) -> List[MatchResult]:
        func_list = self.get_functions()
        result: List[MatchResult] = []
        # print(func_list)
        for f in func_list:
            for r in rule.complied:
                for m in r.finditer(f['func']):
                    # print(m)
                    ctx = gen_context(self.code.processed)
                    ctx.start_line = f['lineno']
                    ctx.end_line = f['lineno']+1
                    result.append(
                        MatchResult(
                            context=ctx,
                            match_type="ast",
                            match_rule=r.pattern,
                            description=rule.description,
                            file_path=self.code.file_path,
                            severity=Severity.calculate(rule.danger),
                            language='Python',
                            ptype=rule.ptype,
                            confidence=rule.confidence
                        )
                    )
        return result
