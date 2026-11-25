"""ICA-609 Type2 card socket -> breadboard breakout (single layer, copper on F.Cu).

v2 (socket lowered): the socket hangs UNDER the PCB (footprint on B.Cu), beside the breadboard, card chip facing up;
its legs come up through the board and are soldered on top. Headers: plastic under the PCB (standard), soldered on top.
Everything below is written in the socket datasheet frame and mirrored left-right onto the board (MIR = -1),
so seen from the top the detect switch is on the left and the tongue/breadboard is on the right,
exactly like the reference drawing (breadboard d1-d5 / g1-g5).

Geometry from the Hamburg ICA-609 Type2 NO datasheet, "Reference dimension for PCB layout"
(component-side view, card goes in from the bottom edge, C5-C8 row on the card-entry side):
  C1..C4  y = 0,      x = 22.08 + 2.54*i
  C5..C8  y = 38.10,  x = 22.08 + 2.54*i
  SW1     (33.51, 0)     SW2 (33.51, 2.54)        10 x drill 1.00
  4 x snap-in holes 3.20 at x = 0 / 58, y = 19.05 -+ 10
  frame 62 x 40 centred on the holes.
Two 1x5 headers 0.5" apart (breadboard rows d and g), symmetric about the socket centre line,
on a tongue that sticks out of the socket's left side (the side away from the detect switch),
so the traces need no crossings:
  J2 (upper, pin1 nearest socket): C1 C2 C3 C4 SW1
  J3 (lower, pin1 nearest socket): C5 C6 C7 C8 SW2
usage: python gen_breakout.py <out_dir>
"""
import json, os, sys, uuid
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import models3d

OUT = sys.argv[1]
NAME = "card609_breakout"
os.makedirs(OUT, exist_ok=True)
U = lambda: str(uuid.uuid4())

# ---------------- geometry (socket-local mm, y down) ----------------
P = 2.54
CPIN = {f"C{i+1}": (22.08 + P * i, 0.0) for i in range(4)}
CPIN.update({f"C{i+5}": (22.08 + P * i, 38.10) for i in range(4)})
CPIN["SW1"] = (33.51, 0.0)
CPIN["SW2"] = (33.51, 2.54)
HOLES = []                               # pure T: the 4 snap-in holes (x 0/58, y 9.05/29.05) are all off the board
FRAME = (-2.0, -0.95, 60.0, 39.05)
YU, YL = 19.05 - 6.35, 19.05 + 6.35          # header rows (breadboard d / g)
XH = -8.5                                    # header pin 1 (nearest socket); breadboard edge ~5 mm past it
COLX = [XH - P * k for k in range(5)]
J2N = ["C1", "C2", "C3", "C4", "SW1"]
J3N = ["C5", "C6", "C7", "C8", "SW2"]
NETS = [""] + [f"C{i}" for i in range(1, 9)] + ["SW1", "SW2"]
NID = {n: i for i, n in enumerate(NETS)}
PN = lambda n: "/" + n if n else ""   # schematic local-label net names

# board outline: socket area + tongue
BX0, BY0, BX1, BY1 = -3.5, -2.7, 61.0, 40.8   # 2.7 mm margin past both pin rows, so the T is symmetric   # socket frame area (only used for reference now)
SX0, SX1 = 19.0, 38.5                        # T: vertical strip under the two pin rows
EX0, EX1, EY0, EY1 = -3.5, 3.5, 6.0, 32.1     # left ear block for the two left snap-in holes
TX0, TY0, TY1 = COLX[-1] - 1.6, YU - 2.2, YL + 2.2
OUTLINE = [(SX0, BY0), (SX1, BY0), (SX1, BY1), (SX0, BY1), (SX0, TY1), (TX0, TY1), (TX0, TY0), (SX0, TY0)]

