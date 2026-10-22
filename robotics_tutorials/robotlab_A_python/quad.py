"""quad.py: the shared helpers for the four-legged robot. Keep it in the SAME folder as bus.py and the quad_*.py scripts.

Forward is the direction BETWEEN two legs. The legs are named A, B, C, D, seen from above, counter-clockwise starting at the front left:
    A front-left, B rear-left, C rear-right, D front-right.   (Leg A sits 45 degrees counter-clockwise from the forward direction.)
In the code a leg is its place in the lists below: A is 0, B is 1, C is 2, D is 3.
Servo IDs (set them in Wizard like Module 1): hips are the odd numbers 1, 3, 5, 7 and knees the even numbers 2, 4, 6, 8.
Hip 1 and knee 2 are leg A, hip 3 and knee 4 are leg B, and so on.
Angles are in degrees.  Hip yaw 0 = leg straight out from the body, positive = counter-clockwise seen from above.
Knee 0 = leg horizontal pointing outward, positive = foot tips DOWN.  Numbers come from the CAD of the printed parts.
"""
import json
import math
import os
import time

# ---- geometry, millimetres ----
R_HIP = 80.0        # hip axis, out from the body centre
KNEE_OUT = 32.0     # knee axis, out from the hip axis
KNEE_DROP = 26.0    # knee axis, below the underside of the body plate
LEG = 120.0         # knee axis to foot tip

LEG_ANGLE0 = 45.0     # leg A sits 45 degrees counter-clockwise from the forward direction: forward points BETWEEN legs D and A
LEGS = "ABCD"                           # leg names, in order: front-left, rear-left, rear-right, front-right
HIP_ID = [1, 3, 5, 7]                   # hip servo of leg A, B, C, D
KNEE_ID = [2, 4, 6, 8]                  # knee servo of leg A, B, C, D (hip 1 and knee 2 belong to the same leg)
HIP_SIGN, KNEE_SIGN = +1, +1          # flip to -1 if a joint turns the wrong way (all four legs are identical copies)
CALIB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "quad_calib.json")
TICKS_PER_DEG = 4096 / 360


# ---- kinematics ----
def foot_in_leg(yaw, knee):
    """Forward kinematics of one leg. (hip yaw, knee) in degrees -> foot (x, y, z) in mm.
    Origin = the hip axis at the underside of the body plate. x points straight out from the body, z points up."""
    t, p = math.radians(knee), math.radians(yaw)
    reach = KNEE_OUT + LEG * math.cos(t)          # how far the foot is from the hip axis, along the floor
    return reach * math.cos(p), reach * math.sin(p), -(KNEE_DROP + LEG * math.sin(t))


def foot_in_body(leg, yaw, knee):
    """Same, but measured from the body centre. x points FORWARD (between legs D and A), y points left."""
    x, y, z = foot_in_leg(yaw, knee)
    a = math.radians(LEG_ANGLE0 + 90 * leg)
    return (R_HIP + x) * math.cos(a) - y * math.sin(a), (R_HIP + x) * math.sin(a) + y * math.cos(a), z


def height_of(knee):
    """How high the body plate rides above the floor when the foot is on the floor at this knee angle (mm)."""
    return KNEE_DROP + LEG * math.sin(math.radians(knee))


def knee_for_height(h):
    """Inverse kinematics: the knee angle that puts the body plate h mm above the floor."""
    return math.degrees(math.asin((h - KNEE_DROP) / LEG))


def nod(servo_id, degrees=8, pause=0.6):
    """Make one servo nod: hold where it is, turn it a few degrees, turn it back, go limp. Used to show WHICH servo is which."""
    import bus
    start = bus.present_pos(servo_id)
    bus.torque(servo_id, True)                       # torque on first, so the servo holds the pose it is in
    bus.goal_pos(servo_id, start + round(degrees * TICKS_PER_DEG)); time.sleep(pause)
    bus.goal_pos(servo_id, start); time.sleep(pause)
    bus.torque(servo_id, False)


def lean_offsets(lifted, amount):
    """To lift leg `lifted`, its two neighbours slide their feet toward it by `amount` degrees of hip yaw.
    Returns {leg: yaw_offset}."""
    return {(lifted + 1) % 4: -amount, (lifted - 1) % 4: +amount}


