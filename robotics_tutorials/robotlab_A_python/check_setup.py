"""Run this first. It checks Python, the libraries, and lists the serial ports it can see.  Usage:  python check_setup.py"""
import importlib.metadata as md
import os
import platform
import sys

in_venv = sys.prefix != sys.base_prefix
print("venv         :", ("active: " + os.path.basename(sys.prefix)) if in_venv else "NOT active  ->  switch it on first (source robotlab-a-env/bin/activate, or robotlab-a-env\\Scripts\\Activate.ps1 on Windows)")
print("python       :", platform.python_version(), "" if sys.version_info >= (3, 8) else "  <-- too old, install Python 3.8 or newer")
for pkg in ("dynamixel-api", "dynamixel-sdk", "numpy", "scipy"):
    try:
        print(f"{pkg:<13}:", md.version(pkg))
    except md.PackageNotFoundError:
        print(f"{pkg:<13}: MISSING  ->  with the venv on:  pip install {pkg}" + ("   (only needed for fit_log.py)" if pkg in ("numpy", "scipy") else ""))

print("serial ports :", end=" ")
try:
    from serial.tools import list_ports          # pyserial comes along with dynamixel-sdk
    ports = [f"{p.device} ({p.description})" for p in list_ports.comports()]
    print("; ".join(ports) if ports else "none found. Plug in the adapter / OpenCR, switch it on, and run this again.")
except ImportError:
    print("pyserial missing, so the list is unavailable. Install the libraries first.")
print("Put the name you see (for example /dev/ttyACM0 or COM4) in the PORT line at the top of each script.")
