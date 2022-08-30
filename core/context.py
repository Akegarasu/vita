from enum import Enum
from pydantic import BaseModel
from typing import Tuple, List

CodeLine = Tuple[int, str]


class Context(BaseModel):
    """
    match context here.
    """
    code: List[CodeLine]


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
        if danger < 3:
            return cls.prompt


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
