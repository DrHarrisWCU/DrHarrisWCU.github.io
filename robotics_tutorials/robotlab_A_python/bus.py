"""bus.py: the few Dynamixel calls the later modules need, in one place. Keep it in the SAME folder as the scripts that import it.
It uses dynamixel_sdk, ROBOTIS's own library, which pip installs for you together with dynamixel-api.
Run it on its own to test the connection:  python bus.py
Why not dynamixel_api here? It opens one port connection per servo, and two arm joints must share one port (and one packet).
"""
import os
from dynamixel_sdk import PortHandler, PacketHandler, GroupSyncWrite, COMM_SUCCESS

PORT = os.environ.get("DXL_PORT", "/dev/ttyACM0")   # OpenCR passthrough. U2D2: /dev/ttyUSB0. Windows: COM3
BAUD = int(os.environ.get("DXL_BAUD", "57600"))      # factory setting for the XL430

# Control table addresses (XL430-W250). Look them up again with the e-Manual if your model differs.
ID, OPERATING_MODE = 7, 11
POS_D_GAIN, POS_I_GAIN, POS_P_GAIN = 80, 82, 84
GOAL_PWM, PROFILE_VELOCITY, GOAL_POSITION = 100, 112, 116
MOVING, PRESENT_LOAD, PRESENT_VELOCITY, PRESENT_POSITION = 122, 126, 128, 132
PRESENT_VOLTAGE, PRESENT_TEMP, HARDWARE_ERROR = 144, 146, 70
TORQUE_ENABLE = 64

_port = PortHandler(PORT)
_packet = PacketHandler(2.0)


def to_steps(angle_deg):
    """Joint angle in degrees -> servo ticks. 0 degrees is tick 2048, the same zero the URDF uses."""
    return max(0, min(4095, 2048 + round(angle_deg * 4096 / 360)))


def to_deg(steps):
    return (steps - 2048) * 360 / 4096


def signed(value, nbytes):
    """Registers hold raw bytes. Load and velocity can be negative, so reinterpret as two's complement."""
    top = 1 << (8 * nbytes - 1)
    return value - 2 * top if value >= top else value


def open_bus():
    if not _port.openPort():
        raise SystemExit(f"Cannot open {PORT}. Wrong name, or another program is using it.")
    if not _port.setBaudRate(BAUD):
        raise SystemExit(f"Cannot set {BAUD} baud on {PORT}.")


def close_bus():
    _port.closePort()


def _check(result, error):
    if result != COMM_SUCCESS:
        raise RuntimeError(_packet.getTxRxResult(result))
    if error != 0:
        raise RuntimeError(_packet.getRxPacketError(error))


# ---- generic register access: every other helper is built from these six ----
def write1(servo_id, addr, value): _check(*_packet.write1ByteTxRx(_port, servo_id, addr, int(value)))
def write2(servo_id, addr, value): _check(*_packet.write2ByteTxRx(_port, servo_id, addr, int(value)))
def write4(servo_id, addr, value): _check(*_packet.write4ByteTxRx(_port, servo_id, addr, int(value)))


def _read(fn, servo_id, addr):
    value, result, error = fn(_port, servo_id, addr)
    _check(result, error)
    return value


def read1(servo_id, addr): return _read(_packet.read1ByteTxRx, servo_id, addr)
def read2(servo_id, addr): return _read(_packet.read2ByteTxRx, servo_id, addr)
def read4(servo_id, addr): return _read(_packet.read4ByteTxRx, servo_id, addr)


def ping(servo_id):
    """Model number if the servo answers, otherwise None."""
    model, result, error = _packet.ping(_port, servo_id)
    return model if result == COMM_SUCCESS else None


# ---- the helpers from Module 2 ----
def torque(servo_id, on):
    write1(servo_id, TORQUE_ENABLE, 1 if on else 0)


def goal_pos(servo_id, steps):
    """The goal-position packet from Lab 2.1, built and sent for you."""
    write4(servo_id, GOAL_POSITION, steps)


def present_pos(servo_id):
    return read4(servo_id, PRESENT_POSITION)


def sync_goal(goals):
    """Send many goals in ONE packet. goals is {servo_id: steps}. No replies come back."""
    group = GroupSyncWrite(_port, _packet, GOAL_POSITION, 4)
    for servo_id, steps in goals.items():
        group.addParam(servo_id, list(int(steps).to_bytes(4, "little")))
    result = group.txPacket()
    group.clearParam()
    if result != COMM_SUCCESS:
        raise RuntimeError(_packet.getTxRxResult(result))


if __name__ == "__main__":
    # Self-test: list every servo that answers at IDs 1 to 10 and where its horn is now.
    open_bus()
    try:
        print(f"Port {PORT} at {BAUD} baud")
        found = [i for i in range(1, 11) if ping(i)]
        if not found:
            print("No servo answered. Check power, the cable, the port name (PORT at the top of this file), and that Wizard is closed.")
        for i in found:
            print(f"  ID {i}: model {ping(i)}, position {present_pos(i)} ticks = {to_deg(present_pos(i)):+.1f} deg")
    finally:
        close_bus()
