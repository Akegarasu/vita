from pydantic import BaseModel
from typing import List
from .ast_gen.model import AstImpl
from .ast_gen.py import PythonAst


class CodeFile(BaseModel):
    ext: str
    ast: AstImpl
    origin: str
    processed: str


class CodeManager:
    """
    Manager 源码文件加载与管理、预处理器
    """

    def __init__(self):
        self.files: List[CodeFile] = []

    def __test_for_ast_type_impl(self):
        """
        类型测试用
        :return:
        """
        self.files.append(CodeFile(ext="123", ast=PythonAst(""), origin="", processed=""))

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