def support_margin(points, com=(0.0, 0.0)):
    """Distance in mm from the centre of mass to the nearest edge of the polygon of feet on the floor.
    Negative means the centre of mass is OUTSIDE the polygon (the robot tips over). 3 or 4 points, in order."""
    if len(points) == 3:
        order = points
    else:                                          # sort 4 points around their centre
        cx = sum(p[0] for p in points) / len(points)
        cy = sum(p[1] for p in points) / len(points)
        order = sorted(points, key=lambda p: math.atan2(p[1] - cy, p[0] - cx))
    best, sign = 1e9, 1
    n = len(order)
    cross_sum = sum(order[i][0] * order[(i + 1) % n][1] - order[(i + 1) % n][0] * order[i][1] for i in range(n))
    orient = 1 if cross_sum > 0 else -1
    for i in range(n):
        (x0, y0), (x1, y1) = order[i][:2], order[(i + 1) % n][:2]
        ex, ey = x1 - x0, y1 - y0
        d = orient * (ex * (com[1] - y0) - ey * (com[0] - x0)) / math.hypot(ex, ey)   # positive = inside this edge
        best = min(best, d)
    return best


def body_turn(before, after, legs):
    """How far the body turned (degrees, counter-clockwise) when the planted feet `legs` went from pose `before` to pose `after`,
    and the worst foot slide (mm) left over. A foot that stays on the floor cannot move relative to the floor, so any
    leftover is the foot sliding."""
    P = [foot_in_body(l, *before[l])[:2] for l in legs]
    Q = [foot_in_body(l, *after[l])[:2] for l in legs]
    dot = sum(p[0] * q[0] + p[1] * q[1] for p, q in zip(P, Q))
    cross = sum(p[0] * q[1] - p[1] * q[0] for p, q in zip(P, Q))
    b = math.atan2(cross, dot)                      # how far the feet turned about the body centre
    slide = max(math.hypot(p[0] * math.cos(b) - p[1] * math.sin(b) - q[0], p[0] * math.sin(b) + p[1] * math.cos(b) - q[1]) for p, q in zip(P, Q))
    return -math.degrees(b), slide


def forward_sign(leg):
    """Which way a hip must turn to carry the foot of `leg` toward the front: -1 for the two left legs (A, B), +1 for the right legs (C, D).
    A hip swings its foot sideways to the leg, and a leg at 45 degrees has a forward part to that swing."""
    return -1 if math.sin(math.radians(LEG_ANGLE0 + 90 * leg)) > 0 else +1


def body_move(before, after, legs):
    """How far the body moves (forward mm, sideways mm) when the planted feet `legs` go from pose `before` to pose `after`, and
    the worst foot slide (mm) left over. Planted feet cannot move on the floor, so the body shifts by the average of what the feet
    did, and whatever is left over for each foot is that foot sliding."""
    P = [foot_in_body(l, *before[l])[:2] for l in legs]
    Q = [foot_in_body(l, *after[l])[:2] for l in legs]
    D = [sum(p[i] - q[i] for p, q in zip(P, Q)) / len(legs) for i in (0, 1)]
    slide = max(math.hypot(p[0] - q[0] - D[0], p[1] - q[1] - D[1]) for p, q in zip(P, Q))
    return D[0], D[1], slide


# ---- motions: a list of poses with times, in the same shape as a ROS 2 JointTrajectory ----
def compensated_knee(yaw, knee):
    """The hip swings the foot along a CIRCLE, so the foot drifts in toward the body as the hip turns away from straight out.
    This returns the knee angle that cancels the drift: the foot stays the same distance out from the leg's own straight-out line.
    The price: the knee also sets the height, so the foot rises or sinks a little instead."""
    x_out = KNEE_OUT + LEG * math.cos(math.radians(knee))            # how far out the foot is with the hip straight
    c = (x_out / math.cos(math.radians(yaw)) - KNEE_OUT) / LEG         # the reach the circle would need, turned back into a knee angle
    return math.copysign(math.degrees(math.acos(max(-1.0, min(1.0, c)))), knee)


def load_motion(path):
    """Read a motion file. Returns (joint_names, points) with points = [(time_from_start_seconds, [positions in degrees]), ...]."""
    with open(path) as f:
        m = json.load(f)
    return m["joint_names"], [(p["time_from_start"], p["positions"]) for p in m["points"]]


