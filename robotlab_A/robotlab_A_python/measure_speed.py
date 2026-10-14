"""How fast is this servo really?  Usage:  python measure_speed.py [ID]
Swings the horn through 120 degrees at full speed (Profile Velocity = 0), reads the velocity
register as fast as the bus allows, and reports the peak. Nothing may be attached to the horn.
"""
import sys
import time
import math
from bus import (open_bus, close_bus, torque, goal_pos, write4, read4, signed, to_steps,
                 PROFILE_VELOCITY, PRESENT_VELOCITY, PRESENT_POSITION)

SERVO = int(sys.argv[1]) if len(sys.argv) > 1 else 2
RPM_PER_UNIT = 0.229

open_bus()
try:
    torque(SERVO, True)
    write4(SERVO, PROFILE_VELOCITY, 0)          # 0 means "no limit": the motor's own top speed
    goal_pos(SERVO, to_steps(-60))
    time.sleep(1.5)
    samples = []                                 # (time, velocity rad/s, position deg)
    start = time.perf_counter()
    goal_pos(SERVO, to_steps(+60))
    while time.perf_counter() - start < 1.2:
        v = signed(read4(SERVO, PRESENT_VELOCITY), 4) * RPM_PER_UNIT * 2 * math.pi / 60
        p = (read4(SERVO, PRESENT_POSITION) - 2048) * 360 / 4096
        samples.append((time.perf_counter() - start, v, p))
    goal_pos(SERVO, to_steps(0))
    time.sleep(0.5)
finally:
    torque(SERVO, False)
    close_bus()

peak = max(abs(v) for _, v, _ in samples)
# Cross-check: speed from how far the position moved over a 50 ms window (one tick of position is
# too coarse to difference between neighbouring samples).
cross = 0.0
for i, a in enumerate(samples):
    for b in samples[i + 1:]:
        if b[0] - a[0] >= 0.05:
            cross = max(cross, abs((b[2] - a[2]) * math.pi / 180 / (b[0] - a[0])))
            break
print(f"{len(samples)} samples, about {len(samples) / 1.2:.0f} per second")
print(f"peak velocity register : {peak:.2f} rad/s  ({peak * 60 / 2 / math.pi:.0f} rpm)")
print(f"peak from position diff: {cross:.2f} rad/s   (averaged over 50 ms, should be a bit lower)")
print("Use the register value, rounded down a little, as velocity= in the URDF <limit> tag.")
