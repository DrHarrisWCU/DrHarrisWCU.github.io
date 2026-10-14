"""Log commanded and measured position for Optional B. Saves run1.csv."""
import csv
import math
import time
from bus import open_bus, close_bus, torque, goal_pos, present_pos, to_steps, to_deg

SERVO = 2                  # the pitch joint, with nothing attached to the horn yet
DURATION = 3.0             # seconds


def command(t):
    """Same command as Optional B, in radians: a step, a rest, a small step, then a 2 Hz sine."""
    if t < 0.1: return 0.0
    if t < 0.7: return 0.5
    if t < 1.2: return 0.0
    if t < 1.5: return 0.25
    if t < 2.5: return 0.25 + 0.2 * math.sin(2 * math.pi * 2.0 * (t - 1.5))
    return 0.25


open_bus()
rows = []
try:
    torque(SERVO, True)
    goal_pos(SERVO, to_steps(0))
    time.sleep(1.0)
    start = time.perf_counter()
    while True:
        t = time.perf_counter() - start
        if t > DURATION:
            break
        cmd = command(t)
        goal_pos(SERVO, to_steps(math.degrees(cmd)))
        meas = to_deg(present_pos(SERVO))      # read straight after writing
        rows.append((t, cmd, math.radians(meas)))
finally:
    torque(SERVO, False)
    close_bus()

with open("run1.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["t", "cmd_rad", "meas_rad"])
    w.writerows(rows)
print(f"saved {len(rows)} rows, about {len(rows) / DURATION:.0f} samples per second")