def motion_poses(names, points, stand_knee=40.0, straighten=False, dt=0.1):
    """Turn a motion into [(time, pose), ...] where pose = {leg: [yaw, knee]} for all four legs. Joints the motion does not name
    stay at yaw 0 and the standing knee. With straighten=True the motion is cut into steps of dt seconds and every leg that has
    both a hip and a knee gets compensated_knee() applied while its foot is in the air, so that part of the path is straight instead of a circle."""
    joints = {}
    for j, name in enumerate(names):
        kind, letter = name.split("_")                           # "hip_A" -> ("hip", "A")
        joints.setdefault(LEGS.index(letter), {})[kind] = j
    times = [t for t, _ in points]

    def at(t, j):                                                # straight line in time between the two points around t
        for (t0, p0), (t1, p1) in zip(points, points[1:]):
            if t0 <= t <= t1:
                return p0[j] if t1 == t0 else p0[j] + (p1[j] - p0[j]) * (t - t0) / (t1 - t0)
        return points[-1][1][j]

    grid = sorted(set(times) | ({round(k * dt, 6) for k in range(int(times[-1] / dt + 1e-9) + 1)} if straighten else set()))
    out = []
    for t in grid:
        pose = {leg: [0.0, stand_knee] for leg in range(4)}
        for leg, js in joints.items():
            if "hip" in js:
                pose[leg][0] = at(t, js["hip"])
            if "knee" in js:
                pose[leg][1] = at(t, js["knee"])
            if straighten and "hip" in js and "knee" in js:           # only while the foot is in the air: a foot on the floor must stay at floor height
                w = max(0.0, min(1.0, (stand_knee - pose[leg][1]) / 10.0))     # 0 on the floor, fading up to 1 when the knee is 10 degrees up
                pose[leg][1] += w * (compensated_knee(pose[leg][0], pose[leg][1]) - pose[leg][1])
        out.append((t, pose))
    return out


def margin_of_pose(pose, lifted=()):
    """Support margin for a pose {leg: (yaw, knee)}. Legs in `lifted` are off the floor."""
    pts = [foot_in_body(l, *pose[l]) for l in range(4) if l not in lifted]
    return support_margin(pts)


# ---- servo ticks ----
def load_calibration():
    try:
        with open(CALIB_FILE) as f:
            return {int(k): int(v) for k, v in json.load(f).items()}
    except FileNotFoundError:
        return None


def joint_to_ticks(servo_id, degrees, sign, zero_ticks):
    """Joint angle -> servo ticks, using the zero you found in calibration:  ticks = zero + sign * angle * 4096 / 360."""
    return max(0, min(4095, round(zero_ticks + sign * degrees * TICKS_PER_DEG)))


class Robot:
    """Eight servos on one bus. With dry_run=True nothing is sent anywhere: it only prints."""

    def __init__(self, dry_run=True, profile_velocity=0):
        self.dry_run = dry_run
        self.calib = load_calibration()
        if self.calib is None:
            if not dry_run:
                raise SystemExit("No quad_calib.json yet. Run quad_calibrate.py first.")
            print("(no quad_calib.json yet: using 2048 as every zero, fine for a dry run)")
            self.calib = {i: 2048 for i in HIP_ID + KNEE_ID}
        self.ids = HIP_ID + KNEE_ID
        if not dry_run:
            import bus
            self.bus = bus
            bus.open_bus()
            for i in self.ids:
                bus.write4(i, bus.PROFILE_VELOCITY, profile_velocity)    # 0 = as fast as it can, otherwise 0.229 rpm per unit
                bus.torque(i, True)

    def set_profile(self, value):
        """Servo speed limit register: 0 = as fast as it can, otherwise 0.229 rpm per unit."""
        if not self.dry_run:
            for i in self.ids:
                self.bus.write4(i, self.bus.PROFILE_VELOCITY, value)

    def goals(self, pose):
        g = {}
        for leg, (yaw, knee) in pose.items():
            g[HIP_ID[leg]] = joint_to_ticks(HIP_ID[leg], yaw, HIP_SIGN, self.calib[HIP_ID[leg]])
            g[KNEE_ID[leg]] = joint_to_ticks(KNEE_ID[leg], knee, KNEE_SIGN, self.calib[KNEE_ID[leg]])
        return g

    def go(self, pose):
        """Send all eight goals in ONE packet (sync write)."""
        g = self.goals(pose)
        if self.dry_run:
            return g
        self.bus.sync_goal(g)
        return g

    def close(self):
        if not self.dry_run:
            for i in self.ids:
                self.bus.torque(i, False)
            self.bus.close_bus()


