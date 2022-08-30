from .rules import Rule, RuleManager
from .code import CodeFile, CodeManager
from .context import MatchResult, Context, Severity
from typing import List
from .log import logger

import os


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

        self._match()

    def _match(self):
        for c in self.manager.files:
            logger.info(f"scanning file {c.file_name}")
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

    @staticmethod
    def __match_regex(code: CodeFile, rule: Rule) -> List[MatchResult]:
        result: List[MatchResult] = []

        for r in rule.complied:
            if r.match(code.processed) != 0:
                result.append(
                    MatchResult(
                        context=Context(code=[(0, "占位符")]),
                        match_type="regex",
                        match_rule=r.pattern,
                        description=rule.description,
                        file_path=os.path.join(code.file_path, code.file_name),
                        severity=Severity.calculate(rule.danger),
                        language=rule.language
                    )
                )

            return result
