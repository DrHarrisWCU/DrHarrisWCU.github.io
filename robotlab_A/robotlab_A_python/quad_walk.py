"""A very basic stop-and-go walk.  Edit the settings, then press Run.  DRY_RUN = True prints every pose and touches nothing.
The robot walks toward the gap between leg D and leg A (that is "forward"). Every leg takes a step, one at a time. For each leg:
  lean   the two legs beside the leg you are about to lift slide their feet toward it, so the weight sits over the other three
  lift   knee up
  swing  hip yaw carries the foot forward
  lower  knee down
  centre the two neighbours slide back
After all four legs have stepped, one more move:
  push   all four hips sweep back together: the body is carried forward
The legs are at 45 degrees to the walking direction, so a hip can only push the foot along a line at 45 degrees to it.
Every foot skids sideways on the floor during the push, by as much as the body moves forward. That is why the feet should be smooth plastic.
There are only a few speeds: fast for a foot in the air, slow while all feet are on the floor.
"""
import time
from quad import Robot, Mover, lean_offsets, describe, lifted_legs, forward_sign, body_move, LEGS

DRY_RUN = True
CYCLES = 2            # how many steps to take
STAND_KNEE = 40.0     # knee angle with the foot on the floor (body about 100 mm high)
LIFT_KNEE = 15.0      # knee angle with the foot in the air
STROKE = 12.0         # every hip swings between +STROKE and -STROKE of yaw around its standing position
LEAN = 20.0           # how far the neighbours slide their feet to catch the weight
ORDER = (0, 2, 3, 1)  # legs A, C, D, B (front-left, rear-right, front-right, rear-left): each lifted foot is far from the last one
LEG_SPEED = 90.0      # deg/s for lifting, swinging and lowering a foot (nothing heavy rides on it)
BODY_SPEED = 30.0     # deg/s while all feet are on the floor: leaning, centring, pushing. Slow, so nothing slips
SETTLE = 0.15         # seconds to wait after each move so the servos catch up


def walk_keyframes():
    """Return a list of (name, pose, speed). pose = {leg: (hip_yaw, knee)} for all four legs."""
    S, K, L = STROKE, STAND_KNEE, LEAN
    pose = {leg: [-forward_sign(leg) * S, K] for leg in range(4)}     # every foot starts at the BACK of its stroke
    frames = []

    def snap(name, speed):
        frames.append((name, {l: tuple(v) for l, v in pose.items()}, speed))

    snap("stand", BODY_SPEED)
    for leg in ORDER:
        offsets = lean_offsets(leg, L)
        for l, o in offsets.items():
            pose[l][0] += o
        snap(f"lean toward leg {LEGS[leg]}", BODY_SPEED)
        pose[leg][1] = LIFT_KNEE;                    snap(f"lift leg {LEGS[leg]}", LEG_SPEED)
        pose[leg][0] = forward_sign(leg) * S;        snap(f"swing leg {LEGS[leg]} forward", LEG_SPEED)
        pose[leg][1] = STAND_KNEE;                   snap(f"lower leg {LEGS[leg]}", LEG_SPEED)
        for l, o in offsets.items():
            pose[l][0] -= o
        snap("centre again", BODY_SPEED)
    for leg in range(4):
        pose[leg][0] = -forward_sign(leg) * S
    snap("push: body moves forward", BODY_SPEED)
    return frames


if __name__ == "__main__":
    frames = walk_keyframes()
    fwd, side, slide = body_move(frames[-2][1], frames[-1][1], range(4))
    print(f"one cycle moves the body about {fwd:.0f} mm forward ({side:+.0f} mm sideways); every foot skids about {slide:.0f} mm during the push")
    robot = Robot(dry_run=DRY_RUN)
    try:
        mover = Mover(robot)
        mover.start(frames[0][1])
        for cycle in range(CYCLES):
            for name, pose, speed in frames[1:]:
                print(describe(name, pose, lifted_legs(pose, STAND_KNEE)))
                mover.go_to(pose, speed, SETTLE)         # all eight joints, one packet per 20 ms, until they arrive
        print(f"{CYCLES} cycles take {mover.seconds():.1f} s ({mover.updates} updates of eight goals)")
        if DRY_RUN:
            print("DRY_RUN is True, so nothing moved. Check that no line says TIPS, then set DRY_RUN = False.")
    finally:
        robot.close()
