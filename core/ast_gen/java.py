import javalang
from abc import ABC
from typing import Any, List
from core import context
from core.ast_gen.model import AstImpl
from core.context import MatchResult, Context
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
        # print(self.code.split("\n"))

    def get_functions(self) -> List[str]:
        pass

    def parse(self):
        """
        java ast parser
        :return:
        """
        test = JavaAstAnalyze(self.code)
        test.getFunction()
        test.getMethodInvocation()

        self.result = test.result
        self._ast = javalang.parse.parse(self.code)

    def do_match(self, rule: Rule) -> List[MatchResult]:
        pattern = ruletest.rules[2].patterns

        Matchresult = MatchResult
        Matchresult.match_type = "ast"
        Matchresult.language = "java"
        Matchresult.file_path = ""
        Matchresult.severity = ruletest.rules[2].danger

        for i in self.result:
            for position, value in i.items():
                for j in pattern:
                    if j in str(value):
                        Matchresult.match_rule = ruletest.rules[2].description
                        context = Context
                        context.code = []
                        codecontent = self.codeList[i['position'] - 2] + "\n" + self.codeList[
                            i['position'] - 1] + "\n" + self.codeList[i['position'] - 0] + "\n"
                        context.code.append((i['position'], codecontent))
                        Matchresult.context = context
        return Matchresult


if __name__ == "__main__":
    f = open("./javaast/Test.java", "r")
    test = JavaAst(f.read())
    test.parse()
    ruletest = RuleManager()
    ruletest.load_yaml_rules("C:\\Users\\86130\\Desktop\\vita-KKfine\\data\\rules\\test_rule.yml")

    print(test.do_match(ruletest).match_rule)
    print(test.do_match(ruletest).context.code[0][1])