# lanes between the two header rows, top to bottom
W = 0.4
LANES = ["C1", "C2", "C3", "C4", "SW1", "SW2", "C8", "C7", "C6", "C5"]
lo, hi = YU + 0.85 + 0.25 + W / 2, YL - 0.85 - 0.25 - W / 2
LY = {n: lo + (hi - lo) * i / (len(LANES) - 1) for i, n in enumerate(LANES)}
COL = {n: COLX[i] for i, n in enumerate(J2N)}
COL.update({n: COLX[i] for i, n in enumerate(J3N)})
HROW = {n: YU for n in J2N}
HROW.update({n: YL for n in J3N})


def path(n):
    px, py = CPIN[n]
    pts = [(px, py)]
    if n == "SW1":                      # step left between C4 and SW2, then down
        pts.append((31.6, 0.0))
        px = 31.6
    pts += [(px, LY[n]), (COL[n], LY[n]), (COL[n], HROW[n])]
    return pts


models3d.header(os.path.join(OUT, '3d', 'header_1x05.wrl'), sign=+1, below=True)
OX, OY = 70.0, 50.0                     # place on the sheet
MIR = -1                                # board top view = datasheet view mirrored (socket on the back)
X = lambda v: round(MIR * v + OX, 4)
Y = lambda v: round(v + OY, 4)

# ---------------- PCB ----------------
o = []
a = o.append
a('(kicad_pcb (version 20241229) (generator "pcbnew") (generator_version "9.0")')
a(' (general (thickness 1.6) (legacy_teardrops no))\n (paper "A4")')
a(''' (layers
 (0 "F.Cu" signal) (2 "B.Cu" signal) (13 "F.Paste" user) (15 "B.Paste" user)
 (5 "F.SilkS" user "F.Silkscreen") (7 "B.SilkS" user "B.Silkscreen")
 (1 "F.Mask" user) (3 "B.Mask" user) (17 "Dwgs.User" user "User.Drawings") (19 "Cmts.User" user "User.Comments")
 (25 "Edge.Cuts" user) (27 "Margin" user) (31 "F.CrtYd" user "F.Courtyard") (29 "B.CrtYd" user "B.Courtyard")
 (35 "F.Fab" user) (33 "B.Fab" user))
 (setup (pad_to_mask_clearance 0) (allow_soldermask_bridges_in_footprints no))''')
for n in NETS:
    a(f' (net {NID[n]} "{PN(n)}")')

pts = " ".join(f"(xy {X(x)} {Y(y)})" for x, y in OUTLINE)
a(f' (gr_poly (pts {pts}) (stroke (width 0.1) (type default)) (fill no) (layer "Edge.Cuts") (uuid "{U()}"))')


def net(n):
    return f' (net {NID[n]} "{PN(n)}")' if n else ""


def gtext(t, x, y, layer="F.SilkS", size=0.8, extra=""):
    mir = " (justify mirror)" if layer.startswith("B.") else ""
    a(f' (gr_text "{t}" (at {X(x)} {Y(y)}{extra}) (layer "{layer}") (uuid "{U()}") (effects (font (size {size} {size}) (thickness {size*0.15:.2f})){mir}))')


# J1 socket (on the BACK, legs soldered on top). local coords = board orientation, i.e. mirrored datasheet x
a(f' (footprint "card609:ICA-609_Type2" (layer "B.Cu") (uuid "{U()}") (at {X(0)} {Y(0)})')
a(f'  (property "Reference" "J1" (at {MIR*29} 22 0) (layer "B.Fab") (uuid "{U()}") (effects (font (size 1.5 1.5) (thickness 0.2)) (justify mirror)))')
a(f'  (property "Value" "ICA-609 Type2 NO" (at {MIR*29} 25 0) (layer "B.Fab") (uuid "{U()}") (effects (font (size 1 1) (thickness 0.15)) (justify mirror)))')
a(f'  (property "Footprint" "card609:ICA-609_Type2" (at 0 0 0) (layer "B.Fab") (hide yes) (uuid "{U()}") (effects (font (size 1 1) (thickness 0.15))))')
a('  (attr through_hole)')
fx0, fy0, fx1, fy1 = FRAME
for lay, w, g in (("B.Fab", 0.1, 0),):   # frame overhangs the T board, so outline on Fab only
    a(f'  (fp_rect (start {MIR*(fx0-g)} {fy0-g}) (end {MIR*(fx1+g)} {fy1+g}) (stroke (width {w}) (type default)) (fill no) (layer "{lay}") (uuid "{U()}"))')
