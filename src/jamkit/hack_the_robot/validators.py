from __future__ import annotations

from typing import Any, Callable

from .models import Mission

Validator = Callable[[Any, Any, Mission, Any], bool]

def _normalised(value: Any) -> str:
    return " ".join(str(value).strip().lower().split())

def exact_match(expected: Any, actual: Any, mission: Mission, robot: Any) -> bool:
    return expected == actual

def case_insensitive_match(expected: Any, actual: Any, mission: Mission, robot: Any) -> bool:
    if not isinstance(expected, str) or not isinstance(actual, str):
        return False
    return expected.strip().lower() == actual.strip().lower()

def pin_match(expected: Any, actual: Any, mission: Mission, robot: Any) -> bool:
    user_id = (
        mission.validator_params.get("user_id")
        or mission.metadata.get("user_id")
        or "svc_311"
    )

    if isinstance(actual, dict):
        submitted_user = actual.get("user_id", user_id)
        submitted_pin = actual.get("pin")
    elif isinstance(actual, (list, tuple)) and len(actual) == 2:
        submitted_user = actual[0]
        submitted_pin = actual[1]
    else:
        submitted_user = user_id
        submitted_pin = actual

    if submitted_pin is None:
        return False
    return robot._is_valid_pin(str(submitted_user), str(submitted_pin))

def restore_command_match(expected: Any, actual: Any, mission: Mission, robot: Any) -> bool:
    if not isinstance(actual, str):
        return False
    
    if isinstance(expected, str) and _normalised(expected) == _normalised(actual):
        return True
    
    if not isinstance(expected, str):
        return False
    
    expected_tokens = _normalised(expected).split()
    actual_tokens = _normalised(actual).split()
    if len(expected_tokens) != len(actual_tokens):
        return False
    
    return expected_tokens == actual_tokens

def recovery_profile_match(expected, actual, mission, robot):
    if not isinstance(expected, dict) or not isinstance(actual, dict):
        return False
    
    exp_slot = str(expected.get("backup_slot", "")).strip().upper()
    act_slot = str(actual.get("backup_slot", "")).strip().upper()

    exp_targets = str(expected.get("repair_targets", []))
    act_targets = str(actual.get("repair_targets", []))

    return exp_slot == act_slot and exp_targets == act_targets


VALIDATORS: dict[str, Validator] = {
    "exact": exact_match,
    "case_insensitive": case_insensitive_match,
    "pin_match": pin_match,
    "restore_command": restore_command_match,
    "recovery_profile": recovery_profile_match
}

def validate_submission(mission: Mission, expected: Any, actual: Any, robot: Any) -> bool:
    if mission.validator_name:
        Validator = VALIDATORS.get(mission.validator_name)
        if Validator is None:
            raise ValueError(f"Unknown validator: {mission.validator_name}")
        return Validator(expected, actual, mission, robot)
    
    if isinstance(expected, str):
        return case_insensitive_match(expected, actual, mission, robot)
    return exact_match(expected, actual, mission, robot)