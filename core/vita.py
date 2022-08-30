import re

from .rules import Rule, RuleManager
from .code import CodeFile, CodeManager
from .context import MatchResult, Context, Severity, gen_context
from typing import List
from .log import logger

import os

newline = re.compile(r'\n')


class Vita:

    def __init__(self,
                 rule_path: str) -> None:
        self.rule: RuleManager = RuleManager()
        self.manager: CodeManager = CodeManager()
        self.results: List[MatchResult] = []

        self.rule.load_yaml_rules(path=rule_path)

    def run(self,
            file_path: str,
            ignore: str) -> None:
        """
        程序入口。
        """
        self.manager.load_files(
            path=file_path,
            ignore=ignore
        )
        self.manager.file_preprocess()
        # self.manager.ast_parse()

        self._match()
        self.output()
        breakpoint()

    def _match(self):
        for c in self.manager.files:
            logger.info(f"scanning file {c.file_name}")
            for r in self.rule.rules:
                if r.language != c.ext:
                    continue
                if r.rule_type == "ast":
                    self.results.extend(
                        self.__match_ast(cf=c, rule=r)
                    )
                elif r.rule_type == "regex":
                    self.results.extend(
                        self.__match_regex(cf=c, rule=r)
                    )

    @staticmethod
    def __match_ast(cf: CodeFile, rule: Rule) -> List[MatchResult]:
        return cf.ast.do_match(rule)

    @staticmethod
    def __match_regex(cf: CodeFile, rule: Rule) -> List[MatchResult]:
        result: List[MatchResult] = []
        for r in rule.complied:
            for m in r.finditer(cf.processed):
                ctx = gen_context(cf.processed)
                ctx.start_line = len(newline.findall(cf.processed, 0, m.start())) + 1
                ctx.end_line = len(newline.findall(cf.processed, 0, m.end())) + 1
                result.append(
                    MatchResult(
                        context=ctx,
                        match_type="regex",
                        match_rule=r.pattern,
                        description=rule.description,
                        file_path=os.path.join(cf.file_path, cf.file_name),
                        severity=Severity.calculate(rule.danger),
                        language=rule.language
                    )
                )
        return result

    def output(self):
        for r in self.results:
            ok = f''' [输出报告]\n等级: {r.severity}\n文件: {r.file_path}\n漏洞: {r.description}\n规则: {r.match_rule}\n'''
            ctx_codes = r.context.get_context_codes(4)
            for cc in ctx_codes:
                ok += f"{'--> ' + str(cc[0]) if cc[0] == r.context.start_line else '    ' + str(cc[0])}   {cc[1]}\n"
            ok = ok[:-1]
            logger.info(ok)