a(f'  (fp_rect (start {MIR*(fx0-0.5)} {fy0-0.5}) (end {MIR*(fx1+0.5)} {fy1+0.5}) (stroke (width 0.05) (type default)) (fill no) (layer "B.CrtYd") (uuid "{U()}"))')
# card (85.6 x 54) shown on Fab, fully inserted: ISO contact columns line up with the spring tips (y 15.24 / 22.86),
# so the leading edge sits at y ~4.2 and the card sticks out ~50.5 mm past the frame bottom (datasheet: 50.4 REF)
cx = 29.0
CARD_Y0 = 15.24 - 11.0
CARD_BOX = (cx - 27, cx + 27, CARD_Y0, CARD_Y0 + 85.6)
a(f'  (fp_rect (start {MIR*(cx-27)} {CARD_Y0:.2f}) (end {MIR*(cx+27)} {CARD_Y0+85.6:.2f}) (stroke (width 0.1) (type dash)) (fill no) (layer "B.Fab") (uuid "{U()}"))')
SILK = []                               # socket pin labels go on the TOP silkscreen as board text (footprint is on the back)
for n, (x, y) in CPIN.items():
    shape = "rect" if n == "C1" else "circle"
    a(f'  (pad "{n}" thru_hole {shape} (at {MIR*x} {y}) (size 1.8 1.8) (drill 1.0) (layers "F.Cu" "F.Mask"){net(n)} (pinfunction "{n}") (pintype "passive") (uuid "{U()}"))')
    dy = 2.2 if y < 19 else -2.2
    SILK.append((n, x + 2.6, y + 0.6) if n == "SW2" else (n, x + 2.6, y - 0.9) if n == "SW1" else (n, x, y + dy))
for x, y in HOLES:
    a(f'  (pad "" np_thru_hole circle (at {MIR*x} {y}) (size 3.2 3.2) (drill 3.2) (layers "*.Cu" "*.Mask") (uuid "{U()}"))')
models3d.socket(os.path.join(OUT, '3d', 'ICA-609_socket.wrl'), CPIN, FRAME)
a('  (model "${KIPRJMOD}/3d/ICA-609_socket.wrl" (offset (xyz 0 0 0)) (scale (xyz 1 1 1)) (rotate (xyz 0 0 180)))')
a(' )')

