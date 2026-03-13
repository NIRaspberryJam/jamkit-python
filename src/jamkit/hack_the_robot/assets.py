from __future__ import annotations

from pathlib import Path
from typing import Any

def load_asset_value(base_dir: Path, asset_def: dict[str, Any]) -> Any:
    asset_type = asset_def["type"]

    if asset_type == "string":
        return asset_def["value"]
    
    if asset_type == "text_file":
        rel_path = asset_def["path"]
        file_path = (base_dir / rel_path).resolve()
        return file_path.read_text(encoding="utf-8")
    
    if asset_type == "lines_file":
        rel_path = asset_def["path"]
        file_path = (base_dir / rel_path).resolve()
        return file_path.read_text(encoding="utf-8").splitlines()
    
    if asset_type == "list":
        return asset_def["value"]
    
    if asset_type == "dict":
        return asset_def["value"]
    
    raise ValueError(f"Unsupported asset type: {asset_type}")