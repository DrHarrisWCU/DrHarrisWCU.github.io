"""Move one XL430 with dynamixel_api. This file needs no other file from the zip.
Run:  python move_one.py        (servo ID 1)       python move_one.py 2     (servo ID 2)
Close Dynamixel Wizard first: only one program can hold the serial port.
"""
import sys
import time
from dynamixel_api import XL430W250TConnector

PORT = "/dev/ttyACM0"   # The top of Wizard's device list shows yours. Linux: ttyACM0 (OpenCR) or ttyUSB0 (U2D2).
                        # Windows: COM4 or similar. macOS: /dev/cu.usbmodemXXXX.
BAUD = 57600            # factory setting of the XL430
SERVO_ID = int(sys.argv[1]) if len(sys.argv) > 1 else 1

TICKS_PER_TURN = 4096   # one full turn is 4096 ticks
CENTER = 2048           # tick for "0 degrees". Ticks cannot be negative, so we measure angles from the middle.


def deg_to_ticks(deg):
    """Degrees from center -> goal ticks, clamped into the legal range 0..4095."""
    ticks = round(CENTER + deg * TICKS_PER_TURN / 360)
    return max(0, min(TICKS_PER_TURN - 1, ticks))


def ticks_to_deg(ticks):
    return (ticks - CENTER) * 360 / TICKS_PER_TURN


def wait_until_there(servo, goal_ticks, tolerance=8, timeout=4.0):
    """Poll the real position instead of guessing a sleep time. Returns True if it arrived."""
    start = time.time()
    while time.time() - start < timeout:
        if abs(servo.read_field("present_position") - goal_ticks) <= tolerance:
            return True
        time.sleep(0.02)
    return False


# Leaving the "with" block turns torque off again, so the servo is limp when the script ends.
with XL430W250TConnector(device=PORT, baud_rate=BAUD, dynamixel_id=SERVO_ID) as servo:
    print(f"Connected to servo {SERVO_ID}")
    servo.write_field("profile_velocity", 50)                         # about 11 rpm: smooth and safe (unit 0.229 rpm)
    here = servo.read_field("present_position")
    servo.write_field("goal_position", here)                          # goal = where we are, so torque-on does not jerk
    servo.write_field("torque_enable", 1)                             # now the motor holds its position
    for angle in (0, 30, -30, 0):                                     # degrees from center
        goal = deg_to_ticks(angle)
        servo.write_field("goal_position", goal)
        arrived = wait_until_there(servo, goal)
        measured = ticks_to_deg(servo.read_field("present_position"))
        print(f"goal {angle:+4d} deg = {goal:4d} ticks   measured {measured:+7.1f} deg   {'ok' if arrived else 'did not arrive'}")
