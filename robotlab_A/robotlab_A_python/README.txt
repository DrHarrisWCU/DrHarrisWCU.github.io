Tutorial A scripts. Setup once, in this folder:

  python3 -m venv robotlab-a-env            (Windows PowerShell:  py -m venv robotlab-a-env)
  source robotlab-a-env/bin/activate        (Windows PowerShell:  robotlab-a-env\Scripts\Activate.ps1)
  pip install dynamixel-api numpy scipy     (dynamixel-api brings dynamixel-sdk with it)
  python check_setup.py

Every new terminal: run the "activate" line again before anything else.
Set servo IDs with Dynamixel Wizard 2.0, then close Wizard before running Python.
Edit the PORT line at the top of a script if your port is not /dev/ttyACM0 (bus.py also reads the DXL_PORT environment variable).

Keep ALL these files in one folder. move_one.py and scan_bus.py stand alone. The later scripts
import bus.py, so if you see  ModuleNotFoundError: No module named 'bus'  the script is not in the same folder as bus.py,
or you are running it with a different Python than the one in your virtual environment.

What each file is for
  check_setup.py     Step 0   checks Python, the libraries and the serial port
  scan_bus.py        Steps 1-2  finds every servo on the bus (stands alone)
  move_one.py        Step 2   moves one servo to +30 and -30 degrees (stands alone)
  bus.py             helper   shared register addresses and conversions, used by the scripts below
  read_status.py     Step 3   prints position, velocity, load, voltage, temperature
  measure_speed.py   Step 4   peak speed of a servo
  load_curve.py      Step 4   scale-based torque calibration (asks for lever length and scale grams)
  arm2dof.urdf       Step 5   robot description of the arm
  move_arm.py        Step 5   moves the two-joint arm
  aim.py             Step 6   inverse kinematics: yaw and pitch to reach a point
  trace.py           Step 7   capstone: trace a path with the arm
Quadruped modules (eight servos: hips 1, 3, 5, 7 and knees 2, 4, 6, 8; every script starts with DRY_RUN = True)
  quad.py            helper   leg kinematics, calibration file, the Robot class and the Mover (read it once, do not edit except the two SIGN lines)
  quad_identify.py   Step 8   nods each servo so you can say which leg it is on; run it BEFORE quad_calibrate.py
  quad_calibrate.py  Step 8   finds each servo's zero and saves quad_calib.json; run it BEFORE anything else below
  quad_stand.py      Step 8   stands the robot at a chosen body height using inverse kinematics
  quad_play.py       Step 9   plays a motion file on leg A (leg_step.json), with optional circle compensation
  leg_step.json      Step 9   the example motion: joint_names, units (deg), points with time_from_start and positions (ROS 2 JointTrajectory shape)
  quad_walk.py       Step 10  a very basic stop-and-go walk (lift, swing, lower, push)
  quad_turn.py       Step 12  a very basic turn-in-place gait
  quad_smooth.py     Step 13  the same gaits as smooth curves, one sync-write packet per update
Optional modules (they work on one servo at a time)
  set_gains.py       Optional A   change position P, I, D gains
  log_step.py        Optional A and B   record a step response to a CSV
  fit_log.py         Optional B   fit a model to that CSV
