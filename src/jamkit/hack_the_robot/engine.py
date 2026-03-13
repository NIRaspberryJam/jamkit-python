from __future__ import annotations

import time
import json

from pathlib import Path
from typing import Any

from .loader import load_workshop
from .models import Asset, Mission, WorkshopConfig
from .validators import validate_submission

class Robot:
    def __init__(
        self,
        config_path: str | Path | None = None,
        *,
        typing_delay: float = 0.04,
        validation_delay: float = 0.5,
    ) -> None:
        if config_path is None:
            config_path = Path(__file__).with_name("missions.json")

        self.config: WorkshopConfig = load_workshop(config_path)
        self.typing_delay = typing_delay
        self.validation_delay = validation_delay
        self.connected = False
        self.current_mission_index = 0
        self.hint_index_by_mission: dict[str, int] = {}
        self._last_read_asset_name: str | None = None
        self._read_asset_names: set[str] = set()
        self._pin_attempt_count = 0

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
        self._block([f"[{self.config.robot_name}] {line}" for line in lines])

    def _resolve_asset(self, asset_ref: Any) -> Asset | None:
        if isinstance(asset_ref, Asset):
            return self.config.assets.get(asset_ref.name, asset_ref)

        if isinstance(asset_ref, str) and asset_ref in self.config.assets:
            return self.config.assets[asset_ref]

        for asset in self.config.assets.values():
            if asset_ref is asset or asset_ref is asset.value:
                return asset

        return None
    
    @property
    def finished(self) -> bool:
        return self.current_mission_index >= len(self.config.missions)

    # Core flow
    def connect(self) -> None:
        self._banner(f"Connecting to {self.config.robot_name}")
        self._block(self.config.connect_lines)
        self.connected = True
        if self.config.missions:
            self.show_mission()
        else:
            self._line_with_robot_name("No missions loaded.")
    
    def show_mission(self) -> None:
        if self.finished:
            self._line_with_robot_name("All missions already complete.")
            return

        mission = self.current_mission
        self._banner(f"[{mission.id}] {mission.title}")
        self._block(mission.intro)

        if mission.assets:
            self._line()
            self._line("Available mission assets:")
            for asset_name in mission.assets:
                asset = self.config.assets.get(asset_name)
                if asset is None:
                    self._line(f" - {asset_name}")
                    continue

                address = f" @ {asset.address}" if asset.address else ""
                self._line(f" - {asset.display_label} ({asset.name}){address}")
    
    @property
    def current_mission(self) -> Mission:
        if self.finished:
            raise RuntimeError("No active mission. Workshop is complete.")
        return self.config.missions[self.current_mission_index]
    
    def get_asset(self, name: str) -> Any:
        if name not in self.config.assets:
            raise KeyError(f"Unknown asset: {name}")
        return self.config.assets[name].value
    
    def get_asset_wrapper(self, name: str) -> Asset:
        if name not in self.config.assets:
            raise KeyError(f"Unknown asset: {name}")
        return self.config.assets[name]
    
    def read_memory(self, asset: Any) -> Any:
        resolved = self._resolve_asset(asset)

        self._line()
        self._line_with_robot_name("Reading memory...")

        if resolved is not None:
            self._last_read_asset_name = resolved.name
            self._read_asset_names.add(resolved.name)
            self._line_with_robot_name(f"Label: {resolved.display_label}")
            self._line_with_robot_name(f"Address: {resolved.address or 'UNMAPPED'}")
            self._line_with_robot_name(f"Type: {resolved.kind}")
            if resolved.description:
                self._line_with_robot_name(f"Note: {resolved.description}")
            self._line_with_robot_name("Memory read complete.")
            return resolved.value

        if isinstance(asset, str):
            self._line_with_robot_name("No known memory asset found for this input.")
        else:
            self._line_with_robot_name("External object received")
        self._line_with_robot_name("Memory read complete.")
        return asset

    def show(self, value: Any) -> None:
        resolved = self._resolve_asset(value)

        # If this is a known asset but it has not been read yet,
        # only reveal pointer metadata (address), not the value.
        if resolved is not None and resolved.name not in self._read_asset_names:
            self._line()
            self._line_with_robot_name("Memory pointer detected.")
            self._line(f"{resolved.display_label} ({resolved.name}) @ {resolved.address or 'UNMAPPED'}")
            self._line()
            self._line_with_robot_name("Run robot.read_memory(...) first to unlock this value.")
            return

        if resolved is not None:
            value = resolved.value

        self._line()
        self._line_with_robot_name("Output:")
        if isinstance(value, list):
            for item in value:
                self._line(str(item))
        elif isinstance(value, dict):
            self._line(json.dumps(value, indent=2))
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

    def _is_valid_pin(self, user_id: str, pin: str) -> bool:
        internal = self.config.assets.get("pin_table_internal")
        if internal and isinstance(internal.value, dict):
            expected = internal.value.get(user_id)
            return expected is not None and str(expected) == str(pin)
        
        pins_1 = self.config.assets.get("pins_1")
        if pins_1 and isinstance(pins_1.value, dict):
            expected = pins_1.value.get(user_id)
            return expected is not None and str(expected) == str(pin)
        
        return False
    
    def check_pin(self, user_id: str, pin: str | int) -> bool:
        self._pin_attempt_count += 1
        pin_text = str(pin).strip()
        ok = self._is_valid_pin(str(user_id), pin_text)

        self._line()
        self._line_with_robot_name(f"PIN check ${self._pin_attempt_count}: user_id={user_id}, pin={pin_text}")

        if ok:
            self._line_with_robot_name("PIN accepted. Access channel recovered.")
        else:
            self._line_with_robot_name("PIN rejected. Try another candidate.")
        return ok
    
    def submit(self, answer: Any) -> bool:
        if not self.connected:
            self._line_with_robot_name("Connect first with robot.connect().")
            return False

        if self.finished:
            self._line_with_robot_name("All missions are already complete.")
            return False

        mission = self.current_mission
        expected = mission.expected_answer

        ok = validate_submission(
            mission=mission,
            expected=expected,
            actual=answer,
            robot=self,
        )

        self._line()
        self._line_with_robot_name("Validating submission...")
        time.sleep(self.validation_delay)

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
    
    def _final_reboot(self) -> None:
        old_typing_delay = self.typing_delay
        self._banner("SYSTEM RESTORE / RECOVERY")

        self.typing_delay = 1
        self._block(
            [
                "Locating stable backup image...",
                "Repairing corrupted memory sectors...",
                "Re-enabling safety systems...",
                "Flushing sabotage hooks...",
                "Rebooting core services...",
                "",
                "[#####-----] 50%",
                "[########--] 80%",
                "[##########] 100%",
                "",
                f"{self.config.robot_name} ONLINE",
                "Hello, friend. Thanks for fixing me.",
                "Workshop complete: Hack the Robot recovery successful.",
            ]
        )
        self.typing_delay = old_typing_delay