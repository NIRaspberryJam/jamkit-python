from __future__ import annotations

import time
from pathlib import Path
from typing import Any

from .loader import load_workshop
from .models import Asset, Mission, WorkshopConfig

class Robot:
    def __init__(
        self,
        config_path: str | Path | None = None,
        *,
        typing_delay: float = 0.06,
    ) -> None:
        if config_path is None:
            config_path = Path(__file__).with_name("missions.json")

        self.config: WorkshopConfig = load_workshop(config_path)
        self.typing_delay = typing_delay
        self.connected = False
        self.current_mission_index = 0
        self.hint_index_by_mission: dict[str, int] = {}
        self._last_read_asset: str | None = None

    # Output Helpers
    def _line(self, text: str = "") -> None:
        print(text)
        if self.typing_delay > 0:
            time.sleep(self.typing_delay)
    
    def _block(self, lines: list[str]) -> None:
        for line in lines:
            self._line(line)
    
    def _banner(self, title: str) -> None:
        self._line()
        self._line("=" * 50)
        self._line(title)
        self._line("=" * 50)
    
    def _line_with_robot_name(self, msg: str = "") -> None:
        text = f"[{self.config.robot_name}] {msg}"
        self._line(text)
    
    def _block_with_robot_name(self, lines: list[str]) -> None:
        output: list[str] = []
        for line in lines:
            output.append(f"[{self.config.robot_name}] {line}")
        
        self._block(output)

    # Core flow
    def connect(self) -> None:
        self._banner(f"Connecting to {self.config.robot_name}")
        self._block(self.config.connect_lines)
        self.connected = True
        self.show_mission()
    
    def show_mission(self) -> None:
        mission = self.current_mission
        self._banner(f"[{mission.id}] {mission.title}")
        self._block(mission.intro)

        if mission.assets:
            self._line()
            self._line("Available mission assets:")
            for asset_name in mission.assets:
                self._line(f" - {asset_name}")
    
    @property
    def current_mission(self) -> Mission:
        return self.config.missions[self.current_mission_index]
    
    def get_asset(self, name: str) -> Any:
        if name not in self.config.assets:
            raise KeyError(f"Unknown asset: {name}")
        return self.config.assets[name].value
    
    def read_memory(self, asset: Any) -> None:
        matched_name = None
        for name, obj in self.config.assets.items():
            if obj.value is asset:
                matched_name = name
                break
        
        self._line()
        self._line_with_robot_name("Reading memory...")
        if matched_name is not None:
            self._last_read_asset = matched_name
            self._line_with_robot_name(f"Memory label: {matched_name}")
        else:
            self._line_with_robot_name("External object received")
        
        self._line_with_robot_name("Memory read complete.")

    def show(self, value: Any) -> None:
        self._line()
        self._line_with_robot_name("Output:")
        if isinstance(value, list):
            for item in value:
                self._line(str(item))
        else:
            self._line(str(value))
        
        self._line()
        self._line_with_robot_name("If this looks correct, use robot.submit(...)")
    
    def hint(self) -> None:
        mission = self.current_mission
        idx = self.hint_index_by_mission.get(mission.id, 0)

        self._line()
        if idx < len(mission.hints):
            self._line_with_robot_name(f"Hint: {mission.hints[idx]}")
            self.hint_index_by_mission[mission.id] = idx + 1
        else:
            self._line_with_robot_name("No more hits available for this mission.")
    
    def submit(self, answer: Any) -> bool:
        mission = self.current_mission
        expected = mission.expected_answer

        ok = self._answers_match(expected, answer)

        self._line()
        self._line_with_robot_name("Validating submission...")

        time.sleep(1)

        if ok:
            if mission.success_lines:
                self._block_with_robot_name(mission.success_lines)
            else:
                self._line_with_robot_name("Mission complete.")

            self.current_mission_index += 1
            if self.current_mission_index < len(self.config.missions):
                self.show_mission()
            else:
                self._final_reboot()
            
            return True

        if mission.failure_lines:
            self._block_with_robot_name(mission.failure_lines)
        else:
            self._line_with_robot_name("Submission incorrect.")
        
        self._line_with_robot_name("Use robot.hint() if you are stuck.")
        return False

    def _answers_match(self, expected: Any, actual: Any) -> bool:
        if isinstance(expected, str) and isinstance(actual, str):
            return expected.strip().lower() == actual.strip().lower()
        return expected == actual
    
    def _final_reboot(self) -> None:
        old_typing_delay = self.typing_delay
        self._banner("SYSTEM RESTORE")

        self.typing_delay = 1
        self._block(
            [
                "Restoring backup...",
                "Repairing corrupted memory sectors...",
                "Re-enabling safety systems...",
                "Rebooting core services...",
                "",
                "3...",
                "2...",
                "1...",
                "",
                f"{self.config.robot_name} ONLINE",
                "Hello, friend. Thanks for fixing me."
            ]
        )
        self.typing_delay = old_typing_delay