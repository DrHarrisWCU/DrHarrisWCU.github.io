// =====================================================================
//  body_plates.scad  -  the body plate that holds the 4 HIP servos,
//  one at each corner.
// =====================================================================
//  ONE part. Print it twice: one goes on top of the hip servos (horn side),
//  the other goes upside down underneath them (back side). The servos
//  themselves hold the two plates apart, so there are no spacers.
//
//  Each hip servo stands with its shaft vertical and its case pointing in
//  toward the middle of the body. Over each servo the plate has a POD: a
//  wide strip screwed to all 4 case-corner screws on that face, so the servo
//  case becomes part of the frame (like the RealAnt body).
//
//   seen from above:
//
//      hip o                         o hip       o  = hip axis
//           \\___________________//              \\ = pod over a hip servo
//            \                   /               Near the hip axis the pod is a
//             |  o o o o o o o  |                THIN tab (thin_t), because the hip
//             |  o \       / o  |                bracket's ears swing over it there.
//             |  o   [hub]   o  |                The centre has a big window with a
//             |  o /       \ o  |                cross brace (like RealAnt) and a
//             |  o o o o o o o  |                hub for the IMU; boards bolt to the
//            /___________________\               brace, and a ring of M3 holes runs
//           //                   \\              around the edges.
//      hip o                         o hip
//
//  Strength (plastic is not steel): every inside corner is rounded (stress spreads
//  out instead of starting a crack), the pods are as wide as the servo plus 6 mm a
//  side, and each servo is held by 4 screws per plate instead of 2.
//
//  The plate comes out with the servo side flat on the print bed. No supports.
//
//  Screws per plate: 8 x M2.5 flat-head x 12 at the top corners (thin tab),
//                    8 x M2.5 flat-head x 14 at the bottom corners (thick pod).
//                    These replace the case screws (M2.5 x 10): swap one at a time.
//                    Plus whatever your boards need.
// =====================================================================

include <xl430.scad>

// ---------- layout (X = length, front to back; Y = width, side to side) ----------
hip_spacing = [140, 140];  // distance between the hip axes: [front to back, side to side]
centre_size = [120, 120];  // the centre of the plate is a rectangle this big
assert(centre_size[0] < hip_spacing[0] && centre_size[1] < hip_spacing[1],
       "centre_size must be smaller than hip_spacing, or the legs hit the plate");

// the 4 hip axes, one at each corner of the hip_spacing rectangle
hip_positions = [for (sx = [1, -1], sy = [1, -1]) [sx * hip_spacing[0] / 2, sy * hip_spacing[1] / 2]];

// ---------- plate thickness ----------
thin_t  = 2.0;      // the tab under the hip bracket. MUST be less than horn_proud (2.2).
thick_t = 4.0;      // everything else
assert(thin_t < horn_proud, "thin_t must be thinner than horn_proud, or the hip bracket ears rub on it");

// ---------- pods (servo coordinates: x = 0 on the hip axis, +x toward the body centre) ----------
pod_hw       = servo_width / 2 + 6;   // half width of a pod: the servo plus 6 mm each side
pod_overhang = 3;                     // the pod reaches this far past the top end of the servo
fillet_r     = 20;                    // radius where a pod meets the centre (bigger = stronger)

// Where the hip bracket goes (from hip_bracket.scad, for hip angles up to +-90 deg):
swing_r  = 27;   // its hip ears stay inside this circle (hip_reach = 26) ...
pod_start = 15;  // ... and never come further toward the body than this. So the plate is
                 //     thin inside swing_r, but only for x < pod_start.
web_r    = 18.5; // the bracket's web passes through the plate's level between web_r
web_x    = 12;   // and swing_r, for x < web_x (web_hw = 10, plus 2 mm). Nothing at all may be there.

horn_gap     = 0.5;            // space between the turning horn and the tab
cable_window = [16, 27, 7];    // window over the cable plugs: x from, x to, half width

