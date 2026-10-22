Tutorial A scripts. 

Follow the tutorial series at https://drharriswcu.github.io/robotlab_A to install everything correctly.

Typical Linux setup once in this folder:

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

3D-printed parts (the quad_scad folder)
  The parts are drawn in OpenSCAD, a free program that builds 3D models from a short text script
  instead of by dragging shapes with the mouse. Every size is a named number near the top of the file,
  so you change a number, preview, and export a new STL for your slicer.
  Download it (Windows, macOS, Linux) from  https://openscad.org/downloads.html
  On Ubuntu/Debian you can also use:  sudo apt install openscad

  Using a file: open it in OpenSCAD, press F5 to preview, F6 to render, then File > Export > Export as STL.
  Or from a terminal:  openscad -o part.stl file.scad
  Files with a "part" setting export one piece at a time:  openscad -o fit_ring.stl -D 'part="fit_ring"' xl430_test_pieces.scad
  Keep ALL the .scad files in one folder: most of them load xl430.scad (and each other) with include/use.
  All sizes are in millimetres and all servo sizes come from the ROBOTIS XL430-W250 drawing.

  Shared servo model (draws nothing by itself)
    xl430.scad              XL430-W250 dimensions, screw positions and a simple stand-in servo (xl430_dummy)
                            used by every other file. Also defines the servo axes the other files use.
    xl430_preview.scad      opens xl430.scad and shows the stand-in servo; red dots mark the two
                            top-corner case screws that the printed parts bolt to

  Bench arm (one servo clamped to the desk)
    xl430_arm.scad          Step 4   a lever arm that bolts to the servo horn       (export: xl430_arm.stl)
    xl430_base.scad         Step 4   a desk-clamp mount that holds the servo upright (export: xl430_desk_mount.stl)
    xl430_test_pieces.scad  Step 4   two quick fit-check pieces: a ring with the servo-shaped opening and a disc with
                            the horn screw pattern. Print these FIRST to check your printer's fit before the
                            full parts. part = "all", "fit_ring" or "horn_plate". Sizes come from the two files above.

  Quadruped (Steps 8-13, eight servos). Parts to print for one robot:
    body_plates.scad        the body plate that holds the 4 hip servos, one per corner.   Print 2
                            (one on top of the servos, one flipped underneath; the servos are the spacers).
                            Has a centre window with a cross brace and a hub for the IMU / boards. No supports.
                            Screws per plate: 8 x M2.5 flat-head x 12 and 8 x M2.5 flat-head x 14
                            (they replace the M2.5 x 10 case screws; swap one at a time).
    hip_bracket.scad        joins a hip servo to its knee servo: flat ears clamp the hip horn and idler,
                            upright ears clamp the knee horn and idler.                   Print 4
                            The file draws it already lying on one knee ear, the way it goes on the
                            print bed, so export it as is. Use supports "everywhere", not "build plate only":
                            the hip ears and the top knee ear both need them.
                            A wide web and a tapered rib on each hip ear make the joint between the hip ears
                            and the middle block stronger.
                            Screws per bracket: 16 x M2 x 6. When rendered it prints "knee axis is ... mm"
                            in the console; copy that number into knee_x in leg_assembly_preview.scad.
    leg.scad                the lower leg, screwed to the knee servo's case by two thin plates,
                            ending in a tapered blade and foot.                           Print 4
                            Print lying on the back plate, as it comes out of the file.
                            Screws per leg: 4 x M2.5 flat-head x 12.
  Preview-only files (nothing here gets printed; change the angles and press F5 to check for collisions)
    leg_assembly_preview.scad  one complete leg: hip servo, hip bracket, knee servo and leg, at hip_angle and knee_angle
    robot_preview.scad      the whole walker: both body plates and all four legs at the same angles
