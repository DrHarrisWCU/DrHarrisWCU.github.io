"""Print everything a servo knows about itself, 10 times.  Usage:  python read_status.py [ID]
Move the horn by hand (torque is off) and watch the numbers change.
"""
import sys
import time
from bus import (open_bus, close_bus, read1, read2, read4, signed, to_deg,
                 PRESENT_POSITION, PRESENT_VELOCITY, PRESENT_LOAD, PRESENT_VOLTAGE, PRESENT_TEMP, HARDWARE_ERROR)

SERVO = int(sys.argv[1]) if len(sys.argv) > 1 else 1

open_bus()
try:
    print("position_deg  velocity_rpm  load_pct  volts  temp_C  hw_error")
    for _ in range(10):
        pos = to_deg(read4(SERVO, PRESENT_POSITION))
        vel = signed(read4(SERVO, PRESENT_VELOCITY), 4) * 0.229      # raw unit is 0.229 rpm
        load = signed(read2(SERVO, PRESENT_LOAD), 2) * 0.1           # raw unit is 0.1 percent
        volts = read2(SERVO, PRESENT_VOLTAGE) * 0.1                  # raw unit is 0.1 V
        temp = read1(SERVO, PRESENT_TEMP)
        err = read1(SERVO, HARDWARE_ERROR)
        print(f"{pos:12.1f}  {vel:12.1f}  {load:8.1f}  {volts:5.1f}  {temp:6d}  {err:#04x}")
        time.sleep(0.2)
finally:
    close_bus()
