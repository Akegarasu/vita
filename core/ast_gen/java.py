import javalang
from abc import ABC
from typing import Any, List
from core import context
from core.ast_gen.model import AstImpl
from core.context import MatchResult, Context, gen_context, Severity
from core.rules import Rule, RuleManager


class JavaAstAnalyze:
    def __init__(self, code):
        self.code = code
        self.tree = javalang.parse.parse(self.code)
        self.result = []

    def getMethodInvocation(self):
        info = {}
        for path, node in self.tree.filter(javalang.tree.MethodInvocation):
            if 'qualifier' in dir(node):
                info["position"] = node.position.line
                info["MethodInvocation"] = str(node.qualifier) + "." + str(node.member)
                # print(str(node.qualifier)+ "." + str(node.member) + " and position : " + str(node.position.line))
                # print(node.position.line)
                self.result.append(info)
                info = {}

    def getFunction(self):
        info = {}
        for path, node in self.tree.filter(javalang.tree.ClassDeclaration):
            if 'name' in dir(node) and node.position:
                info["position"] = node.position.line
                info["functionName"] = str(node.name)
                self.result.append(info)
                info = {}
                # print(node.name, end=" ")
                # print(node.position)

    def do_match(self):
        pass


class JavaAst(AstImpl, ABC):
    _ast: Any

    def __init__(self, code: str):
        super().__init__()
        self.code = code
        self.codeList = self.code.split("\n")
        self.result = None

    def get_functions(self) -> List[str]:
        pass

    def parse(self):
        """
        java ast parser
        :return:
        """
        j = JavaAstAnalyze(self.code)
        j.getFunction()
        j.getMethodInvocation()

        self.result = j.result
        self._ast = javalang.parse.parse(self.code)

    def do_match(self, rule: Rule) -> List[MatchResult]:
        pattern = ruletest.rules[2].patterns
        result = []
        for i in self.result:
            for position, value in i.items():
                for j in pattern:
                    if j in str(value):
                        ctx = gen_context(self.code)
                        ctx.start_line = i['position']
                        ctx.end_line = i['position'] + 1
                        result.append(
                            MatchResult(
                                context=ctx,
                                match_rule=rule.description,
                                description=rule.description,
                                match_type="ast",
                                severity=Severity.calculate(rule.danger),
                                file_path="",
                                language="java"
                            )
                        )
        return result


if __name__ == "__main__":
    f = open("./javaast/Test.java", "r")
    test = JavaAst(f.read())
    test.parse()
    ruletest = RuleManager()
    ruletest.load_yaml_rules("C:\\Users\\86130\\Desktop\\vita-KKfine\\data\\rules\\test_rule.yml")

    print(test.do_match(ruletest).match_rule)
    print(test.do_match(ruletest).context.code[0][1])
