"""quad_identify.py: find out which servo is on which leg.  Run:  python quad_identify.py   (do this BEFORE quad_calibrate.py)
The computer cannot see the robot. It knows servo IDs, not legs. So it nods one servo at a time and YOU tell it what moved.
At the end it prints the two lines to paste into quad.py, built from what you saw, so the wiring can be anything.

First put a piece of masking tape on each leg and write its letter on it. Forward is the GAP between two legs. Of the two front
legs the left one is A. Then counter-clockwise from above: B = rear-left, C = rear-right, D = front-right.
Hold the robot in the air by the body, or lay it on its back, so the legs can nod freely. Power on, Wizard closed.
"""
from bus import open_bus, close_bus, torque, ping
from quad import HIP_ID, KNEE_ID, LEGS, nod

NAMES = ["front-left", "rear-left", "rear-right", "front-right"]
EXPECT = [(leg, kind, (HIP_ID if kind == "hip" else KNEE_ID)[leg]) for leg in range(4) for kind in ("hip", "knee")]

open_bus()
try:
    missing = [sid for _, _, sid in EXPECT if ping(sid) is None]
    if missing:
        raise SystemExit(f"These IDs did not answer: {missing}. Check power and cables, and that each servo was given its ID in Wizard "
                         f"(run scan_bus.py to see which IDs are really on the bus).")
    print("All eight servos answered: IDs", sorted(HIP_ID + KNEE_ID))
    seen = {}                                              # (leg, 'hip'/'knee') -> servo id, as YOU saw it
    for leg, kind, sid in EXPECT:
        move = "swing sideways (like a windscreen wiper)" if kind == "hip" else "tip up and down"
        print(f"\nServo {sid} is expected to be the {kind} of leg {LEGS[leg]} ({NAMES[leg]}). Watch: it should {move}.")
        nod(sid)
        a = input("Press Enter if that is what you saw. Otherwise type the leg letter you saw move, then h or k for hip or knee (for example Ch): ").strip().upper()
        if a == "":
            seen[(leg, kind)] = sid
        else:
            try:
                seen[(LEGS.index(a[0]), {"H": "hip", "K": "knee"}[a[1]])] = sid
            except (ValueError, KeyError, IndexError):
                print("   I did not understand that, so I counted it as a mismatch. Run the script again.")
    if len(seen) == 8 and all(seen[(leg, kind)] == sid for leg, kind, sid in EXPECT):
        print("\nEvery servo is where the numbering says. Nothing to change. Next: python quad_calibrate.py")
    elif len(seen) == 8:
        print("\nThe wiring is not the way the numbering says. Paste these two lines over the ones in quad.py, then run quad_calibrate.py:")
        print("HIP_ID = " + str([seen[(leg, 'hip')] for leg in range(4)]))
        print("KNEE_ID = " + str([seen[(leg, 'knee')] for leg in range(4)]))
    else:
        print(f"\nOnly {len(seen)} different servos were matched. Two of your answers pointed at the same leg and joint, so run it again.")
finally:
    for _, _, sid in EXPECT:
        try:
            torque(sid, False)
        except Exception:
            pass
    close_bus()
