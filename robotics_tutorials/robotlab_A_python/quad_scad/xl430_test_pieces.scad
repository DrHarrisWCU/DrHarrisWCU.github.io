// Fit-check pieces for the Dynamixel XL430-W250 bench arm. Print these before the full parts.
// All dimensions are in millimetres.
//
// The sizes come from the arm and base files, so changing FIT, the servo facts or the horn
// screw settings there changes these pieces too.
//
// How to use:
//   Open this file in OpenSCAD and press F5 to preview both pieces side by side.
//   To export one piece, change `part` below (or pass it on the command line) and press F6, then Export as STL:
//       openscad -o fit_check_servo_ring.stl -D 'part="fit_ring"' xl430_test_pieces.scad
//       openscad -o fit_check_horn_plate.stl -D 'part="horn_plate"' xl430_test_pieces.scad
//   part is one of: "all", "fit_ring", "horn_plate"

part = "all";

XL430_LIBRARY = true;   // stops the included files from drawing their own part
include <xl430_arm.scad>
include <xl430_base.scad>

// ---------------------------------------------------------------------------
// a thin frame with the servo-shaped opening: print it first to check the fit
module fit_ring() {
    Wp = SERVO_Y + 2 * FIT;
    Hp = SERVO_Z + 2 * FIT;
    difference() {
        cube([Wp + 8, Hp + 8, 6], center = true);
        cube([Wp, Hp, 8], center = true);
    }
}

// a flat disc with the horn screw pattern: print it to check the screw holes line up with the servo horn
module horn_plate() {
    difference() {
        cylinder(d = HUB_OD, h = HUB_T);
        translate([0, 0, -0.01]) cylinder(d = RECESS_D, h = RECESS_H + 0.01);
        horn_screws();
    }
}

// ---------------------------------------------------------------------------
if (part == "fit_ring") fit_ring();
else if (part == "horn_plate") horn_plate();
else {   // all: laid out side by side for a preview (not for printing)
    translate([30, 0, 0]) fit_ring();
    translate([-20, 0, 0]) horn_plate();
}
