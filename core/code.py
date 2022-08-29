from pydantic import BaseModel
from typing import List
from .ast_gen.model import Ast


class CodeFile(BaseModel):
    ext: str
    ast: Ast
    origin: str
    processed: str


class CodeManager:
    """
    Manager 源码文件加载与管理、预处理器
    """

    def __init__(self):
        self.files: List[CodeFile] = []

    def load_files(self):
        """
        加载源码文件
        :return:
        """
        pass

    def file_preprocess(self):
        """
        文件预处理
        :return:
        """
        pass

    def ast_parse(self):
        """
        生成文件 ast 树
        :return:
        """
        pass

    def _classify(self):
        """
        识别文件类型
        :return:
        """
        pass
