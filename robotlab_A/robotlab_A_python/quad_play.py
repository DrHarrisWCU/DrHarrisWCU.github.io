"""Play a recorded motion: a list of poses, each with the time to ARRIVE there. Edit the settings, then press Run.
DRY_RUN = True prints every pose and the foot position it gives, and touches nothing.

The motion file is the same shape as a ROS 2 JointTrajectory message, so the same idea carries over to ROS later:
    joint_names      which joints, in order, e.g. ["hip_A", "knee_A"]   (hip_A is the hip of leg A, knee_A its knee)
    points           a list of  { "time_from_start": seconds, "positions": [one number per joint name] }
Here positions are in degrees. ROS 2 uses radians, and one multiplication by pi/180 will turn them into radians when you get there.
You can write the file by hand, or copy it from Lab 9.1 in the tutorial. Joints the file does not name stay standing.
"""
import math
from quad import Robot, Mover, load_motion, motion_poses, foot_in_leg, LEGS

DRY_RUN = True
MOTION_FILE = "leg_step.json"   # next to this script
LOOPS = 2               # play it this many times (only if it ends where it started)
STRAIGHTEN = False      # True: cut the motion into 0.1 s steps and cancel the circle the hip draws, but only while the foot is in the air
STAND_KNEE = 40.0       # the knee angle for joints the file does not name
SPEED_LIMIT = 200.0     # deg/s you allow any joint. Compare with the top speed you measured in Module 4


names, points = load_motion(MOTION_FILE)
poses = motion_poses(names, points, STAND_KNEE, STRAIGHTEN)
named_legs = sorted({LEGS.index(n.split("_")[1]) for n in names})

worst = 0.0
for (t0, p0), (t1, p1) in zip(poses, poses[1:]):
    if t1 > t0:
        worst = max(worst, max(abs(p1[l][j] - p0[l][j]) for l in range(4) for j in range(2)) / (t1 - t0))
print(f"{MOTION_FILE}: {len(points)} points, {poses[-1][0]:.1f} s, joints {names}")
print(f"fastest joint speed: {worst:.0f} deg/s (limit {SPEED_LIMIT:.0f})")
if worst > SPEED_LIMIT:
    raise SystemExit("Too fast. Give that move more time in the file.")
loops = LOOPS
if any(abs(poses[0][1][l][j] - poses[-1][1][l][j]) > 1e-6 for l in range(4) for j in range(2)):
    print("This motion does not end where it starts, so it will play once. Make the last pose equal the first to loop it.")
    loops = 1

robot = Robot(dry_run=DRY_RUN)
try:
    mover = Mover(robot)
    mover.start(poses[0][1])
    for _ in range(loops):
        for (t0, _p0), (t1, p1) in zip(poses, poses[1:]):
            if t1 <= t0:
                continue
            feet = "  ".join(f"leg {LEGS[l]} foot x{foot_in_leg(*p1[l])[0]:6.1f} y{foot_in_leg(*p1[l])[1]:6.1f} z{foot_in_leg(*p1[l])[2]:7.1f}" for l in named_legs)
            print(f"t = {t1:5.2f} s   " + "  ".join(f"{LEGS[l]}: hip {p1[l][0]:+6.1f} knee {p1[l][1]:5.1f}" for l in named_legs) + "   " + feet)
            mover.go_for(p1, t1 - t0)                 # all eight joints, one packet per 20 ms, arriving exactly at t1
    print(f"{loops} play(s) take {mover.seconds():.1f} s ({mover.updates} updates of eight goals)")
    if DRY_RUN:
        print("DRY_RUN is True, so nothing moved. Check the numbers, then set DRY_RUN = False with the robot held in the air.")
finally:
    robot.close()
