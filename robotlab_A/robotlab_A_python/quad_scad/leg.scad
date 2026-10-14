// =====================================================================
//  leg.scad  -  the lower leg. It is screwed to the KNEE servo's case.
// =====================================================================
//  Like the RealAnt "leg", but it holds the servo the only safe way:
//  two THIN plates, one on the front face and one on the back face,
//  each held by the 2 top case screws (the ones next to the horn).
//  The plates run past the far end of the servo to an end wall,
//  and a tapered blade runs from the wall to the foot.
//
//   one plate, looking at the servo's front face:
//
//      bridge  ____
//      screw  o    o  screw          The plates are thinner than the horn
//            ||(  )||                sticks out, so the hip bracket's knee
//       rail ||    || rail           ears can turn over them without rubbing.
//            ||    ||
//            || servo case ends here
//            ||    ||  <- room for the cables
//          [== end wall ==]>======= blade =======( foot )
//
//  The knee servo's horn and idler bolt to the KNEE ears of hip_bracket.scad,
//  so when the knee servo turns, its whole case (and this leg) swings.
//
//  Screws: 4 x M2.5 flat-head, 2 mm longer than the case screws you take out
//          (the drawing lists M2.5 x 10, so use M2.5 x 12). Swap one screw at a time.
//  Print:  lay it on the back plate (as it comes out of this file).
//          The front plate needs supports under it.
//
//  Uses the servo coordinates from xl430.scad: shaft = Z, case runs to +X.
//  Press F5 to preview, F6 to render, then File > Export > STL.
// =====================================================================

include <xl430.scad>

// ---------- things you might want to change ----------
plate_t    = 2.0;   // plate thickness. MUST be less than horn_proud (2.2).
pad_r      = 4.5;   // radius of the round pad around each screw
horn_gap   = 0.5;   // space between the turning horn and the plate
rail_in    = 9;     // the rails run from this far off the centre line ...
rail_out   = servo_width / 2 + 3;   // ... to this far (3 mm past the case edge)
top_bridge_w = 3;   // strip across the top end that ties the two screws together (0 = none)
cable_room = fit;   // gap between the end of the servo and the end wall. "fit" = snug against
                    // the servo; make it bigger (e.g. 8) if the cable plugs need room there.
wall_t     = 5;     // end wall thickness
leg_length = 120;   // knee axis -> centre of the foot
foot_r     = 6;     // radius of the rounded foot
blade_t    = 10;    // blade thickness (Z)
holes      = 3;     // lightening holes in the blade (0 for none)
hole_d     = 7;

assert(plate_t < horn_proud, "plate_t must be thinner than horn_proud, or the bracket ears rub on it");

// ---------- worked out from the numbers above ----------
face_z  = servo_depth / 2;               // z of the servo's front face (the back face is at -face_z)
outer_z = face_z + plate_t;              // z of the outside of a plate
wall_x  = axis_from_bottom + cable_room; // where the end wall starts
bottom  = -outer_z;                      // z of the flat bottom face (outside of the back plate)


// The outline of one plate, flat, in servo X/Y.
module plate_2d() {
    difference() {
        union() {
            // a rail from each top screw down to the end wall
            for (screw = top_corner_screws) {
                side = sign(screw[1]);   // +1 or -1
                hull() {
                    translate(screw) circle(r = pad_r);
                    translate([wall_x, side > 0 ? rail_in : -rail_out]) square([1, rail_out - rail_in]);
                }
            }
            // bridge across the top end of the servo
            if (top_bridge_w > 0)
                translate([-axis_from_top - top_bridge_w, -servo_width / 2 + corner_inset])
                    square([top_bridge_w + 1, servo_width - 2 * corner_inset]);
        }
        circle(d = horn_d + 2 * horn_gap);    // the horn turns inside here
    }
}

// The front plate, with its 2 countersunk screw holes. The back plate is a mirror copy.
module front_plate() {
    difference() {
        translate([0, 0, face_z]) linear_extrude(height = plate_t) plate_2d();
        for (screw = top_corner_screws)
            translate([screw[0], screw[1], face_z]) countersunk_hole(plate_t);
    }
}

module end_wall() {
    translate([wall_x, -rail_out, -outer_z]) cube([wall_t, 2 * rail_out, 2 * outer_z]);
}

module blade() {
    difference() {
        translate([0, 0, bottom]) linear_extrude(height = blade_t) hull() {
            translate([wall_x, -rail_out]) square([wall_t, 2 * rail_out]);   // wide at the wall
            translate([leg_length, 0]) circle(r = foot_r);                   // narrow at the foot
        }
        // lightening holes, evenly spaced between the wall and the foot
        wall_end = wall_x + wall_t;
        for (i = [1 : holes]) {
            x = wall_end + i * (leg_length - foot_r - wall_end) / (holes + 1);
            translate([x, 0, bottom - 1]) cylinder(d = hole_d, h = blade_t + 2);
        }
    }
}

module leg() {
    front_plate();
    mirror([0, 0, 1]) front_plate();   // back plate
    end_wall();
    blade();
}

// lift it so the flat bottom sits on the print bed (z = 0)
translate([0, 0, -bottom]) leg();
