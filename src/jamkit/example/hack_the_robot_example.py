from jamkit.hack_the_robot import Robot, msg_1

robot = Robot()
robot.connect()

# Mission 1
robot.read_memory(msg_1)
decoded = ""
for ch in msg_1:
    if ch.isalpha():
        decoded += chr(ord(ch) - 1)
    else:
        decoded += ch
robot.submit(decoded)