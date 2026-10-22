"""Find each servo's zero tick and save it in quad_calib.json.  Run:  python quad_calibrate.py
The servo's own zero (tick 2048) is wherever the horn happened to be when you screwed the leg on. You tell the computer
what 'hip straight out' and 'knee horizontal' look like on YOUR robot by holding the leg there while it reads the ticks.
Needs the robot powered, the eight IDs set (hips 1, 3, 5, 7 and knees 2, 4, 6, 8), and bus.py + quad.py in this folder.
"""
import json
import time
from bus import open_bus, close_bus, torque, present_pos, goal_pos
from quad import HIP_ID, KNEE_ID, CALIB_FILE, HIP_SIGN, KNEE_SIGN, TICKS_PER_DEG, nod, LEGS

IDS = HIP_ID + KNEE_ID
names = {0: "front-left", 1: "rear-left", 2: "rear-right", 3: "front-right"}

open_bus()
try:
    for i in IDS:
        torque(i, False)                   # limp, so you can move every joint by hand
    zeros = {}
    for leg in range(4):
        print(f"\nLeg {LEGS[leg]} ({names[leg]}): the one with the tape marked {LEGS[leg]}. Watch it nod, hip first and then knee...")
        for sid in (HIP_ID[leg], KNEE_ID[leg]):
            nod(sid)
        input(f"Hold it so that the HIP points straight out from the body along its arm and the KNEE leg is HORIZONTAL, "
              f"pointing outward. Press Enter while you hold it still... ")
        for sid in (HIP_ID[leg], KNEE_ID[leg]):
            zeros[sid] = present_pos(sid)
            print(f"   servo {sid}: zero = {zeros[sid]} ticks  ({(zeros[sid] - 2048) * 360 / 4096:+.1f} deg from tick 2048)")
    with open(CALIB_FILE, "w") as f:
        json.dump(zeros, f, indent=1)
    print(f"\nSaved {CALIB_FILE}.")

    print("\nDirection test on leg A. The leg will move 15 degrees and come back. Keep your hands clear.")
    input("Press Enter to move the HIP of leg A (front-left) by +15 degrees... ")
    z = zeros[HIP_ID[0]]
    torque(HIP_ID[0], True)
    goal_pos(HIP_ID[0], round(z + HIP_SIGN * 15 * TICKS_PER_DEG)); time.sleep(1.5)
    print("Seen from ABOVE, did the foot swing COUNTER-CLOCKWISE (toward leg B, the rear-left)?  If not, set HIP_SIGN = -1 in quad.py.")
    goal_pos(HIP_ID[0], z); time.sleep(1.5); torque(HIP_ID[0], False)
    input("Press Enter to move the KNEE of leg A by +15 degrees... ")
    z = zeros[KNEE_ID[0]]
    torque(KNEE_ID[0], True)
    goal_pos(KNEE_ID[0], round(z + KNEE_SIGN * 15 * TICKS_PER_DEG)); time.sleep(1.5)
    print("Did the foot tip DOWN toward the floor?  If it went up, set KNEE_SIGN = -1 in quad.py.")
    goal_pos(KNEE_ID[0], z); time.sleep(1.5)
finally:
    for i in IDS:
        try:
            torque(i, False)
        except Exception:
            pass
    close_bus()
