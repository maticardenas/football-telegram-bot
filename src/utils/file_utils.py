import json
import os
from pathlib import Path
from typing import Any, Dict


def read_json_file(json_file_path: Path) -> Dict[str, Any]:
    with open(json_file_path, mode="r") as f:
        return json.load(f)
