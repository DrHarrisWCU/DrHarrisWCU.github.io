"""Light painting: the arm draws a shape on the ceiling with a pointer.  Hardware: yaw ID 1, pitch ID 2.
Start with DRY_RUN = True: it prints what it WOULD send and touches no hardware.
Take a phone photo with a 5 to 10 second exposure (Night mode, or a long-exposure app) while it runs.
"""
import math
import time
from aim import aim

DRY_RUN = True
YAW, PITCH = 1, 2
SHAPE = "square"             # "square", "circle", or "triangle"
SIZE = 0.40                  # metres (side, or diameter)
CENTRE = (0.5, 0.0)          # metres on the ceiling, from straight above the arm
SPEED = 0.10                 # metres per second for the beam on the ceiling
RATE = 50                    # goal updates per second
CORNER_PAUSE = 0.15          # seconds to wait at each corner so the servo catches up


def corners(shape):
    cx, cy = CENTRE
    h = SIZE / 2
    if shape == "square":
        return [(cx - h, cy - h), (cx + h, cy - h), (cx + h, cy + h), (cx - h, cy + h), (cx - h, cy - h)]
    if shape == "triangle":
        return [(cx - h, cy - h), (cx + h, cy), (cx - h, cy + h), (cx - h, cy - h)]
    n = 48
    return [(cx + h * math.cos(2 * math.pi * k / n), cy + h * math.sin(2 * math.pi * k / n)) for k in range(n + 1)]


def path(shape):
    """Yield (x, y, pause) points about SPEED/RATE metres apart along the outline."""
    pts = corners(shape)
    step = SPEED / RATE
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        n = max(1, int(math.hypot(x1 - x0, y1 - y0) / step))
        for k in range(n):
            yield x0 + (x1 - x0) * k / n, y0 + (y1 - y0) * k / n, 0.0
        yield x1, y1, (0.0 if shape == "circle" else CORNER_PAUSE)   # a circle has no corners to wait at


if not DRY_RUN:
    from bus import open_bus, close_bus, torque, goal_pos, to_steps, write4, PROFILE_VELOCITY
    open_bus()
    torque(YAW, True)
    torque(PITCH, True)
    write4(YAW, PROFILE_VELOCITY, 0)
    write4(PITCH, PROFILE_VELOCITY, 0)

count = 0
try:
    first = True
    for x, y, pause in path(SHAPE):
        yaw, pitch = aim(x, y)
        if DRY_RUN:
            if count % 25 == 0 or pause:
                print(f"spot ({x:+.2f}, {y:+.2f}) -> yaw {yaw:+6.1f}, pitch {pitch:+6.1f}")
        else:
            goal_pos(YAW, to_steps(yaw))
            goal_pos(PITCH, to_steps(pitch))
            if first:
                time.sleep(2.0)                  # let the arm reach the first corner before drawing
                first = False
        count += 1
        time.sleep(0 if DRY_RUN else (pause or 1 / RATE))
    print(f"{count} points {'planned' if DRY_RUN else 'sent'}")
finally:
    if not DRY_RUN:
        torque(YAW, False)
        torque(PITCH, False)
        close_bus()
