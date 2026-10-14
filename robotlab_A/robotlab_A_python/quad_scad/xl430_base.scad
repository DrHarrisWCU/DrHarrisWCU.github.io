// Parametric desk-clamp motor mount (the base) for a Dynamixel XL430-W250 bench arm.
// All dimensions are in millimetres. Servo dimensions come from the ROBOTIS XL-430 drawing (dated 24-Mar-18).
//
// Coordinates of the mount: X along the servo shaft (horn toward +X), Y sideways (arm rests toward +Y), Z up.
// The servo sits upright, horn end on top.
//
// How to use:
//   Open this file in OpenSCAD and press F5 to preview, F6 to render, then Export as STL:
//       openscad -o xl430_desk_mount.stl xl430_base.scad
//   The arm is in xl430_arm.scad and the fit-check pieces are in xl430_test_pieces.scad.

$fn = 96;   // smoothness of round features. Lower (for example 48) previews faster.

// ---------------- servo facts from the ROBOTIS XL-430 drawing ----------------
SERVO_Y = 28.5;        // width (across the horn face)
SERVO_Z = 46.5;        // height (long direction of the horn face)
SERVO_X = 34.0;        // depth along the shaft, between the two end faces
AXIS_FROM_TOP = 11.25; // shaft axis is this far below the top (horn) end of the body
SIDE_HOLE_DX = 12.0;   // side faces: 2 columns of holes 12 mm apart, centred on the depth
SIDE_HOLE_ROWS = [4.0, 28.0]; // rows are this far below the shaft axis

// ---------------- print and fit settings ----------------
FIT = 0.25;            // clearance per side around the servo body. Raise to 0.3 if your printer runs tight.

// ---------------- the mount ----------------
FLOOR = 6.0;
WALL = 5.0;
BACK_T = 4.0;          // back wall thickness
FRONT_T = 1.2;         // front ring thickness
HORN_HOLE_D = 26.0;    // opening in the front ring around the horn
NOTCH_HW = 8.0;        // cable notch in the back wall: half width
NOTCH_Z = 24.0;        // ... and the height above the floor where it starts
ROOT_R = 2.5;          // inside root fillet radius
PLATE_X0 = -44.0;
PLATE_Y0 = -40.0;
PLATE_Y1 = 50.0;
GUS_T = 4.0;           // gusset thickness
GUS_RISE = 40.0;       // gusset height
GUS_RUN_POS = 22.0;    // how far the gussets stick out of the wall on the +Y side
GUS_RUN_NEG = 17.0;    // ... and on the -Y side
GUS_X = [0.5, 15.25, 28.5]; // x start of the three gussets on each wall; clear of the screw pockets
SCREW_HOLE_D = 2.7;    // M2.5 screws into the servo's side holes
SCREW_CB_D = 5.4;
SCREW_CB_H = 3.0;

// ---------------------------------------------------------------------------
// helpers

// a cylinder that starts at point p and points along the Y axis in direction s (+1 or -1)
module cyl_y(p, s, d, h) {
    translate(p) rotate([-90 * s, 0, 0]) cylinder(d = d, h = h);
}
// a cylinder that starts at point p and points along +X
module cyl_x(p, d, h) {
    translate(p) rotate([0, 90, 0]) cylinder(d = d, h = h);
}

// ---------------------------------------------------------------------------
module mount() {
    Wp = SERVO_Y + 2 * FIT;                 // pocket width (Y)
    Dp = SERVO_X + 2 * FIT;                 // pocket length (X)
    top = FLOOR + SERVO_Z;
    z_axis = FLOOR + SERVO_Z - AXIS_FROM_TOP;
    x_back = -BACK_T;
    x_front = Dp + FRONT_T;
    xc = FIT + SERVO_X / 2;

    difference() {
        union() {
            // base plate with rounded corners
            hull() for (x = [PLATE_X0 + 4, x_front - 4], y = [PLATE_Y0 + 4, PLATE_Y1 - 4])
                translate([x, y, 0]) cylinder(r = 4, h = FLOOR);

            // side walls
            for (sgn = [1, -1])
                translate([x_back, sgn > 0 ? Wp / 2 : -Wp / 2 - WALL, FLOOR])
                    cube([x_front - x_back, WALL, top - FLOOR]);

            // full-height back wall, with a cable notch at the top, ties the two walls together
            difference() {
                translate([-BACK_T, -Wp / 2 - WALL, FLOOR]) cube([BACK_T, Wp + 2 * WALL, top - FLOOR]);
                translate([-BACK_T - 1, -NOTCH_HW, FLOOR + NOTCH_Z]) cube([BACK_T + 2, 2 * NOTCH_HW, top - FLOOR]);
            }

            // front ring ties the walls at the horn end and leaves a C-shaped opening around the horn
            difference() {
                translate([Dp, -Wp / 2 - WALL, FLOOR]) cube([FRONT_T, Wp + 2 * WALL, top - FLOOR]);
                cyl_x([Dp - 1, 0, z_axis], HORN_HOLE_D, FRONT_T + 2);
            }

            // inside root fillets (the servo corner is R3.25 so it clears)
            for (sgn = [1, -1]) {
                yw = sgn * Wp / 2;
                ycen = yw - sgn * ROOT_R;
                difference() {
                    translate([0, sgn > 0 ? yw - ROOT_R : yw, FLOOR]) cube([Dp, ROOT_R, ROOT_R]);
                    cyl_x([-1, ycen, FLOOR + ROOT_R], 2 * ROOT_R, Dp + 2);
                }
            }

            // gussets: three per wall, between the screw pockets
            for (g = [[1, GUS_RUN_POS], [-1, GUS_RUN_NEG]]) {
                sgn = g[0];
                run = g[1];
                yo = sgn * (Wp / 2 + WALL - 0.5);
                pts = [[yo, FLOOR - 0.5], [yo + sgn * (run + 0.5), FLOOR - 0.5],
                       [yo + sgn * (run + 0.5), FLOOR + 1.5], [yo, FLOOR + GUS_RISE]];
                for (gx = GUS_X)
                    translate([gx, 0, 0]) rotate([90, 0, 90]) linear_extrude(height = GUS_T) polygon(pts);
            }
        }

        // screw holes through both walls into the servo's side holes (M2.5 x 6)
        for (dx = [-SIDE_HOLE_DX / 2, SIDE_HOLE_DX / 2], row = SIDE_HOLE_ROWS, sgn = [1, -1]) {
            zz = z_axis - row;
            ys = sgn * Wp / 2;
            cyl_y([xc + dx, ys - sgn * 1, zz], sgn, SCREW_HOLE_D, WALL + 2);
            cyl_y([xc + dx, ys + sgn * (WALL - SCREW_CB_H), zz], sgn, SCREW_CB_D, SCREW_CB_H + 1);
        }
    }
}

// ---------------------------------------------------------------------------
// draw the mount unless another file has included this one as a library
if (is_undef(XL430_LIBRARY)) mount();
