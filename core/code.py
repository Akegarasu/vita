import os
from pydantic import BaseModel
from typing import List, Optional, Any
from .ast_gen.py import PythonAst
from .ast_gen.go import GoAst
from .ast_gen.java import JavaAst

from .log import logger
from .model import CodeFile


class CodeManager:
    """
    Manager 源码文件加载与管理、预处理器
    """

    def __init__(self):
        self.files: List[CodeFile] = []

    def load_files(self, path: str, ignore: str) -> None:
        """
        加载源码文件
        :return:
        """
        ignore_exts = ignore.split(",")
        if os.path.isfile(path):
            self._load(path)

        for path, dirs, files in os.walk(path):
            for f in files:
                if len(ignore) > 0:
                    if self._check_ignore(f, ignore_exts):
                        continue
                file_full_path = os.path.join(path, f)
                self._load(file_full_path)

    def _load(self, full_path: str):
        with open(full_path, "r", encoding="utf-8", errors="ignore") as fl:
            self.files.append(CodeFile(
                origin=fl.read(),
                file_name=os.path.basename(full_path),
                file_path=full_path,
            ))
        logger.info(f"loaded file {full_path}")

    def file_preprocess(self):
        """
        文件预处理
        :return:
        """
        for f in self.files:
            f.ext = self._classify(f)

            # TODO: file process
            f.processed = f.origin.replace("\r\n", "\n")

    def ast_parse(self):
        """
        生成文件 ast 树
        :return:
        """
        for code_file in self.files:
            if code_file.ext == "go":
                parser = GoAst
            elif code_file.ext == "java":
                parser = JavaAst
            elif code_file.ext == "py":
                parser = PythonAst
            else:
                # do nothing here when file ext is not supported
                continue
            code_file.ast = parser(code_file)
            code_file.ast.parse()

    @staticmethod
    def _classify(c: CodeFile) -> str:
        """
        识别文件类型
        :return: file ext
        """
        return c.file_name.split(".")[-1]

    @staticmethod
    def _check_ignore(file_name: str, ignore_exts: List[str]) -> bool:
        """
        检测文件类型是否忽略，True文件在忽略类型内，表示应忽略该文件
        :param file_name: 文件名
        :param ignore_exts: 忽略的文件类型
        :return: 是否忽略该文件
        """
        file_ext = file_name.split(".")[-1]
        if file_ext in ignore_exts:
            return True
        return False
