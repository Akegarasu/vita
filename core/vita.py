from .rules import RuleManager
from .rules import Rule
from .code import CodeManager
from .code import CodeFile
from .context import MatchResult
from typing import List


class Vita:

    def __init__(self, rule_path: str):
        self.rule: RuleManager = RuleManager()
        self.manager: CodeManager = CodeManager()
        self.results: List[MatchResult] = []

        self.rule.load_yaml_rules(path=rule_path)

    def run(self, file_path: str) -> None:
        """
        程序入口。
        """
        self.manager.load_files(path=file_path)
        self.manager.file_preprocess()
        self.manager.ast_parse()
        breakpoint()

    def _match(self):
        for c in self.manager.files:
            for r in self.rule.rules:
                if r.rule_type == "ast":
                    self.results.extend(
                        self.__match_ast(code=c, rule=r)
                    )
                elif r.rule_type == "regex":
                    self.results.extend(
                        self.__match_regex(code=c, rule=r)
                    )

    @staticmethod
    def __match_ast(code: CodeFile, rule: Rule) -> List[MatchResult]:
        return code.ast.do_match(rule)

    def __match_regex(self, code: CodeFile, rule: Rule) -> List[MatchResult]:
        ...
