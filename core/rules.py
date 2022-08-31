import os

from pydantic import BaseModel
from typing import List, Any, Pattern

from .utils import load_yaml

from .log import logger


class Rule(BaseModel):
    """
    匹配规则
    """
    rule_type: str
    language: str
    patterns: List[str]
    description: str
    danger: int
    complied: List[Pattern]


class RuleManager:

    def __init__(self):
        self.rules: List[Rule] = list()

    def load_yaml_rules(self, path: str) -> None:
        logger.info(f"loading rules on path {path}")
        if os.path.isfile(path):
            self._load(path)
        else:
            for path, dirs, files in os.walk(path):
                print(files)
                for f in files:
                    print(f)
                    self._load(os.path.join(path, f))

    def _load(self, path: str) -> None:
        cfg = load_yaml(path)
        print(cfg)
        for r in cfg["rules"]:
            self.rules.append(
                Rule(
                    rule_type=r["type"],
                    language=cfg["language"],
                    description=r["description"],
                    danger=r["danger"],
                    patterns=r["patterns"],
                    complied=r["patterns"],
                )
            )
        logger.info(f"loaded {path} for {len(cfg['rules'])} rules.")
