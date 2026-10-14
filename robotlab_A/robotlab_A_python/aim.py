"""Where must the two joints point so the beam lands on a spot on the ceiling?
Edit the settings below, then just press Run. Start with DRY_RUN = True: it prints the angles and touches no hardware.
When the numbers look right, set DRY_RUN = False to drive the real arm (yaw ID 1, pitch ID 2).
Terminal users can still type:  python aim.py 0.5 0 --move
"""
import math
import sys

DRY_RUN = True       # True: only print. False: also move the real arm.
TARGET_X, TARGET_Y = 0.5, 0.0    # the ceiling spot to aim at, metres (x forward, y left of straight above the arm)
HOLD = 3.0           # seconds to hold the position before the motors go limp

HEIGHT = 2.0          # metres from the pitch axis up to the ceiling. Measure yours.
YAW_SIGN, PITCH_SIGN = +1, +1          # flip to -1 if your joint turns the other way
YAW_ZERO, PITCH_ZERO = 0.0, 0.0        # degrees. Nonzero if your pointer is not mounted straight


def aim(x, y, height=HEIGHT):
    """Ceiling spot (x forward, y left, metres, measured from straight above the arm) -> (yaw_deg, pitch_deg).
    Pitch 0 means the pointer looks straight up, like the URDF. Pitch grows as it tips toward the spot."""
    yaw = math.degrees(math.atan2(y, x)) if (x or y) else 0.0
    off_axis = math.hypot(x, y)                       # how far the spot is from straight above
    pitch = math.degrees(math.atan2(off_axis, height))
    return YAW_SIGN * yaw + YAW_ZERO, PITCH_SIGN * pitch + PITCH_ZERO


def move_to(x, y, hold=HOLD):
    """Send the real arm to ceiling point (x, y). Same calls as move_arm.py: goal_pos(id, to_steps(degrees))."""
    import time
    from bus import open_bus, close_bus, torque, goal_pos, present_pos, to_steps, to_deg
    yaw, pitch = aim(x, y)
    if abs(yaw) > 150 or not -10 <= pitch <= 90:
        raise SystemExit(f"yaw {yaw:.1f} / pitch {pitch:.1f} is outside what the arm can do. Pick a closer point.")
    open_bus()
    try:
        torque(1, True)
        torque(2, True)
        goal_pos(1, to_steps(yaw))             # the yaw joint, ID 1
        goal_pos(2, to_steps(pitch))           # the pitch joint, ID 2
        time.sleep(hold)
        print(f"arm reports yaw {to_deg(present_pos(1)):+.1f}, pitch {to_deg(present_pos(2)):+.1f} deg. Is the beam on the spot?")
    finally:
        torque(1, False)
        torque(2, False)
        close_bus()


def spot(yaw_deg, pitch_deg, height=HEIGHT):
    """The reverse: joint angles -> where the beam lands. Use it to check aim()."""
    yaw = math.radians(YAW_SIGN * (yaw_deg - YAW_ZERO))
    pitch = math.radians(PITCH_SIGN * (pitch_deg - PITCH_ZERO))
    r = height * math.tan(pitch)
    return r * math.cos(yaw), r * math.sin(yaw)


if __name__ == "__main__":
    print("   x      y     yaw    pitch   spot() says")
    for x, y in [(0, 0), (0.5, 0), (0, 0.5), (0.3, 0.3), (-0.4, 0.2), (0.8, -0.6)]:
        yaw, pitch = aim(x, y)
        sx, sy = spot(yaw, pitch)
        assert abs(sx - x) < 1e-6 and abs(sy - y) < 1e-6, "aim() and spot() disagree"
        print(f"{x:6.2f} {y:6.2f} {yaw:7.1f} {pitch:7.1f}   ({sx:.2f}, {sy:.2f})")
    args = [a for a in sys.argv[1:] if a != "--move"]
    x, y = (float(args[0]), float(args[1])) if len(args) == 2 else (TARGET_X, TARGET_Y)
    yaw, pitch = aim(x, y)
    print(f"\ntarget ({x:.2f}, {y:.2f}) m: yaw {yaw:.1f} deg, pitch {pitch:.1f} deg")
    if DRY_RUN and "--move" not in sys.argv:
        print("DRY_RUN is True, so the motors were not touched. Set DRY_RUN = False to move the arm.")
    else:
        move_to(x, y)
