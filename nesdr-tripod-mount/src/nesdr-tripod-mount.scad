// NESDR SMArt v5 tripod holder (parametric, rounded version)
// Holds the RTL-SDR stick upright (USB plug down, SMA + whip on top)
// on a camera tripod with a 1/4"-20 screw.
// Print flat as oriented (foot on the bed), PETG, no supports, 4 walls.

/* [Mounting] */
// "selftap" = round hole the tripod screw threads into; "nut" = captive 1/4"-20 UNC nut slid in from the side; "insert" = heat-set 1/4"-20 brass insert pressed in from below
mount = "selftap"; // [selftap, nut, insert]
selftap_d = 5.4;   // self-tapping hole diameter
insert_hole_d = 7.6; // heat-set insert pocket (insert OD minus ~0.4)
insert_l = 8.5;      // insert length + 0.5
chamfer = 1.0;     // entry chamfer at the bottom of the hole

/* [Stick] */
stick_w = 16.9;
stick_t = 14.2;
clearance = 0.4;   // per side

/* [Sleeve] */
wall = 2.4;
sleeve_h = 50;
offset_x = 45;     // sleeve centre distance from the tripod screw
lip = 2.4;         // bottom lip the stick rests on
usb_w = 13.4;      // opening in the lip for the USB plug
usb_t = 11.0;
vent_w = 8;        // stadium-shaped vent windows on both wide faces
vent_z0 = 10;
vent_z1 = 40;

/* [Foot and arm] */
foot = 30;
foot_h = 14;
arm_w = 12;
arm_h = 12;

/* [Rounding] */
r_foot = 4.0;      // vertical corner radius of the foot
r_sleeve = 3.5;    // vertical corner radius of the sleeve
r_top = 2.0;       // top edge rounding

/* [Nut (mount = nut)] */
nut_af = 11.11;
nut_t = 5.56;
nut_z = 4.0;
bolt_d = 6.8;

$fn = 64;
W = stick_w + 2*clearance;
T = stick_t + 2*clearance;
OW = W + 2*wall;
OT = T + 2*wall;

// rounded block: flat bottom at z = 0, vertical corner radius rv, rounded top edges (rt)
module rblock(cx, cy, sx, sy, h, rv, rt) {
  hull() for (ix = [-1, 1], iy = [-1, 1])
    translate([cx + ix*(sx/2 - rv), cy + iy*(sy/2 - rv), 0]) {
      cylinder(r = rv, h = h - rt);
      translate([0, 0, h - rt]) scale([1, 1, rt/rv]) sphere(r = rv);
    }
}

// rounded rectangle prism for cuts (no top rounding)
module rcut(cx, cy, sx, sy, z0, h, r) {
  hull() for (ix = [-1, 1], iy = [-1, 1])
    translate([cx + ix*(sx/2 - r), cy + iy*(sy/2 - r), z0]) cylinder(r = r, h = h);
}

module body() {
  rblock(0, 0, foot, foot, foot_h, r_foot, r_top);
  // arm, overlapping into foot and sleeve
  rblock((foot/2 + offset_x)/2, 0, offset_x - foot/2 + 4, arm_w, arm_h, 3, r_top);
  rblock(offset_x, 0, OW, OT, sleeve_h, r_sleeve, 1.5);
}

module cuts() {
  rcut(offset_x, 0, W, T, lip, sleeve_h, 1.2);                 // sleeve cavity
  rcut(offset_x, 0, usb_w, usb_t, -1, lip + 2, 1.5);           // USB opening
  // vent windows through both wide faces
  hull() for (zz = [vent_z0 + vent_w/2, vent_z1 - vent_w/2])
    translate([offset_x, 0, zz]) rotate([90, 0, 0]) cylinder(d = vent_w, h = OT + 4, center = true);
  if (mount == "nut") {
    sw = nut_af + 0.5; sh = nut_t + 0.5;
    translate([-foot/2 - 1, -sw/2, nut_z]) cube([foot/2 + 1 + nut_af*0.58 + 0.2, sw, sh]);
    translate([0, 0, -1]) cylinder(d = bolt_d, h = foot_h + 2);
  } else if (mount == "insert") {
    // heat-set insert pocket from the bottom, clearance hole above it
    translate([0, 0, -1]) cylinder(d = insert_hole_d, h = insert_l + 1);
    translate([0, 0, -0.01]) cylinder(d1 = insert_hole_d + 1.2, d2 = insert_hole_d, h = 0.6);
    translate([0, 0, -1]) cylinder(d = bolt_d - 0.2, h = foot_h + 2);
  } else {
    translate([0, 0, -1]) cylinder(d = selftap_d, h = foot_h + 2);
    translate([0, 0, -0.01]) cylinder(d1 = selftap_d + 2*chamfer, d2 = selftap_d, h = chamfer);
  }
}

difference() { body(); cuts(); }
