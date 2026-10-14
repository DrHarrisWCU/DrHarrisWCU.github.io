// =====================================================================
//  hip_bracket.scad  -  joins the HIP servo to the KNEE servo
// =====================================================================
//  Like the RealAnt "hip_joint": a block in the middle with two pairs of ears.
//
//      HIP ears  (flat, top and bottom) clamp the hip servo's horn and idler.
//                The hip axis is vertical (Z) and passes through (0,0,0).
//      KNEE ears (standing up, left and right) clamp the knee servo's horn
//                and idler. The knee axis is horizontal (Y), at x = knee_x.
//
//   view from above:
//
//        hip ear          block        knee ear
//      ( o )=============[#####]=============( o )
//      hip axis         (cable hole)       knee axis
//      x = 0                                x = knee_x
//
//   view from the side (the hip ears and the web that joins them to the block):
//
//              rib  ___
//      ( o )=======/   |               the web runs from the top hip ear to the
//                  |web|##########     bottom one, through the block. A tapered
//                  |   |  block  #     rib on the outside of each hip ear makes
//                  |   |##########     the ear thicker where it meets the web.
//      ( o )=======\___|
//              rib
//
//  The hip ears sit at the same height as the body plates, so everything on
//  the hip ears (and the web that joins them to the block) is kept
//  within hip_reach of the hip axis. The body plates stay outside swing_r
//  (body_plates.scad), which must be a little bigger than hip_reach.
//  The rest of the block only spans the height of the knee ears, which fits
//  between the two body plates.
//
//  Either ear of a pair can take the horn; the holes are the same.
//  Screws: 16 x M2 x 6 (8 into the horns, 8 self-tapping into the idlers).
//
//  Print: this file draws the bracket the way it goes on the print bed,
//         lying on one knee ear. Use supports "everywhere" (not "on build
//         plate only"): the hip ears and the top knee ear both need them.
//         Other files use hip_bracket(), which is the bracket in its
//         assembled position (hip axis = Z), not the print position.
//
//  Press F5 to preview, F6 to render, then File > Export > STL.
// =====================================================================

include <xl430.scad>

// ---------- things you might want to change ----------
ear_t   = 4;      // thickness of every ear
ear_r   = 13;     // radius of the round end of each ear (must cover horn_d / 2)
pad_h   = 0.5;    // small raised disc under each ear: only it touches the horn,
                  // so the ear never rubs on the servo case, or on the
                  // thin plates of leg.scad that sit under the knee ears
block_t = 8;      // thickness of the middle block (along X)
web_t   = 7;      // thickness of the web that joins the hip ears to the block (along X).
                  // It starts at block_x, so keep block_x + web_t at or below hip_reach.
web_hw  = 10;     // half width of that web (along Y). Keep it below web_x in body_plates.scad.
rib_h   = 3;      // extra thickness on the outside of each hip ear where it meets the web
rib_start = 12;   // the rib tapers to nothing here (distance from the hip axis).
                  // Keep it past horn_pcd / 2 + m2_head_d / 2 so the screw heads stay clear.
hip_reach = 26;   // nothing on the hip ears or the web goes further than this from the
                  // hip axis. Keep it below swing_r in body_plates.scad.

// The servos swing inside their ears. A corner of the case is
// sqrt(11.25^2 + 14.25^2) = 18.2 mm from the shaft, so keep these above ~19.
hip_clear  = 19;  // hip axis  -> hip side of the block
knee_clear = 21;  // knee side of the block -> knee axis

cable_hole = [12, 10];   // window through the block for the servo cable (Y, Z)

// ---------- worked out from the numbers above ----------
gap     = wheel_to_wheel + 2 * pad_h;   // inner face to inner face of a pair of ears
outer   = gap / 2 + ear_t;              // half size of the block in Y and Z
block_x = hip_clear;                    // where the block starts
knee_x  = block_x + block_t + knee_clear;   // where the knee axis is

assert(rib_start > horn_pcd / 2 + m2_head_d / 2, "rib_start must clear the horn screw heads");
assert(web_t <= block_t, "web_t must not be thicker than the block");


// One ear, lying flat. Shaft on the Z axis, ear reaching toward +X for "length".
// end_hw is the half width of its flat end.
// The face that touches the servo is the bottom (z = 0); the pad sticks down from it.
module ear(length, end_hw) {
    difference() {
        union() {
            hull() {
                cylinder(r = ear_r, h = ear_t);                       // round end
                translate([length - 1, -end_hw, 0]) cube([1, 2 * end_hw, ear_t]);   // flat end
            }
            translate([0, 0, -pad_h]) cylinder(d = horn_d, h = pad_h);   // the pad
        }
        translate([0, 0, -pad_h]) horn_holes(ear_t + pad_h, "top");
    }
}

// The wedge on the outside of a hip ear: nothing at rib_start, rib_h tall over the web.
// Its bottom face sits on the outside face of the ear (z = 0 here).
module rib() {
    hull() {
        translate([rib_start, -web_hw, 0]) cube([0.01, 2 * web_hw, 0.01]);
        translate([block_x, -web_hw, 0])   cube([web_t, 2 * web_hw, rib_h]);
    }
}

// The bracket in its assembled position: hip axis = Z, knee axis along Y at x = knee_x.
module hip_bracket() {
    hip_ear_len  = block_x + web_t;       // from the hip axis to the far side of the web
    knee_ear_len = knee_x - block_x;      // from the knee axis back to the near side of the block

    difference() {
        union() {
            // middle block: only as tall as the knee ears, so it fits between the body plates
            translate([block_x, -outer, -ear_r]) cube([block_t, 2 * outer, 2 * ear_r]);

            // hip ears + their ribs + the web joining them, trimmed to a circle of radius hip_reach
            intersection() {
                cylinder(r = hip_reach, h = 2 * (outer + rib_h) + 2, center = true);
                union() {
                    translate([block_x, -web_hw, -outer]) cube([web_t, 2 * web_hw, 2 * outer]);
                    for (side = [0, 1])
                        mirror([0, 0, side]) {      // top (+Z), then bottom
                            translate([0, 0, gap / 2]) ear(hip_ear_len, web_hw);
                            translate([0, 0, outer]) rib();
                        }
                }
            }

            // knee ears: +Y side and -Y side (a mirror copy)
            for (side = [0, 1])
                mirror([0, side, 0])
                    translate([knee_x, 0, 0]) rotate([-90, 0, 0]) rotate([0, 0, 180])
                        translate([0, 0, gap / 2]) ear(knee_ear_len, ear_r);
        }
        // cable window through the block
        translate([block_x - 1, -cable_hole[0] / 2, -cable_hole[1] / 2])
            cube([block_t + 2, cable_hole[0], cable_hole[1]]);
    }
}

// The print position: turned so the outside of the -Y knee ear lies flat on the bed (z = 0).
module hip_bracket_print() {
    translate([0, 0, outer]) rotate([90, 0, 0]) hip_bracket();
}

hip_bracket_print();
echo(str("knee axis is ", knee_x, " mm from the hip axis"));