# J2 / J3 headers (plastic on top, long pins through the board into the breadboard, soldered on the back)
for ref, row, names, hval in (("J2", YU, J2N, "Upper row (breadboard d1-d5, pin1=d1)"), ("J3", YL, J3N, "Lower row (breadboard g1-g5, pin1=g1)")):
    a(f' (footprint "card609:PinHeader_1x05_P2.54" (layer "F.Cu") (uuid "{U()}") (at {X(XH)} {Y(row)})')
    ty = -2.0 if row == YU else 2.0
    a(f'  (property "Reference" "{ref}" (at -1.9 {ty} 0) (layer "F.Fab") (uuid "{U()}") (effects (font (size 0.8 0.8) (thickness 0.12))))')
    a(f'  (property "Value" "{hval}" (at 5.08 {ty} 0) (layer "F.Fab") (hide yes) (uuid "{U()}") (effects (font (size 0.8 0.8) (thickness 0.12))))')
    a(f'  (property "Footprint" "card609:PinHeader_1x05_P2.54" (at 0 0 0) (layer "F.Fab") (hide yes) (uuid "{U()}") (effects (font (size 1 1) (thickness 0.15))))')
    a('  (attr through_hole)')
    a(f'  (fp_rect (start -1.27 -1.27) (end {4*P+1.27} 1.27) (stroke (width 0.12) (type default)) (fill no) (layer "F.SilkS") (uuid "{U()}"))')
    a(f'  (fp_rect (start -1.6 -1.6) (end {4*P+1.6} 1.6) (stroke (width 0.05) (type default)) (fill no) (layer "F.CrtYd") (uuid "{U()}"))')
    for k, n in enumerate(names):
        shape = "rect" if k == 0 else "circle"
        a(f'  (pad "{k+1}" thru_hole {shape} (at {P*k} 0) (size 1.7 1.7) (drill 1.0) (layers "F.Cu" "F.Mask"){net(n)} (pinfunction "{n}") (pintype "passive") (uuid "{U()}"))')
    a('  (model "${KIPRJMOD}/3d/header_1x05.wrl" (offset (xyz 0 0 0)) (scale (xyz 1 1 1)) (rotate (xyz 0 0 0)))')
    a(' )')
    # pin names on the tongue, between the rows
    ly = row + (2.35 if row == YU else -2.35)
    for k, n in enumerate(names):
        gtext(n, COLX[k], ly, size=0.8)

gtext("ICA-609 breakout", 11.2, 12.0, size=0.8)
gtext("1 layer, F.Cu", 11.2, 26.2, size=0.8)
for n, x, y in SILK:
    gtext(n, x, y, size=0.8)
cxa = (SX0 + SX1) / 2                   # centre of the T stem
gtext("CARD IN", cxa, 33.0, size=1.2)
a(f' (gr_poly (pts (xy {X(cxa)} {Y(27.6)}) (xy {X(cxa-1.2)} {Y(29.6)}) (xy {X(cxa+1.2)} {Y(29.6)})) (stroke (width 0.15) (type solid)) (fill yes) (layer "F.SilkS") (uuid "{U()}"))')
a(f' (gr_line (start {X(cxa)} {Y(29.6)}) (end {X(cxa)} {Y(31.6)}) (stroke (width 0.3) (type solid)) (layer "F.SilkS") (uuid "{U()}"))')

# traces (F.Cu only)
for n in LANES:
    p = path(n)
    for (x0, y0), (x1, y1) in zip(p, p[1:]):
        a(f' (segment (start {X(x0)} {Y(y0)}) (end {X(x1)} {Y(y1)}) (width {W}) (layer "F.Cu") (net {NID[n]}) (uuid "{U()}"))')
a(')')
open(os.path.join(OUT, NAME + ".kicad_pcb"), "w", encoding="utf-8").write("\n".join(o) + "\n")

# ---------------- schematic ----------------
ROOT = U()
s = []
b = s.append
F = '(effects (font (size 1.27 1.27)))'
FH = '(effects (font (size 1.27 1.27)) (hide yes))'
b(f'(kicad_sch (version 20231120) (generator "eeschema") (generator_version "8.0") (uuid "{ROOT}") (paper "A4")')
b(' (title_block (title "ICA-609 card socket breadboard breakout") (comment 1 "J2/J3 pin 1 = nearest the socket"))')
b(' (lib_symbols')
JPINS = [f"C{i}" for i in range(1, 9)] + ["SW1", "SW2"]
b(f'  (symbol "card609:ICA-609" (pin_names (offset 1.016)) (exclude_from_sim no) (in_bom yes) (on_board yes)')
b(f'   (property "Reference" "J" (at 0 15.24 0) {F}) (property "Value" "ICA-609" (at 0 -15.24 0) {F})')
b(f'   (property "Footprint" "" (at 0 0 0) {FH}) (property "Datasheet" "" (at 0 0 0) {FH})')
b('   (symbol "ICA-609_0_1" (rectangle (start -5.08 13.97) (end 5.08 -13.97) (stroke (width 0.254) (type default)) (fill (type background))))')
b('   (symbol "ICA-609_1_1"')
for i, n in enumerate(JPINS):
    b(f'    (pin passive line (at 7.62 {11.43 - P*i:.2f} 180) (length 2.54) (name "{n}" {F}) (number "{n}" {F}))')
