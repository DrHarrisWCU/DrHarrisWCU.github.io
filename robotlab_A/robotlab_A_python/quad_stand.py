"""Stand the robot up at a chosen body height, using inverse kinematics.  Edit the settings, then press Run.
Start with DRY_RUN = True: it prints the knee angle and the eight servo goals and touches nothing.
First real run: hold the robot in the air by the body so the feet hang free, then set DRY_RUN = False.
"""
import time
from quad import Robot, knee_for_height, height_of, describe

DRY_RUN = True
HEIGHT = 100.0        # how high the underside of the body plate should ride above the floor, mm
HOLD = 5.0            # seconds to stand before the servos go limp

knee = knee_for_height(HEIGHT)
pose = {leg: (0.0, knee) for leg in range(4)}
print(f"inverse kinematics: for {HEIGHT:.0f} mm the knee angle is {knee:.1f} deg (forward kinematics check: {height_of(knee):.1f} mm)")
print(describe("stand", pose))
robot = Robot(dry_run=DRY_RUN, profile_velocity=30)       # a slow profile, so nothing slams
try:
    goals = robot.go(pose)
    print("goals:", goals)
    if DRY_RUN:
        print("DRY_RUN is True, so nothing moved. Set DRY_RUN = False to stand up.")
    else:
        time.sleep(HOLD)
finally:
    robot.close()
