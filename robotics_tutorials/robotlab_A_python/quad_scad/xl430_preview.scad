// =====================================================================
//  xl430_preview.scad  -  shows the stand-in servo from xl430.scad.
//  xl430.scad only holds numbers and modules, so it draws nothing when
//  opened on its own. Open THIS file and press F5 to see the servo.
//  Red dots = the two top-corner case screws on the front face.
// =====================================================================

include <xl430.scad>

xl430_dummy();

color("Red")
    for (screw = top_corner_screws)
        translate([screw[0], screw[1], servo_depth / 2]) cylinder(d = m25_hole, h = 1);
