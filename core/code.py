import os
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
from .ast_gen.py import PythonAst
from .ast_gen.go import GoAst
from .ast_gen.java import JavaAst

from .log import logger


class CodeFile(BaseModel):
    ext: Optional[str]
    ast: Any
    origin: str
    processed: Optional[str]
    file_path: str
    file_name: str


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
        self.files.append(
            CodeFile(
                ext="123",
                ast=PythonAst(""),
                origin="",
                processed="",
                file_name="",
                file_path="")
        )

    def load_files(self, path: str) -> None:
        """
        加载源码文件
        :return:
        """
        logger.info(f"loading source code in {path}")
        for path, dirs, files in os.walk(path):
            for f in files:
                file_full_path = os.path.join(path, f)
                with open(file_full_path, "r", encoding="utf-8") as fl:
                    self.files.append(CodeFile(
                        origin=fl.read(),
                        file_name=f,
                        file_path=file_full_path,
                    ))
                logger.info(f"loaded file {file_full_path}")

    def file_preprocess(self):
        """
        文件预处理
        :return:
        """
        for f in self.files:
            f.ext = self._classify(f)

            # TODO: file process
            f.processed = f.origin

    def ast_parse(self):
        """
        生成文件 ast 树
        :return:
        """
        for f in self.files:
            if f.ext == "go":
                parser = GoAst
            elif f.ext == "java":
                parser = JavaAst
            elif f.ext == "py":
                parser = PythonAst
            else:
                # do nothing here when file ext is not supported
                continue
            p = parser(f.processed)
            f.ast = p.parse()

    @staticmethod
    def _classify(c: CodeFile) -> str:
        """
        识别文件类型
        :return: file ext
        """
        return c.file_name.split(".")[-1]
