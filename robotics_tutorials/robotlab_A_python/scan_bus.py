"""Find every servo on the bus, at every common baud rate. This file needs no other file from the zip.
Run it with the servos plugged in and Dynamixel Wizard CLOSED.
Uses dynamixel_sdk, which pip installed together with dynamixel-api.
"""
from dynamixel_sdk import PortHandler, PacketHandler, COMM_SUCCESS

PORT = "/dev/ttyACM0"   # Linux: ttyACM0 (OpenCR) or ttyUSB0 (U2D2). Windows: COM4 or similar. Same name Wizard shows.
BAUDS = [57600, 115200, 1000000, 2000000, 3000000, 4000000, 9600]   # factory baud for the XL430 is 57600

packet = PacketHandler(2.0)
found_any = False
for baud in BAUDS:
    port = PortHandler(PORT)
    if not port.openPort():
        raise SystemExit(f"Cannot open {PORT}. Wrong name, or another program (Wizard?) is using it.")
    port.setBaudRate(baud)
    found, result = packet.broadcastPing(port)       # one packet that every servo answers
    port.closePort()
    for servo_id, (model, firmware) in sorted(found.items()):
        found_any = True
        print(f"baud {baud:>7}: found ID {servo_id:3d}, model {model}, firmware {firmware}")
if not found_any:
    print("Nothing answered at any baud rate. Check power, the cable, the port name, and that Wizard is closed.")
