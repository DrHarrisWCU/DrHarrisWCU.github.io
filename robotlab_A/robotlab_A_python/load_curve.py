"""Calibrate the Present Load register against a real force, using a lever pressing on a kitchen scale.
Usage:  python load_curve.py [ID] [SIGN]        SIGN is 1 or -1: the direction that pushes the bar onto the scale.

Setup (see the Speed and torque module): servo body clamped, a stiff bar on the horn, the bar tip resting on a scale, bar horizontal.
The script switches the servo to PWM mode (it pushes with a chosen fraction of full drive and does not try to
reach a position) and pushes at five gentle levels, one at a time. For each level it counts down to the push,
tells you when to watch the scale, counts down the push itself, and then asks for the highest number you saw.
Saves load_curve.csv with columns mass_g, lever_m, torque_nm, load_pct.
"""
import csv
import math
import sys
import time
from bus import (open_bus, close_bus, torque, write1, write2, read1, read2, signed,
                 OPERATING_MODE, GOAL_PWM, PRESENT_LOAD, HARDWARE_ERROR)

SERVO = int(sys.argv[1]) if len(sys.argv) > 1 else 2
SIGN = int(sys.argv[2]) if len(sys.argv) > 2 else 1
LEVELS = (10, 20, 30, 40, 50)      # percent of full drive. Stop at 50: this is a stall test and the motor heats up.
HOLD_S = 4.0                       # seconds to push at each level
GET_READY_S = 5                    # countdown before the first push
REST_S = 8                         # rest between pushes (also lets the motor cool a little)
TICK_S = 1.0                       # length of one countdown step
PWM_FULL = 885                     # the XL430's default PWM limit; one unit is about 0.113 percent
G = 9.81
rows = []


def countdown(text, seconds):
    """Print a line that counts down once per second, e.g.  'Level 20 percent: pushing in  5 s'."""
    for left in range(int(seconds), 0, -1):
        print(f"\r  {text} {left:2d} s   ", end="", flush=True)
        time.sleep(TICK_S)
    print(f"\r  {text}  0 s   ")


open_bus()
try:
    torque(SERVO, False)
    write1(SERVO, OPERATING_MODE, 16)            # 16 = PWM control. The mode can only change while torque is off.
    torque(SERVO, True)
    lever = float(input("Distance from the shaft centre to where the bar touches the scale, in metres: "))
    input("Bar horizontal, resting on the scale, scale zeroed (tared). Press Enter to begin. ")
    for n, pct in enumerate(LEVELS):
        print(f"\nLevel {pct} percent  ({n + 1} of {len(LEVELS)}).  Hands clear of the bar.")
        if n == 0:
            countdown(f"Pushing starts in", GET_READY_S)
        else:
            countdown(f"Resting. Pushing starts in", REST_S)
        print(f"  >>> PUSHING NOW: watch the scale and remember the HIGHEST number it shows <<<")
        write2(SERVO, GOAL_PWM, SIGN * round(pct / 100 * PWM_FULL) & 0xFFFF)
        readings = []
        start = time.time()
        shown = None
        while time.time() - start < HOLD_S:
            left = math.ceil(HOLD_S - (time.time() - start))
            if left != shown:
                shown = left
                print(f"\r  Pushing: {left} s left   ", end="", flush=True)
            if time.time() - start > HOLD_S / 2:             # average over the second half: the push has settled
                readings.append(abs(signed(read2(SERVO, PRESENT_LOAD), 2)) * 0.1)
            time.sleep(0.02)
        error = read1(SERVO, HARDWARE_ERROR)
        write2(SERVO, GOAL_PWM, 0)                           # release
        print("\r  Push finished. The bar is released.        ")
        if error:
            print(f"  The servo reported hardware error bits {error:08b} (overload or overheating). Stopping here.")
            break
        load = sum(readings) / len(readings)
        grams = float(input("  Type the highest scale reading you saw, in grams, then press Enter: "))
        torque_nm = grams / 1000 * G * lever
        rows.append((grams, lever, torque_nm, load))
        print(f"  torque {torque_nm:.3f} N*m  ->  load register {load:.1f} percent")
finally:
    try:
        write2(SERVO, GOAL_PWM, 0)
        torque(SERVO, False)
        write1(SERVO, OPERATING_MODE, 3)         # back to normal position mode for every other script
    finally:
        close_bus()

with open("load_curve.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["mass_g", "lever_m", "torque_nm", "load_pct"])
    w.writerows(rows)

pts = [(r[3], r[2]) for r in rows if r[3] > 0.5]
if pts:
    k = sum(l * t for l, t in pts) / sum(l * l for l, t in pts)       # line through the origin
    print(f"\nbest fit: torque = {k:.4f} N*m per percent of load, so 100 percent is about {100 * k:.2f} N*m")
    print("Compare with the datasheet stall torque. Disagree by more than 30 percent? Recheck the lever length and that the bar was horizontal.")
    print("Saved load_curve.csv. Paste its contents into the plot in the tutorial.")
