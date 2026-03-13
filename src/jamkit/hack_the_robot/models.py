from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterator

@dataclass
class Asset:
    name: str
    kind: str
    value: Any
    label: str | None = None
    address: str | None = None
    description: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    export: bool = True

    @property
    def display_label(self) -> str:
        return self.label or self.name

    def __repr__(self) -> str:
        return (
            f"Asset(name={self.name!r}, kind={self.kind!r}, "
            f"address={self.address!r}, value={self.value!r})"
        )

    def __str__(self) -> str:
        return str(self.address)

    def __iter__(self) -> Iterator[Any]:
        return iter(self.value)

    def __len__(self) -> int:
        return len(self.value)

    def __getitem__(self, key: Any) -> Any:
        return self.value[key]

    def __contains__(self, item: Any) -> bool:
        return item in self.value

    def __getattr__(self, attr: str) -> Any:
        # Delegate unknown attributes to underlying value
        return getattr(self.value, attr)

@dataclass
class Mission:
    id: str
    title: str
    intro: list[str] = field(default_factory=list)
    hints: list[str] = field(default_factory=list)
    expected_answer: any = None
    validator_name: str | None = None
    validator_params: dict[str, Any] = field(default_factory=dict)
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