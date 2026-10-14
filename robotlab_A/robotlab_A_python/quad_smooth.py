"""Smooth walking: the same key poses as quad_walk.py / quad_turn.py, but the eight joints glide through them at 50 updates a second.
Edit the settings, then press Run. DRY_RUN = True simulates the whole thing, prints the fastest joint speed, and touches nothing.
Idea: instead of 'go to this pose, wait', build a smooth curve through the key poses for every joint, then read that curve
50 times a second and send ALL eight goals in one sync-write packet.
"""
import math
import time
from quad import Robot, describe, lifted_legs
import quad_walk
import quad_turn

DRY_RUN = True
GAIT = "walk"          # "walk" or "turn"
CYCLES = 3
RATE = 50              # updates per second
TIME_PER_POSE = 0.45   # seconds between one key pose and the next. Smaller = faster walking
SPEED_LIMIT = 200.0    # deg/s you allow any joint. Compare with the top speed you measured in Module 4


def pchip(ts, ys):
    """Smooth curve through the points (ts[i], ys[i]) that never overshoots between them. Returns f(t) -> (value, slope)."""
    n = len(ts)
    h = [ts[i + 1] - ts[i] for i in range(n - 1)]
    d = [(ys[i + 1] - ys[i]) / h[i] for i in range(n - 1)]
    m = [0.0] * n
    for i in range(1, n - 1):
        if d[i - 1] * d[i] > 0:                    # same direction on both sides: blend the slopes
            w1, w2 = 2 * h[i] + h[i - 1], h[i] + 2 * h[i - 1]
            m[i] = (w1 + w2) / (w1 / d[i - 1] + w2 / d[i])
        # else: the joint turns around here (a peak), so its speed is zero here
    m[0], m[-1] = d[0], d[-1]
    if d[0] == 0:
        m[0] = 0.0
    if d[-1] == 0:
        m[-1] = 0.0

    def f(t):
        t = min(max(t, ts[0]), ts[-1])
        i = min(max(max(k for k in range(n - 1) if ts[k] <= t), 0), n - 2)
        s = (t - ts[i]) / h[i]
        h00, h10, h01, h11 = 2 * s**3 - 3 * s**2 + 1, s**3 - 2 * s**2 + s, -2 * s**3 + 3 * s**2, s**3 - s**2
        v = h00 * ys[i] + h10 * h[i] * m[i] + h01 * ys[i + 1] + h11 * h[i] * m[i + 1]
        ds = (6 * s**2 - 6 * s) * ys[i] + (3 * s**2 - 4 * s + 1) * h[i] * m[i] + (-6 * s**2 + 6 * s) * ys[i + 1] + (3 * s**2 - 2 * s) * h[i] * m[i + 1]
        return v, ds / h[i]
    return f


def build_curves():
    frames = (quad_walk.walk_keyframes() if GAIT == "walk" else quad_turn.turn_keyframes())[1:]   # skip the slow 'stand' pose
    stand_knee = quad_walk.STAND_KNEE if GAIT == "walk" else quad_turn.STAND_KNEE
    frames = frames + [frames[0]]                    # close the loop: end where you began
    ts = [i * TIME_PER_POSE for i in range(len(frames))]
    curves = {}
    for leg in range(4):
        for j, name in enumerate(("hip", "knee")):
            curves[(leg, j)] = pchip(ts, [fr[1][leg][j] for fr in frames])
    return curves, ts[-1], frames[0][1], stand_knee


if __name__ == "__main__":
    curves, period, first, stand_knee = build_curves()
    robot = Robot(dry_run=DRY_RUN, profile_velocity=30)
    try:
        robot.go(first)                                   # slowly to the first pose
        if not DRY_RUN:
            time.sleep(2.5)
            for sid in robot.ids:
                robot.bus.write4(sid, robot.bus.PROFILE_VELOCITY, 0)   # now we do the smoothing ourselves
        dt = 1.0 / RATE
        frames_sent, fastest, worst_margin = 0, 0.0, 1e9
        t0 = time.perf_counter()
        for cycle in range(CYCLES):
            for k in range(int(period * RATE)):
                t = k * dt
                pose, speeds = {}, []
                for leg in range(4):
                    (yaw, v1), (knee, v2) = curves[(leg, 0)](t), curves[(leg, 1)](t)
                    pose[leg] = (yaw, knee)
                    speeds += [abs(v1), abs(v2)]
                fastest = max(fastest, max(speeds))
                frames_sent += 1
                robot.go(pose)                            # ONE packet carries all eight goals
                if not DRY_RUN:                           # wait for the next tick on a fixed schedule, not "sleep(dt)"
                    wait = t0 + frames_sent * dt - time.perf_counter()
                    if wait > 0:
                        time.sleep(wait)
        print(f"{GAIT}: {frames_sent} updates, one cycle takes {period:.1f} s, fastest joint {fastest:.0f} deg/s "
              f"({'within' if fastest <= SPEED_LIMIT else 'OVER'} your limit of {SPEED_LIMIT:.0f})")
        if DRY_RUN:
            print("DRY_RUN is True, so nothing moved. Set DRY_RUN = False (feet off the floor first) to try it.")
    finally:
        robot.close()