class Mover:
    """Moves all eight joints together, at a speed you choose:
    you only say WHERE each joint should end up and HOW FAST, and this class sends a new set of goals 50 times a second
    until every joint has arrived. All eight joints start and stop together, in a straight line in joint space.
    The joint with the farthest to go moves at `speed` degrees per second; the others move proportionally slower."""

    def __init__(self, robot, rate=50):
        self.robot, self.rate = robot, rate
        self.cur = None
        self.updates = 0
        self.t0 = None

    def start(self, pose, seconds=2.5):
        """Go to the first pose slowly (the servos' own speed limit), then hand over to the 50 Hz loop."""
        self.cur = {l: list(pose[l]) for l in range(4)}
        self.robot.set_profile(30)
        self.robot.go(self.cur)
        if not self.robot.dry_run:
            time.sleep(seconds)
        self.robot.set_profile(0)

    def _tick(self):
        self.robot.go(self.cur)                      # ONE packet, all eight goals
        self.updates += 1
        if not self.robot.dry_run:                   # wait for the next tick on a fixed schedule
            if self.t0 is None:
                self.t0 = time.perf_counter() - 1.0 / self.rate
            wait = self.t0 + self.updates / self.rate - time.perf_counter()
            if wait > 0:
                time.sleep(wait)

    def go_to(self, pose, speed, settle=0.1):
        """Move every joint to `pose` ({leg: (yaw, knee)}), the farthest one at `speed` deg/s, then wait `settle` seconds."""
        start = {l: list(self.cur[l]) for l in range(4)}
        dist = max(abs(pose[l][j] - start[l][j]) for l in range(4) for j in range(2))
        n = math.ceil(dist / speed * self.rate) if dist > 1e-6 else 0
        for k in range(1, n + 1):
            for l in range(4):
                for j in range(2):
                    self.cur[l][j] = start[l][j] + (pose[l][j] - start[l][j]) * k / n
            self._tick()
        for _ in range(round(settle * self.rate)):   # let the servos finish before the next move
            self._tick()

    def go_for(self, pose, seconds, settle=0.0):
        """Move every joint to `pose` in exactly `seconds`, in a straight line, one packet per tick. This is the way a ROS 2
        joint trajectory works: each point says WHEN to arrive, not how fast to go."""
        start = {l: list(self.cur[l]) for l in range(4)}
        n = math.ceil(seconds * self.rate - 1e-9)
        for k in range(1, n + 1):
            for l in range(4):
                for j in range(2):
                    self.cur[l][j] = start[l][j] + (pose[l][j] - start[l][j]) * k / n
            self._tick()
        for _ in range(round(settle * self.rate)):
            self._tick()

    def seconds(self):
        """How long everything sent so far takes at this rate."""
        return self.updates / self.rate


def describe(name, pose, lifted=()):
    """One printed line for a dry run: the pose and how safely the robot stands in it."""
    m = margin_of_pose(pose, lifted)
    s = "  ".join(f"{LEGS[l]}:{pose[l][0]:+5.1f}/{pose[l][1]:4.1f}" for l in range(4))
    return f"{name:<28} {s}   margin {m:6.1f} mm {'OK' if m > 10 else 'TIPS' if m < 0 else 'close'}"


def lifted_legs(pose, stand_knee):
    """A leg counts as lifted when its knee is noticeably above the standing angle."""
    return tuple(l for l in range(4) if pose[l][1] < stand_knee - 5)


if __name__ == "__main__":
    print("leg A, knee 40 degrees, yaw 0: foot at", [round(v, 1) for v in foot_in_leg(0, 40)], "mm from the hip axis")
    print("body height at knee 40:", round(height_of(40), 1), "mm.  Knee for 100 mm:", round(knee_for_height(100), 1), "deg")
    pose = {l: (0, 40) for l in range(4)}
    print("four feet down, margin", round(margin_of_pose(pose), 1), "mm.  Leg A lifted, margin", round(margin_of_pose(pose, (0,)), 1), "mm  <- on the edge!")
    r = Robot(dry_run=True)
    print("goals:", r.go(pose))
