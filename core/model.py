from pydantic import BaseModel
from typing import List, Optional, Any


class CodeFile(BaseModel):
    ext: Optional[str]
    ast: Any
    origin: str
    processed: Optional[str]
    file_path: str
    file_name: str
