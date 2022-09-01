# _*_ coding:utf-8 _*_
from typing import Any, Dict, Optional

import yaml
from .log import logger


def load_yaml(file_path: str) -> Optional[Dict]:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            r = yaml.load(f, yaml.FullLoader)
            return r
    except Exception as e:
        logger.error(f"load yaml file {file_path} failed, exception: {repr(e)}")

    return None
