import re

from .rules import Rule, RuleManager
from .code import CodeFile, CodeManager
from .context import MatchResult, Context, Severity, gen_context
from typing import List
from .log import logger
import json

import os

newline = re.compile(r'\n')


class Vita:

    def __init__(self,
                 rule_path: str,
                 output_path: str) -> None:
        self.rule: RuleManager = RuleManager()
        self.manager: CodeManager = CodeManager()
        self.results: List[MatchResult] = []
        self.output_path: str = output_path

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
        self.manager.ast_parse()

        self._match()
        self.output()
        # breakpoint()

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
                        file_path=cf.file_path,
                        severity=Severity.calculate(rule.danger),
                        language=rule.language,
                        ptype=rule.ptype,
                        confidence=rule.confidence
                    )
                )
        return result

    def output(self):
        out = {'problems': []}
        severity_count = [0, 0, 0, 0, 0, 0]
        for r in self.results:
            r.context.printable = r.context.gen_context_output(4)
            tmp = r.dict()
            tmp['severity'] = r.severity.name
            severity_count[r.severity.value % 5] += 1
            severity_count[5] += 1
            tmp['context'] = r.context.printable
            tmp['ptype'] = r.ptype
            tmp['confidence'] = r.confidence
            out['problems'].append(tmp)

            ok = f''' [输出报告]\n等级: {r.severity}\n文件: {r.file_path}\n漏洞: {r.description}\n规则: {r.match_rule}\n{r.context.printable}'''
            logger.info(ok)

        out['basic'] = {
            'totleNum': severity_count[5],
            "criticalLevel": severity_count[4],
            'highLevel': severity_count[3],
            'mediumLevel': severity_count[2],
            'lowLevel': severity_count[1],
            'prompt': severity_count[0]
        }

        real_result = json.dumps(out, ensure_ascii=False)
        with open(__file__+"/../../"+self.output_path + "/data.js", "w", encoding="utf-8") as f:
            f.write(f"var datas = {real_result}")

        logger.info(f"gen output report in file {self.output_path}/VitaReport.html")
