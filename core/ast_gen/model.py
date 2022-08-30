from abc import ABC, abstractmethod

from typing import List
from core.context import MatchResult
from core.rules import Rule


class AstImpl(ABC):
    """
    code ast impl
    """

    def __init__(self):
        super().__init__()

    @abstractmethod
    def parse(self):
        ...

    @abstractmethod
    def get_functions(self) -> List[str]:
        """
        待定
        :return:
        """
        ...

    @abstractmethod
    def do_match(self, rule: Rule) -> List[MatchResult]:
        ...
