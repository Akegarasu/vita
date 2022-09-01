from enum import Enum
from pydantic import BaseModel
from typing import Tuple, List, Optional

CodeLine = Tuple[int, str]


class Context(BaseModel):
    """
    match context here.
    """
    code: List[CodeLine]
    printable: Optional[str]
    start_line: Optional[int]
    end_line: Optional[int]

    def get_context_codes(self, rels: int):
        s = 0 if self.start_line - rels < 0 else self.start_line - rels
        e = len(self.code) if self.end_line + rels > len(self.code) else self.end_line + rels
        return self.code[s:e]

    def gen_context_output(self, rels: int) -> str:
        ok = ""
        ctx_codes = self.get_context_codes(rels=rels)
        for cc in ctx_codes:
            ok += f"{'--> ' + str(cc[0]) if cc[0] == self.start_line else '    ' + str(cc[0])}   {cc[1]}\n"
        ok = ok[:-1]
        return ok


class Severity(Enum):
    """严重度
    提醒-低-中-高-严重
    """
    prompt = 0
    low = 1
    medium = 2
    high = 3
    critical = 4

    @classmethod
    def calculate(cls, danger: int):
        if danger <= 2:
            return cls.prompt
        elif 2 < danger <= 4:
            return cls.low
        elif 4 < danger <= 6:
            return cls.low
        elif 6 < danger <= 8:
            return cls.low
        elif 8 < danger <= 10:
            return cls.critical


class MatchResult(BaseModel):
    context: Context
    """匹配上下文"""

    match_type: str
    """匹配的规则类型 regex/ast/self_defined"""
    match_rule: str
    """具体匹配的规则 正则/文字描述"""
    description: str
    """漏洞描述"""
    file_path: str
    """代码文件目录"""
    language: str
    """代码语言"""
    severity: Severity
    """严重程度"""
    ptype: str
    """漏洞类型"""
    confidence: float
    """置信度"""


def gen_context(c: str):
    return Context(
        code=[(i + 1, j) for i, j in enumerate(c.split("\n"))]
    )
