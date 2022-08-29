from .rules import RuleManager
from .code import CodeManager


class Vita:

    def __init__(self, rule_path: str):
        self.rule: RuleManager = RuleManager()
        self.manager: CodeManager = CodeManager()

        self.rule.load_yaml_rules(path=rule_path)

    def run(self, file_path: str) -> None:
        """
        程序入口。
        """
        self.manager.load_files(path=file_path)
        self.manager.file_preprocess()
        self.manager.ast_parse()

