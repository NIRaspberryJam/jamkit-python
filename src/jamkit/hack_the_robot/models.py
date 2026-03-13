from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

@dataclass
class Asset:
    name: str
    kind: str
    value: Any

@dataclass
class Mission:
    id: str
    title: str
    intro: list[str] = field(default_factory=list)
    hints: list[str] = field(default_factory=list)
    expected_answer: any = None
    success_lines: list[str] = field(default_factory=list)
    failure_lines: list[str] = field(default_factory=list)
    assets: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

@dataclass
class WorkshopConfig:
    workshop_id: str
    robot_name: str
    connect_lines: list[str]
    missions: list[Mission]
    assets: dict[str, Asset]