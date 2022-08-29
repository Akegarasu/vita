from abc import ABC, abstractmethod

from typing import List


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
        ...
