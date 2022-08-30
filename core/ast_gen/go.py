import re

import core.ast_gen.goast as gopygo

from abc import ABC

from typing import Any, List
from core.ast_gen.model import AstImpl

from core.context import MatchResult, Severity, gen_context
from core.model import CodeFile
from core.rules import Rule, RuleManager

newline = re.compile(r'\n')

class GoAst(AstImpl, ABC):
    _ast: Any

    def __init__(self, codeFile: CodeFile):
        super().__init__()
        self.code = codeFile.processed
        self.oriCode = codeFile.processed
        self.result = []
        self.filePath = codeFile.file_path

    def parse(self):
        """
        go ast parser
        :return:
        """
        self._goast = gopygo.parse(self)

    def get_functions(self) -> List[str]:
        pass

    def reMatch(self,reObj):
        if type(reObj)==dict:
            for i in reObj:
                if type(reObj[i]) == str:
                    self.relMatch(reObj[i])
                else:
                    self.reMatch(reObj[i])
        elif type(reObj)==list:
            for i in reObj:
                if type(i) == str:
                    self.relMatch(i)
                else:
                    self.reMatch(i)

    def relMatch(self,s: str):
        for r in self.rule.complied:
            for m in r.finditer(s):
                ctx = gen_context(self.oriCode)
                start = 0
                end = 0
                for i in r.finditer(self.oriCode):
                    start = i.start()
                    end = i.end()
                ctx.start_line = len(newline.findall(self.oriCode, 0, start)) + 1
                ctx.end_line = len(newline.findall(self.oriCode, 0, end)) + 1
                self.result.append(MatchResult(
                    context=ctx,
                    match_rule=r.pattern,
                    description=self.rule.description,
                    match_type="ast",
                    severity=Severity.calculate(self.rule.danger),
                    file_path=self.filePath,
                    language="go"
                ))

    def do_match(self, rule: Rule) -> List[MatchResult]:
        self.rule = rule
        self.reMatch(self._ast)
        return self.result


"""
以下部分为测试代码
"""
if __name__ == "__main__":
    pass
    # # goast =
    # tc = open("../../gotest/test.go","r",encoding="utf-8").read()
    #
    # goast = GoAst(CodeFile(
    #     ext="go",
    #
    #     origin: str
    #     processed: Optional[str]
    #     file_path: str
    #     file_name: str
    # ))
    # goast.parse()
    # ruletest = RuleManager()
    # ruletest.load_yaml_rules("../../data/rules/test_rule.yml")
    # goast.do_match(ruletest)
