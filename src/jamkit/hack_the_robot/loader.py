from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .assets import load_asset_value
from .models import Asset, Mission, WorkshopConfig

def _parse_validator(raw_validator: Any) -> tuple[str | None, dict[str, Any]]:
    if raw_validator is None:
        return None, {}
    
    if isinstance(raw_validator, str):
        return raw_validator, {}
    
    if isinstance(raw_validator, dict):
        return raw_validator.get("name"), raw_validator.get("params", {})
    
    raise ValueError(f"Invalid validator config: {raw_validator}")

def load_workshop(config_path: str | Path) -> WorkshopConfig:
    config_path = Path(config_path).resolve()
    base_dir = config_path.parent

    raw = json.loads(config_path.read_text(encoding="utf-8"))
    
    assets: dict[str, Asset] = {}
    for name, asset_def in raw.get("assets", {}).items():
        assets[name] = Asset(
            name=name,
            kind=asset_def["type"],
            value=load_asset_value(base_dir, asset_def),
            label=asset_def.get("label"),
            address=asset_def.get("address"),
            description=asset_def.get("description"),
            metadata=asset_def.get("metadata", {}),
            export=asset_def.get("export", True),
        )
    
    missions: list[Mission] = []
    for m in raw.get("missions", []):
        validator_name, validator_params = _parse_validator(m.get("validator"))
        missions.append(
            Mission(
                id=m["id"],
                title=m["title"],
                intro=m.get("intro", []),
                hints=m.get("hints", []),
                expected_answer=m.get("expected_answer"),
                validator_name=validator_name,
                validator_params=validator_params,
                success_lines=m.get("success_lines", []),
                failure_lines=m.get("failure_lines", []),
                assets=m.get("assets", []),
                metadata=m.get("metadata", {}),
            )
        )


    return WorkshopConfig(
        workshop_id=raw["workshop_id"],
        robot_name=raw.get("robot_name", "JAMBOT-7"),
        connect_lines=raw.get("connect_lines", []),
        missions=missions,
        assets=assets
    )