// ---------- centre window with a cross brace ----------
window_size = [70, 70];   // the opening (before the brace is added back)
brace_w     = 14;         // width of the two diagonal braces
hub_d       = 36;         // round hub where the braces cross (the IMU sits here)
window_r    = 4;          // rounding of the window's corners

// ---------- mounting holes for boards ----------
// One line per board. Each board has 4 holes in a rectangle.
//   [ "name",  [x, y] of the board centre on the plate,  [hole spacing x, y],  hole diameter ]
// Holes must land on solid plate: the hub, the braces, or the frame around the window.
// The Raspberry Pi holes fall on the braces; the IMU holes fall on the hub.
boards = [
    [ "Raspberry Pi 4 / 5",           [0, 0], [58, 49],       2.7 ],   // M2.5
    [ "SparkFun ICM-20948 9DoF IMU",  [0, 0], [20.32, 20.32], 3.3 ],   // 4-40 or M3. 1" board, holes 0.8" apart:
                                                                         // MEASURE yours to be sure.
];

// ---------- ring of M3 holes around the edges (for anything else) ----------
edge_pitch = 10;     // distance between holes
edge_hole  = 3.3;    // M3 clearance
edge_inset = 6;      // keep them this far in from the outside edge ...
edge_gap   = 5;     // ... and this far from the window and from other holes


// ---------------------------------------------------------------------
//  placing things at the hips
// ---------------------------------------------------------------------

// Moves its children to each hip, turned so that servo coordinates
// (from xl430.scad) line up: the servo case (+X) points to the body centre.
module at_each_hip() {
    for (p = hip_positions)
        translate(p) rotate(atan2(p[1], p[0]) + 180) children();
}

// Same spots, but turned to point OUT from the body (the way the legs reach).
// robot_preview.scad uses this to place the legs.
module at_each_leg() {
    for (p = hip_positions)
        translate(p) rotate(atan2(p[1], p[0])) children();
}

// ---------------------------------------------------------------------
//  2D shapes for ONE hip, in servo coordinates
// ---------------------------------------------------------------------

// the strip over the servo, from just past its top end all the way to the body centre
module pod_2d() {
    length = norm(hip_positions[0]);
    translate([-axis_from_top - pod_overhang, -pod_hw])
        square([length + axis_from_top + pod_overhang, 2 * pod_hw]);
}

// where the hip ears swing: only the thin tab may be here
module ear_zone_2d() {
    intersection() {
        circle(r = swing_r);
        translate([-swing_r, -swing_r]) square([swing_r + pod_start, 2 * swing_r]);
    }
}

// where the bracket's web swings: no plate at all
module web_zone_2d() {
    intersection() {
        difference() { circle(r = swing_r + 1); circle(r = web_r); }
        translate([-swing_r - 1, -swing_r - 1]) square([swing_r + 1 + web_x, 2 * swing_r + 2]);
    }
}

// the thin tab: the part of the pod inside the ear zone
module thin_tab_2d() {
    difference() {
        intersection() { pod_2d(); ear_zone_2d(); }
        web_zone_2d();
        circle(d = horn_d + 2 * horn_gap);     // the horn turns inside here
    }
}

// ---------------------------------------------------------------------
//  2D shapes for the whole plate
// ---------------------------------------------------------------------

// centre rectangle + 4 pods, with rounded inside corners where they meet
module outline_2d() {
    offset(r = -fillet_r) offset(delta = fillet_r)      // rounds the INSIDE corners
        union() {
            square(centre_size, center = true);
            at_each_hip() pod_2d();
        }
}

// the window in the middle, with the cross brace and hub left in
module window_2d() {
    offset(r = window_r) offset(delta = -window_r)       // rounds the window's corners
        difference() {
            square(window_size, center = true);
            for (d = [[1, 1], [1, -1]])                  // the two diagonal braces
                hull() {
                    translate([ d[0] * window_size[0] / 2,  d[1] * window_size[1] / 2]) circle(d = brace_w);
                    translate([-d[0] * window_size[0] / 2, -d[1] * window_size[1] / 2]) circle(d = brace_w);
                }
            circle(d = hub_d);
        }
}

