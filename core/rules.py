import os

import regex
from pydantic import BaseModel
from typing import List, Any

from .utils import load_yaml

from .log import logger


class Rule(BaseModel):
    """
    匹配规则
    """
    rule_type: str
    language: str
    patterns: List[str]
    complied: List[Any]


class RuleManager:

    def __init__(self):
        self.rules: List[Rule] = list()

    def load_yaml_rules(self, path: str) -> None:
        logger.info(f"loading rules on path {path}")
        for path, dirs, files in os.walk(path):
            for f in files:
                filename = os.path.join(path, f)
                cfg = load_yaml(filename)
                for r in cfg["rules"]:
                    self.rules.append(
                        Rule(
                            rule_type=r["type"],
                            language=cfg["language"],
                            patterns=r["patterns"],
                            complied=[regex.compile(i) for i in r["patterns"]]
                        )
                    )
                logger.info(f"loaded {filename} for {len(cfg['rules'])} rules.")
