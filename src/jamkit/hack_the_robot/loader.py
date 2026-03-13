from __future__ import annotations

import json
from pathlib import Path

from .assets import load_asset_value
from .models import Asset, Mission, WorkshopConfig

def load_workshop(config_path: str | Path) -> WorkshopConfig:
    config_path = Path(config_path).resolve()
    base_dir = config_path.parent

    raw = json.loads(config_path.read_text(encoding="utf-8"))
    
    assets: dict[str, Asset] = {}
    for name, asset_def in raw.get("assets", {}).items():
        assets[name] = Asset(
            name=name,
            kind=asset_def["type"],
            value=load_asset_value(base_dir, asset_def)
        )
    
    missions = [
        Mission(
            id=m["id"],
            title=m["title"],
            intro=m.get("intro", []),
            hints=m.get("hints", []),
            expected_answer=m.get("expected_answer"),
            success_lines=m.get("success_lines", []),
            failure_lines=m.get("failure_lines", []),
            assets=m.get("assets", []),
            metadata=m.get("metadata", {}),
        )
        for m in raw.get("missions", [])
    ]

    return WorkshopConfig(
        workshop_id=raw["workshop_id"],
        robot_name=raw.get("robot_name", "JAMBOT-7"),
        connect_lines=raw.get("connect_lines", []),
        missions=missions,
        assets=assets
    )
