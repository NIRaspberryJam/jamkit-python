from __future__ import annotations

from pathlib import Path

from .engine import Robot
from .loader import load_workshop

_config_path = Path(__file__).with_name("missions.json")
_workshop = load_workshop(_config_path)

# Export all assets as module level variables
for _asset_name, _asset in _workshop.assets.items():
    globals()[_asset_name] = _asset.value

__all__ = ["Robot", *_workshop.assets.keys()]