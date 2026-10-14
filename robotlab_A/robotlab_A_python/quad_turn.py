"""A turn-in-place gait, the same sequence of moves as the SunFounder crawler kit's turn: lift a foot, move ALL the feet to
their new places at once, put the foot down. Edit the settings, then press Run. DRY_RUN = True prints every pose, touches nothing.

The robot turns counter-clockwise seen from above (TURN_LEFT = True). Legs take turns being the one in the air: A, B, C, D.
One cycle is four stages, and each stage is three moves:
  lift   the leg whose turn it is goes up, in place
  sweep  ALL four hips move together. The three feet on the floor swing back by STROKE degrees, which turns the body.
         The foot in the air swings forward by 3 x STROKE, to the front of its stroke, ready to be the next foot down.
  lower  that leg goes down.
Every foot gets 3 sweeps on the floor and 1 trip in the air, so after four stages every leg is back where it began.
Because each leg is a different distance through its stroke, the feet are staggered, and that stagger is what keeps the
centre of mass inside the three feet that are down. No extra lean is needed.
"""
from quad import Robot, Mover, describe, lifted_legs, body_turn, LEGS

DRY_RUN = True
TURN_LEFT = True      # False turns the other way
CYCLES = 2
STAND_KNEE = 40.0     # knee angle with the foot on the floor
LIFT_KNEE = 15.0      # knee angle with the foot in the air
STROKE = 8.0          # how far each planted hip swings per stage, degrees. Bigger = faster turn and safer, but a bigger swing in the air
LEG_SPEED = 90.0      # deg/s for lifting and lowering
TURN_SPEED = 40.0     # deg/s for the sweep (the foot in the air moves at this speed, the others slower, so they all arrive together)
SETTLE = 0.15


def turn_keyframes():
    """Return a list of (name, pose, speed). pose = {leg: (hip_yaw, knee)} for all four legs."""
    S, K = STROKE, STAND_KNEE
    d = 1 if TURN_LEFT else -1                    # +1: planted hips swing toward smaller yaw
    order = (0, 1, 2, 3) if TURN_LEFT else (0, 3, 2, 1)
    top = 1.5 * S                                 # the front of the stroke. The stroke runs from +1.5 S down to -1.5 S
    # steady state before stage 0: the leg lifted last is at the top, the one lifted first is at the bottom
    pose = {}
    for leg in range(4):
        age = (-order.index(leg) - 1) % 4         # stages since this leg was in the air
        pose[leg] = [d * (top - S * age), K]
    frames = []

    def snap(name, speed):
        frames.append((name, {l: tuple(v) for l, v in pose.items()}, speed))

    snap("stand ready", LEG_SPEED)
    for leg in order:
        pose[leg][1] = LIFT_KNEE;  snap(f"lift leg {LEGS[leg]}", LEG_SPEED)
        for other in range(4):
            pose[other][0] += d * 3 * S if other == leg else -d * S
        pose[leg][0] = d * top                    # the foot in the air goes to the front of its stroke
        snap(f"sweep: leg {LEGS[leg]} returns, the others turn the body", TURN_SPEED)
        pose[leg][1] = STAND_KNEE; snap(f"lower leg {LEGS[leg]}", LEG_SPEED)
    return frames


if __name__ == "__main__":
    frames = turn_keyframes()
    total, worst = 0.0, 0.0
    for prev, cur in zip(frames, frames[1:]):
        if cur[0].startswith("sweep"):
            planted = [l for l in range(4) if l not in lifted_legs(cur[1], STAND_KNEE)]
            turned, slide = body_turn(prev[1], cur[1], planted)
            total += turned
            worst = max(worst, slide)
    print(f"one cycle turns the body about {abs(total):.1f} degrees {'left' if total > 0 else 'right'}, and the worst foot slide is {worst:.1f} mm")
    robot = Robot(dry_run=DRY_RUN)
    try:
        mover = Mover(robot)
        mover.start(frames[0][1])
        for cycle in range(CYCLES):
            for name, pose, speed in frames[1:]:
                print(describe(name, pose, lifted_legs(pose, STAND_KNEE)))
                mover.go_to(pose, speed, SETTLE)
        print(f"{CYCLES} cycles take {mover.seconds():.1f} s ({mover.updates} updates of eight goals)")
        if DRY_RUN:
            print("DRY_RUN is True, so nothing moved. Check that no line says TIPS, then set DRY_RUN = False.")
    finally:
        robot.close()
