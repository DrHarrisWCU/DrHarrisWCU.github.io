// =====================================================================
//  leg_assembly_preview.scad  -  one leg put together, for checking fit.
//  Nothing here gets printed. Change the two angles and press F5 to
//  see whether anything collides. robot_preview.scad uses one_leg() too.
// =====================================================================

use <hip_bracket.scad>   // brings in hip_bracket()
use <leg.scad>           // brings in leg()
include <xl430.scad>

hip_angle  = 0;     // degrees, turns the bracket about the vertical hip axis
knee_angle = 45;    // degrees, positive swings the leg down

knee_x = 48;        // copy this from the "knee axis is ..." line that hip_bracket.scad prints

// The hip servo, its bracket, the knee servo and the leg.
// The hip axis is the Z axis; the leg reaches out along +X.
module one_leg(hip_angle, knee_angle) {
    // hip servo: fixed to the body, case pointing back toward the body (-X)
    rotate([0, 0, 180]) xl430_dummy();

    rotate([0, 0, hip_angle]) {
        color("DarkOrange") hip_bracket();

        // knee servo + leg: shaft along Y, swinging together
        translate([knee_x, 0, 0]) rotate([-90, 0, 0]) rotate([0, 0, knee_angle]) {
            xl430_dummy();
            color("Orange") leg();
        }
    }
}

one_leg(hip_angle, knee_angle);