b('   ))')
b(f'  (symbol "card609:Conn_01x05" (pin_names (offset 1.016) (hide yes)) (exclude_from_sim no) (in_bom yes) (on_board yes)')
b(f'   (property "Reference" "J" (at 0 7.62 0) {F}) (property "Value" "Conn_01x05" (at 0 -7.62 0) {F})')
b(f'   (property "Footprint" "" (at 0 0 0) {FH}) (property "Datasheet" "" (at 0 0 0) {FH})')
b('   (symbol "Conn_01x05_0_1" (rectangle (start -1.27 6.35) (end 1.27 -6.35) (stroke (width 0.254) (type default)) (fill (type background))))')
b('   (symbol "Conn_01x05_1_1"')
for i in range(5):
    b(f'    (pin passive line (at -5.08 {5.08 - P*i:.2f} 0) (length 3.81) (name "Pin_{i+1}" {F}) (number "{i+1}" {F}))')
b('   ))')
b(' )')


def place(lib, ref, val, fpn, x, y, pins):
    b(f' (symbol (lib_id "{lib}") (at {x} {y} 0) (unit 1) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no) (uuid "{U()}")')
    b(f'  (property "Reference" "{ref}" (at {x} {y - 16.5 if ref == "J1" else y - 8.9} 0) {F})')
    b(f'  (property "Value" "{val}" (at {x} {y + 16.5 if ref == "J1" else y + 8.9} 0) {F})')
    b(f'  (property "Footprint" "{fpn}" (at {x} {y} 0) {FH})')
    b(f'  (property "Datasheet" "" (at {x} {y} 0) {FH})')
    for p in pins:
        b(f'  (pin "{p}" (uuid "{U()}"))')
    b(f'  (instances (project "{NAME}" (path "/{ROOT}" (reference "{ref}") (unit 1)))))')


def label(n, x, y, right):
    ang, just = (0, "left bottom") if right else (180, "right bottom")
    b(f' (label "{n}" (at {x:.2f} {y:.2f} {ang}) (fields_autoplaced yes) (effects (font (size 1.27 1.27)) (justify {just})) (uuid "{U()}"))')


jx, jy = 63.5, 76.2
place("card609:ICA-609", "J1", "ICA-609 Type2 NO", "card609:ICA-609_Type2", jx, jy, JPINS)
for i, n in enumerate(JPINS):
    label(n, jx + 7.62, jy - (11.43 - P * i), True)
for ref, hy, names, val in (("J2", 63.5, J2N, "Upper row (breadboard d1-d5, pin1=d1)"), ("J3", 93.98, J3N, "Lower row (breadboard g1-g5, pin1=g1)")):
    hx = 139.7
    place("card609:Conn_01x05", ref, val, "card609:PinHeader_1x05_P2.54", hx, hy, [str(i + 1) for i in range(5)])
    for i, n in enumerate(names):
        label(n, hx - 5.08, hy - (5.08 - P * i), False)
b(' (sheet_instances (path "/" (page "1")))')
b(')')
open(os.path.join(OUT, NAME + ".kicad_sch"), "w", encoding="utf-8").write("\n".join(s) + "\n")

# ---------------- project ----------------
pro = {"meta": {"filename": NAME + ".kicad_pro", "version": 1},
       "board": {"design_settings": {"rules": {"min_clearance": 0.2, "min_track_width": 0.2,
                                               "min_copper_edge_clearance": 0.3}}},
       "sheets": [[ROOT, "Root"]]}
open(os.path.join(OUT, NAME + ".kicad_pro"), "w", encoding="utf-8").write(json.dumps(pro, indent=2))
for n in LANES:
    print(n, [(round(x, 2), round(y, 2)) for x, y in path(n)])
