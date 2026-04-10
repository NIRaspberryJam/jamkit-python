# Base Code
from jamkit.hack_the_robot import Robot, msg_1, logs_1, pin_parts_1, account_1

robot = Robot()
robot.connect()

robot.hint() # hints are optional

# Mission 1
robot.read_memory(msg_1)
robot.show(msg_1)

decoded = ""
for ch in msg_1:
    if ch.isalpha():
        decoded += chr(ord(ch) - 1)
    else:
        decoded += ch

robot.show(decoded)

# Mission 2
robot.read_memory(logs_1)

for line in logs_1:
    robot.show(line)
    if "LOCKOUT" in line or "override" in line:
        parts = line.split()
        for part in parts:
            if part.startswith("user="):
                user_id = part.replace("user=", "")
                break

robot.show(user_id)

# Mission 3
robot.read_memory(pin_parts_1)
robot.show(pin_parts_1)

prefixes = pin_parts_1["prefixes"]
suffixes = pin_parts_1["suffixes"]

for prefix in prefixes:
    for suffix in suffixes:
        candidate = prefix + suffix
        
        if robot.check_pin(user_id, candidate):
            found_pin = candidate

robot.show(found_pin)

# Mission 4
robot.read_memory(account_1)
robot.show(account_1)

backup_slots = account_1["backup_slots"]

best = None
for slot in backup_slots:
    if slot["status"] != "ready":
        continue

    if best is None or slot["integrity"] > best["integrity"]:
        best = slot

backup_slot = best["slot_id"]
robot.show(backup_slot)

# Mission 5
command = f"RESTORE --user {user_id} --pin {found_pin} --slot {backup_slot} --repair"
robot.show(command)