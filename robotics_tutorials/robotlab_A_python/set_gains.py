"""Change a servo's position-loop gains, then run log_step.py to see the new step response.
Usage:  python set_gains.py ID P D        e.g.  python set_gains.py 2 400 2000
Factory values are about P=800, I=0, D=0 on current firmware. Read them first with no arguments.
"""
import sys
from bus import open_bus, close_bus, read2, write2, POS_P_GAIN, POS_I_GAIN, POS_D_GAIN

open_bus()
try:
    servo = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    if len(sys.argv) == 4:
        write2(servo, POS_P_GAIN, int(sys.argv[2]))
        write2(servo, POS_D_GAIN, int(sys.argv[3]))
    print(f"ID {servo}: P={read2(servo, POS_P_GAIN)}  I={read2(servo, POS_I_GAIN)}  D={read2(servo, POS_D_GAIN)}")
finally:
    close_bus()
