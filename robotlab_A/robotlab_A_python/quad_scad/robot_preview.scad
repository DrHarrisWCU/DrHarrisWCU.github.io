// =====================================================================
//  robot_preview.scad  -  the whole walker: body plates + 4 legs.
//  Nothing here gets printed. Change the angles and press F5.
//  The body size and hip positions come from body_plates.scad.
// =====================================================================

use <body_plates.scad>        // brings in body_assembled() and at_each_leg()
use <leg_assembly_preview.scad>   // brings in one_leg()

hip_angle  = 0;     // the same hip angle on every leg
knee_angle = 60;    // the same knee angle on every leg (positive = leg down)

body_assembled();
at_each_leg() one_leg(hip_angle, knee_angle);
