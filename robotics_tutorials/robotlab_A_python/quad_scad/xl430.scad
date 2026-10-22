// =====================================================================
//  xl430.scad  -  Dynamixel XL430-W250 dimensions + a simple dummy model
// =====================================================================
//  This file draws nothing by itself. Other files load it with:
//      include <xl430.scad>
//  Every number comes from the ROBOTIS XL-430 drawing (24-Mar-18).
//  All units are millimetres.
//
//  SERVO COORDINATES used by every file in this folder:
//      Z axis = the output shaft. The horn is on the +Z face (the "front"),
//               the back idler is on the -Z face (the "back").
//      X axis = the long direction of the case. The shaft is near the
//               -X end (the "top" of the servo); the long part of the
//               case (and the cable connectors) is toward +X.
//      Y axis = across the case (the 28.5 mm direction).
//      The origin (0,0,0) is ON the shaft, halfway between front and back.
//
//   front face, looking at the horn:
//
//        o-----------o      o = case screws in the 4 corners.
//        |   (horn)  |          Only the TOP two (next to the horn) are
//        |     +     |          used to hold parts, on the front AND back.
//        |           |          The side faces have no safe screw holes.
//        |           |
//        o-----------o
// =====================================================================

// ---------- case size ----------
servo_width  = 28.5;    // Y: across the front face
servo_length = 46.5;    // X: the long direction
servo_depth  = 34;      // Z: front face of the case to back face of the case
axis_from_top    = 11.25;                          // shaft to the short (-X) end
axis_from_bottom = servo_length - axis_from_top;   // shaft to the long (+X) end = 35.25

// How far the horn (front) and the idler (back) stand out from the case.
// A part that sits between the case and a bracket ear must be thinner than this.
// !! MEASURE THIS WITH CALIPERS on your own servo. Both sides should match.
horn_proud = 2.2;

// Horn face to back-idler face. Bracket ears clamp these two faces.
wheel_to_wheel = servo_depth + 2 * horn_proud;

// ---------- horn and idler ----------
horn_d   = 20.5;    // outer diameter of the horn and of the back idler
horn_pcd = 16;      // the 4 horn screws sit on a circle this big
horn_screw_angle = 0;   // angle of the first of the 4 screws (they are 90 deg apart)
hub_d    = 8;       // the centre boss (with its screw) that sticks out of the horn

// ---------- case screws in the corners of the front and back faces ----------
corner_inset = 3.25;    // each screw is this far in from both edges (22 x 40 mm pattern)
// the two TOP corner screws (next to the horn), as [x, y], in servo coordinates:
top_corner_screws = [
    [-axis_from_top + corner_inset,  servo_width / 2 - corner_inset],    // [-8,  11]
    [-axis_from_top + corner_inset, -servo_width / 2 + corner_inset]     // [-8, -11]
];
// the two BOTTOM corner screws (far end of the case):
bottom_corner_screws = [
    [axis_from_bottom - corner_inset,  servo_width / 2 - corner_inset],  // [32,  11]
    [axis_from_bottom - corner_inset, -servo_width / 2 + corner_inset]   // [32, -11]
];

// ---------- screws you will use ----------
m2_hole       = 2.2;   // M2 clearance hole  (horn and idler screws, M2 x 6)
m2_head_d     = 4.4;   // M2 screw head pocket
head_pocket_h = 1.5;   // depth of the M2 head pockets
m25_hole      = 2.7;   // M2.5 clearance hole (case corner screws)
m25_csk_d     = 5.0;   // M2.5 flat-head countersink, diameter at the surface

// ---------- printing ----------
fit = 0.25;    // gap per side around the servo case. Use 0.3 if parts come out tight.
$fn = 48;      // circle smoothness (bigger = smoother, slower)


// Grey stand-in for the servo. Only used for previews, never printed.
module xl430_dummy() {
    color("DimGray")
        translate([-axis_from_top, -servo_width / 2, -servo_depth / 2])
            cube([servo_length, servo_width, servo_depth]);
    // horn (+Z) and idler (-Z)
    color("Silver") {
        translate([0, 0, servo_depth / 2])               cylinder(d = horn_d, h = horn_proud);
        translate([0, 0, -servo_depth / 2 - horn_proud]) cylinder(d = horn_d, h = horn_proud);
    }
}

// The 4 horn screws + the centre clearance hole, as solid cylinders standing on
// the XY plane. Subtract them from a plate that has the shaft on its Z axis.
//   plate_t = thickness of that plate
//   pocket  = "top" or "bottom": which face gets the screw-head pockets
module horn_holes(plate_t, pocket = "top") {
    // centre: clears the hub and lets a screwdriver reach the centre screw
    translate([0, 0, -1]) cylinder(d = hub_d + 2, h = plate_t + 2);
    for (a = [0 : 90 : 270]) {
        rotate([0, 0, horn_screw_angle + a]) translate([horn_pcd / 2, 0, 0]) {
            translate([0, 0, -1]) cylinder(d = m2_hole, h = plate_t + 2);
            if (pocket == "top")
                translate([0, 0, plate_t - head_pocket_h]) cylinder(d = m2_head_d, h = head_pocket_h + 1);
            else
                translate([0, 0, -1]) cylinder(d = m2_head_d, h = head_pocket_h + 1);
        }
    }
}

// One M2.5 flat-head screw hole for a plate of thickness plate_t lying on z = 0.
// The countersink (cone) opens on the top face, so the screw head sits flush.
module countersunk_hole(plate_t) {
    csk_depth = (m25_csk_d - m25_hole) / 2;      // 90 degree cone
    translate([0, 0, -1]) cylinder(d = m25_hole, h = plate_t + 2);
    translate([0, 0, plate_t - csk_depth]) cylinder(d1 = m25_hole, d2 = m25_csk_d, h = csk_depth + 0.01);
    translate([0, 0, plate_t]) cylinder(d = m25_csk_d, h = 1);
}