// the thick part: the outline, minus the ear zones and the window
module thick_2d() {
    offset(r = 2) offset(delta = -2)                     // round off sharp points
        difference() {
            outline_2d();
            at_each_hip() ear_zone_2d();
        }
}

// ---------------------------------------------------------------------
//  working out where the edge holes go
// ---------------------------------------------------------------------

// every board hole as [x, y]
board_hole_points = [for (b = boards, sx = [-1, 1], sy = [-1, 1])
                        b[1] + [sx * b[2][0] / 2, sy * b[2][1] / 2]];

// distance from point p to the nearest point in a list
function nearest(p, points) = min([for (q = points) norm(p - q)]);

// point p in the servo coordinates of the hip at h
function to_servo(p, h) =
    let(a = atan2(h[1], h[0]) + 180, d = p - h)
    [d[0] * cos(a) + d[1] * sin(a), -d[0] * sin(a) + d[1] * cos(a)];

// true if p is over (or right beside) a hip servo
function over_servo(p) =
    len([for (h = hip_positions) let(s = to_servo(p, h))
            if (s[0] < axis_from_bottom + edge_gap && abs(s[1]) < pod_hw) 1]) > 0;

// An edge hole goes on the frame between the window and the outside edge.
function edge_ok(p) =
       abs(p[0]) <= centre_size[0] / 2 - edge_inset                 // inside the outside edge
    && abs(p[1]) <= centre_size[1] / 2 - edge_inset
    && (abs(p[0]) >= window_size[0] / 2 + edge_gap                  // outside the window
        || abs(p[1]) >= window_size[1] / 2 + edge_gap)
    && !over_servo(p)
    && nearest(p, board_hole_points) > edge_gap;

edge_n = floor(max(centre_size) / 2 / edge_pitch);
edge_points = [for (i = [-edge_n : edge_n], j = [-edge_n : edge_n])
                  if (edge_ok([i * edge_pitch, j * edge_pitch])) [i * edge_pitch, j * edge_pitch]];

// ---------------------------------------------------------------------
//  the plate
// ---------------------------------------------------------------------

// a straight hole through the whole plate at [x, y]
module through_hole(p, d) {
    translate([p[0], p[1], -1]) cylinder(d = d, h = thick_t + 2);
}

// The plate, servo side on z = 0.
module body_plate() {
    difference() {
        union() {
            linear_extrude(height = thin_t)  at_each_hip() thin_tab_2d();
            linear_extrude(height = thick_t) thick_2d();
        }
        at_each_hip() {
            // case screws, countersunk on the outside
            for (screw = top_corner_screws)    translate(screw) countersunk_hole(thin_t);
            for (screw = bottom_corner_screws) translate(screw) countersunk_hole(thick_t);
            // window over the cable plugs
            translate([cable_window[0], -cable_window[2], -1])
                cube([cable_window[1] - cable_window[0], 2 * cable_window[2], thick_t + 2]);
        }
        // centre window
        translate([0, 0, -1]) linear_extrude(height = thick_t + 2) window_2d();
        // board holes and edge holes
        for (b = boards, sx = [-1, 1], sy = [-1, 1])
            through_hole(b[1] + [sx * b[2][0] / 2, sy * b[2][1] / 2], b[3]);
        for (p = edge_points) through_hole(p, edge_hole);
    }
}

// Both copies in place, for previews. z = 0 is halfway between them, level with the hip servos' centres.
module body_assembled() {
    color("DarkOrange") translate([0, 0, servo_depth / 2]) body_plate();
    color("DarkOrange") mirror([0, 0, 1]) translate([0, 0, servo_depth / 2]) body_plate();
}

body_plate();
