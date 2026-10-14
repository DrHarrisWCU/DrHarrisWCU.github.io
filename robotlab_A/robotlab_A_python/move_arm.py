"""Drive the 2-joint arm: ID 1 is the yaw joint, ID 2 is the pitch joint. No ROS."""
import math
import time
from bus import open_bus, close_bus, torque, goal_pos, present_pos, to_steps, to_deg

YAW, PITCH = 1, 2

open_bus()
try:
    torque(YAW, True)
    torque(PITCH, True)

    s1pos = 0                                  # yaw, degrees
    s2pos = 30                                 # pitch, degrees. The URDF limit is +-90.
    goal_pos(YAW, to_steps(s1pos))
    goal_pos(PITCH, to_steps(s2pos))
    time.sleep(1.5)

    # A slow sweep: yaw +-40 degrees every 4 seconds, pitch +-20 degrees every 2 seconds.
    start = time.time()
    while time.time() - start < 6.0:
        t = time.time() - start
        goal_pos(YAW, to_steps(40 * math.sin(2 * math.pi * t / 4.0)))
        goal_pos(PITCH, to_steps(20 * math.sin(2 * math.pi * t / 2.0)))
        time.sleep(0.02)                       # about 50 updates per second

    print(f"yaw {to_deg(present_pos(YAW)):+.1f} deg, pitch {to_deg(present_pos(PITCH)):+.1f} deg")
finally:
    torque(YAW, False)
    torque(PITCH, False)
    close_bus()
