// Parametric horn-mounted lever arm for a Dynamixel XL430-W250 bench arm.
// All dimensions are in millimetres. Servo dimensions come from the ROBOTIS XL-430 drawing (dated 24-Mar-18).
//
// The arm lies flat: the hub face that bolts to the horn is at Z = 0, the shaft axis is the Z axis,
// and the arm reaches out along +X.
//
// How to use:
//   Open this file in OpenSCAD and press F5 to preview, F6 to render, then Export as STL:
//       openscad -o xl430_arm.stl xl430_arm.scad
//   The base is in xl430_base.scad and the fit-check pieces are in xl430_test_pieces.scad.

$fn = 96;   // smoothness of round features. Lower (for example 48) previews faster.

// ---------------- servo facts from the ROBOTIS XL-430 drawing ----------------
HORN_PCD = 16.0;       // 4 x M2.0 tapped holes on a 16 mm circle (at 0, 90, 180, 270 degrees)

// ---------------- the arm ----------------
ARM_L = 100.0;         // shaft axis to the contact bolt axis
HUB_OD = 26.0;
HUB_T = 4.0;           // thickness of the flat hub that bolts to the horn
BAR_T = 9.0;           // thickness of the raised bar (along the shaft direction)
BAR_START = 14.5;      // the raised bar begins this far from the shaft axis
TIP_R = 7.0;           // tip radius (the bar is 14 mm tall at the tip)
RECESS_D = 10.5;       // clears the centre boss and the centre screw
RECESS_H = 2.4;
HOLE_D = 2.2;          // M2 clearance
CBORE_D = 4.4;         // M2 screw head pocket. Use M2 x 5 screws.
CBORE_H = 1.4;
TIP_HOLE_D = 4.2;      // M4 clearance for the contact bolt
NUT_AF = 7.3;          // M4 nut, across flats, plus clearance
NUT_H = 3.6;

// ---------------------------------------------------------------------------
// the four horn screws: through holes, with a pocket for the head
module horn_screws() {
    for (ang = [0, 90, 180, 270]) {
        x = HORN_PCD / 2 * cos(ang);
        y = HORN_PCD / 2 * sin(ang);
        translate([x, y, -0.01]) cylinder(d = HOLE_D, h = HUB_T + 1);
        translate([x, y, HUB_T - CBORE_H]) cylinder(d = CBORE_D, h = CBORE_H + 1);
    }
}

// ---------------------------------------------------------------------------
module arm_profile(h) {
    R = HUB_OD / 2;
    r = TIP_R;
    linear_extrude(height = h) {
        polygon([[0, R], [ARM_L, r], [ARM_L, -r], [0, -R]]);
        circle(r = R);
        translate([ARM_L, 0]) circle(r = r);
    }
}

module arm() {
    R = HUB_OD / 2;
    r = TIP_R;
    difference() {
        union() {
            arm_profile(HUB_T);                                   // the flat hub
            intersection() {                                      // the raised bar
                arm_profile(BAR_T);
                translate([BAR_START, -30, 0]) cube([ARM_L + 20, 60, BAR_T]);
            }
            // the ramp from the hub up to the bar
            rotate([90, 0, 0]) linear_extrude(height = R * 0.9 * 2, center = true)
                polygon([[BAR_START - (BAR_T - HUB_T), HUB_T], [BAR_START, HUB_T], [BAR_START, BAR_T]]);
        }
        translate([0, 0, -0.01]) cylinder(d = RECESS_D, h = RECESS_H + 0.01);
        horn_screws();
        // contact bolt (M4) runs along Y through the tip
        translate([ARM_L, -r - 1, BAR_T / 2]) rotate([-90, 0, 0]) cylinder(d = TIP_HOLE_D, h = 2 * r + 2);
        // hex nut pocket opens on the +Y face
        translate([ARM_L, r - NUT_H, BAR_T / 2]) rotate([-90, 0, 0])
            cylinder(d = NUT_AF / cos(30), h = NUT_H + 1, $fn = 6);
    }
}

// ---------------------------------------------------------------------------
// draw the arm unless another file has included this one as a library
if (is_undef(XL430_LIBRARY)) arm();
