"""Card-reader PCB v8 (KiCad .kicad_pcb), same geometry and wiring as 讀卡機Layout_v8 (gen_layout_card8.py).
Perfboard 11 x 24 holes. U1 nRF52840 module (13 pins per side) on the front, USB-C down.
J1 card socket on the BACK, its 8 legs in c8-c11 at rows 24 and 8. Detect switch legs just off the right edge.
OK wires (front) are drawn on F.SilkS; pads carry nets so KiCad shows the connections as ratsnest.
usage: python gen_pcb_card8.py out.kicad_pcb"""
import runpy, sys, uuid, tempfile, os

OUT = sys.argv[1]
tmp = os.path.join(tempfile.gettempdir(), "_l8.svg")
sys.argv = ["x", tmp]
L = runpy.run_path(os.path.join(os.path.dirname(os.path.abspath(__file__)), "gen_layout_card8.py"))
NC, NR, TOPH, BOTH = L["NC"], L["NR"], L["TOPH"], L["BOTH"]
SWX, SW1R, SW2R, WIRES = L["SWX"], L["SW1R"], L["SW2R"], L["WIRES"]
SOCK_W, SOCK_H, BX, RTOP = L["SOCK_W"], L["SOCK_H"], L["BX"], L["RTOP"]

P = 2.54
OX, OY = 100.0, 100.0
x = lambda c: round(OX + (c - 1) * P, 3)
y = lambda r: round(OY + (NR - r) * P, 3)
U = lambda: str(uuid.uuid4())

NETS = ["", "GND", "VCC_CARD", "RST", "CLK", "IO", "DET", "VBAT"]
NID = {n: i for i, n in enumerate(NETS)}
# module pins, rotated 180 deg: left column c1, right column c7, row 0 = B+/B- (hangs below the board edge)
NL_ = ["B+", "RAW", "GND", "RST", "VCC", "P0.31", "P0.29", "P0.02", "P1.15", "P1.13", "P1.11", "P0.10", "P0.09"]
NR_ = ["B-", "P0.06", "P0.08", "GND", "GND", "P0.17", "P0.20", "P0.22", "P0.24", "P1.00", "P0.11", "P1.04", "P1.06"]
UNET = {"GND": "GND", "B-": "GND", "VCC": "VCC_CARD", "P0.24": "RST", "P0.17": "CLK",
        "P0.20": "IO", "P0.22": "IO", "P1.00": "DET", "RAW": "VBAT"}
JNET = {"C1": "VCC_CARD", "C2": "RST", "C3": "CLK", "C5": "GND", "C7": "IO", "SW1": "DET", "SW2": "GND"}

o = []; a = o.append

# ---------- simple VRML 3D models (KiCad: 1 VRML unit = 2.54 mm; model y is up, board y is down) ----------
MDIR = os.path.dirname(os.path.abspath(OUT))


def wrl(name, boxes):
    """boxes: (x0, x1, y0, y1, z0, z1, rgb) in mm, x/y in board-local coords relative to the footprint origin."""
    out = ["#VRML V2.0 utf8"]
    for x0_, x1_, y0_, y1_, z0, z1, rgb in boxes:
        X0, X1 = sorted((x0_ / P, x1_ / P)); Y0, Y1 = sorted((-y0_ / P, -y1_ / P)); Z0, Z1 = sorted((z0 / P, z1 / P))
        v = [(X0, Y0, Z0), (X1, Y0, Z0), (X1, Y1, Z0), (X0, Y1, Z0), (X0, Y0, Z1), (X1, Y0, Z1), (X1, Y1, Z1), (X0, Y1, Z1)]
        pts = ", ".join(f"{a_:.4f} {b_:.4f} {c_:.4f}" for a_, b_, c_ in v)
        out.append("Shape { appearance Appearance { material Material { diffuseColor %.3f %.3f %.3f specularColor 0.2 0.2 0.2 shininess 0.3 } }"
                   % rgb)
        out.append("  geometry IndexedFaceSet { coord Coordinate { point [ %s ] }" % pts)
        out.append("    coordIndex [ 0 3 2 1 -1 4 5 6 7 -1 0 1 5 4 -1 1 2 6 5 -1 2 3 7 6 -1 3 0 4 7 -1 ] } }")
    path = os.path.join(MDIR, name)
    open(path, "w", encoding="utf-8").write("\n".join(out))
    return path.replace("\\", "/")


BLACK, GOLD, STEEL, CHIP, GREY, PCBB = (0.05, 0.05, 0.06), (0.85, 0.68, 0.25), (0.75, 0.75, 0.78), (0.12, 0.12, 0.14), (0.25, 0.26, 0.28), (0.08, 0.08, 0.10)
lx = lambda c: (c - 1) * P            # board-local x of column c (footprint origin = c1, r24)
ly = lambda r: (NR - r) * P
# module: 2.5 mm header plastic, 1.0 mm module PCB, parts on top
HZ = 2.5
mb = [(lx(0.45), lx(7.55), ly(12.95), ly(-0.75), HZ, HZ + 1.0, PCBB),
      (lx(2.4), lx(5.6), ly(0.6), ly(-1.75), HZ + 1.0, HZ + 4.2, STEEL),          # USB-C, sticks out past the board edge
      (lx(3.0), lx(5.9), ly(7.4), ly(4.4), HZ + 1.0, HZ + 1.85, CHIP),            # nRF52840
      (lx(1.6), lx(2.6), ly(9.4), ly(8.8), HZ + 1.0, HZ + 1.6, STEEL),            # crystal
      (lx(2.3), lx(5.7), ly(12.75), ly(11.9), HZ + 1.0, HZ + 1.05, (0.55, 0.12, 0.12))]   # antenna area
for col in (1, 7):
    mb.append((lx(col) - 1.25, lx(col) + 1.25, ly(12.5), ly(-0.5), 0, HZ, BLACK))   # header plastic
    for i in range(13):
        mb.append((lx(col) - 0.32, lx(col) + 0.32, ly(i) - 0.32, ly(i) + 0.32, -2.8, HZ + 1.6, GOLD))
M_U1 = wrl("model_U1_nRF52840_SuperMini.wrl", mb)


def net(n):
    return f' (net {NID[n]} "{n}")' if n else ""


def txt(t, cx, cy, layer, size=1.0, mirror=False):
    j = " (justify mirror)" if mirror else ""
    a(f' (gr_text "{t}" (at {cx:.3f} {cy:.3f}) (layer "{layer}") (uuid "{U()}") (effects (font (size {size} {size}) (thickness {size*0.15:.2f})){j}))')


a('(kicad_pcb (version 20241229) (generator "pcbnew") (generator_version "9.0")')
a(' (general (thickness 1.6) (legacy_teardrops no))\n (paper "A4")')
a(''' (layers
 (0 "F.Cu" signal) (2 "B.Cu" signal) (9 "F.Adhes" user "F.Adhesive") (11 "B.Adhes" user "B.Adhesive")
 (13 "F.Paste" user) (15 "B.Paste" user) (5 "F.SilkS" user "F.Silkscreen") (7 "B.SilkS" user "B.Silkscreen")
 (1 "F.Mask" user) (3 "B.Mask" user) (17 "Dwgs.User" user "User.Drawings") (19 "Cmts.User" user "User.Comments")
 (25 "Edge.Cuts" user) (27 "Margin" user) (31 "F.CrtYd" user "F.Courtyard") (29 "B.CrtYd" user "B.Courtyard")
 (35 "F.Fab" user) (33 "B.Fab" user))
 (setup (pad_to_mask_clearance 0) (allow_soldermask_bridges_in_footprints no))''')
for i, n in enumerate(NETS):
    a(f' (net {i} "{n}")')

# ---- board outline ----
x0, x1, y0, y1 = x(0.5), x(NC + 0.5), y(NR + 0.5), y(0.5)
a(f' (gr_rect (start {x0} {y0}) (end {x1} {y1}) (stroke (width 0.1) (type default)) (fill no) (layer "Edge.Cuts") (uuid "{U()}"))')

used = set()
# ---- U1 module (front) ----
pin = 0
fp = []
for col, names in ((7, NR_), (1, NL_)):
    for i, nm in enumerate(names):
        pin += 1
        used.add((col, i))
        shape = "rect" if pin == 1 else "circle"
        fp.append(f'  (pad "{pin}" thru_hole {shape} (at {x(col)-OX:.3f} {y(i)-OY:.3f}) (size 1.5 1.5) (drill 1.0) (layers "*.Cu" "*.Mask"){net(UNET.get(nm, ""))} (pinfunction "{nm}") (uuid "{U()}"))')
a(f' (footprint "card:SuperMini_nRF52840_13x2" (layer "F.Cu") (uuid "{U()}") (at {OX} {OY})')
a(f'  (property "Reference" "U1" (at {x(4)-OX:.3f} {y(10.3)-OY:.3f} 0) (layer "F.SilkS") (uuid "{U()}") (effects (font (size 1 1) (thickness 0.15))))')
a(f'  (property "Value" "nRF52840 SuperMini (nice!nano)" (at {x(4)-OX:.3f} {y(9.5)-OY:.3f} 0) (layer "F.Fab") (hide yes) (uuid "{U()}") (effects (font (size 0.8 0.8) (thickness 0.12))))')
a('  (attr through_hole)')
bx0, bx1, by0, by1 = x(0.45) - OX, x(7.55) - OX, y(12.95) - OY, y(-0.75) - OY
for lay in ("F.Fab", "F.SilkS"):
    a(f'  (fp_rect (start {bx0:.3f} {by0:.3f}) (end {bx1:.3f} {by1:.3f}) (stroke (width 0.15) (type default)) (fill no) (layer "{lay}") (uuid "{U()}"))')
a(f'  (fp_rect (start {x(2.5)-OX:.3f} {y(0.35)-OY:.3f}) (end {x(5.5)-OX:.3f} {y(-1.6)-OY:.3f}) (stroke (width 0.12) (type default)) (fill no) (layer "F.SilkS") (uuid "{U()}"))')
a(f'  (fp_text user "USB-C" (at {x(4)-OX:.3f} {y(-0.75)-OY:.3f} 0) (layer "F.SilkS") (uuid "{U()}") (effects (font (size 0.8 0.8) (thickness 0.12))))')
a(f'  (fp_rect (start {x(2.3)-OX:.3f} {y(12.75)-OY:.3f}) (end {x(5.7)-OX:.3f} {y(11.9)-OY:.3f}) (stroke (width 0.1) (type dash)) (fill no) (layer "F.Fab") (uuid "{U()}"))')
for i in range(13):
    a(f'  (fp_text user "{NL_[i]}" (at {x(1.5)-OX:.3f} {y(i)-OY:.3f} 0) (layer "F.Fab") (uuid "{U()}") (effects (font (size 0.6 0.6) (thickness 0.1)) (justify left)))')
    a(f'  (fp_text user "{NR_[i]}" (at {x(6.5)-OX:.3f} {y(i)-OY:.3f} 0) (layer "F.Fab") (uuid "{U()}") (effects (font (size 0.6 0.6) (thickness 0.1)) (justify right)))')
o.extend(fp)
a(f'  (model "{M_U1}" (offset (xyz 0 0 0)) (scale (xyz 1 1 1)) (rotate (xyz 0 0 0)))')
a(' )')

# ---- J1 card socket (back side; legs into the board, detect switch legs off-board) ----
a(f' (footprint "card:ISO7816_socket_62x42" (layer "B.Cu") (uuid "{U()}") (at {OX} {OY})')
sx0 = x(0.5) - BX - OX
sy0 = y(RTOP) - OY
a(f'  (property "Reference" "J1" (at {sx0 + 40:.3f} {sy0 + 8:.3f} 0) (layer "B.SilkS") (uuid "{U()}") (effects (font (size 1.5 1.5) (thickness 0.2)) (justify mirror)))')
a(f'  (property "Value" "ISO7816 card socket (back side, slot at top)" (at {sx0 + 40:.3f} {sy0 + 11:.3f} 0) (layer "B.Fab") (uuid "{U()}") (effects (font (size 1 1) (thickness 0.15)) (justify mirror)))')
a('  (attr through_hole)')
for lay in ("B.Fab", "B.SilkS"):
    a(f'  (fp_rect (start {sx0:.3f} {sy0:.3f}) (end {sx0 + SOCK_W:.3f} {sy0 + SOCK_H:.3f}) (stroke (width 0.15) (type default)) (fill no) (layer "{lay}") (uuid "{U()}"))')
a(f'  (fp_text user "card slot (top edge)" (at {sx0 + 40:.3f} {sy0 + 2:.3f} 0) (layer "B.Fab") (uuid "{U()}") (effects (font (size 1 1) (thickness 0.15)) (justify mirror)))')
for name, (c, r) in list(TOPH.items()) + list(BOTH.items()):
    used.add((c, r))
    a(f'  (pad "{name}" thru_hole circle (at {x(c)-OX:.3f} {y(r)-OY:.3f}) (size 1.5 1.5) (drill 1.0) (layers "*.Cu" "*.Mask"){net(JNET.get(name, ""))} (uuid "{U()}"))')
SH = 2.8   # socket body height (estimate)
sb = [(sx0, sx0 + SOCK_W, sy0, sy0 + SOCK_H, 0.0, SH, GREY),
      (sx0 + 2, sx0 + SOCK_W - 2, sy0 + 0.3, sy0 + 1.6, SH, SH + 0.05, BLACK)]            # card slot mark
for name, (c, r) in list(TOPH.items()) + list(BOTH.items()):
    sb.append((lx(c) - 0.3, lx(c) + 0.3, ly(r) - 0.2, ly(r) + 0.2, -2.0, 0.5, GOLD))   # legs through the board
for r in (SW1R, SW2R):
    sb.append((lx(SWX) - 0.3, lx(SWX) + 0.3, ly(r) - 0.2, ly(r) + 0.2, -2.0, 0.5, STEEL))
sb = [(b[0], b[1], -b[3], -b[2]) + b[4:] for b in sb]   # B.Cu footprint: KiCad flips the model top/bottom (y -> -y, z -> -z)
M_J1 = wrl("model_J1_card_socket.wrl", sb)
a(f'  (model "{M_J1}" (offset (xyz 0 0 0)) (scale (xyz 1 1 1)) (rotate (xyz 0 0 0)))')
for name, r in (("SW1", SW1R), ("SW2", SW2R)):
    a(f'  (pad "{name}" thru_hole oval (at {x(SWX)-OX:.3f} {y(r)-OY:.3f}) (size 1.8 1.3) (drill 0.8) (layers "*.Cu" "*.Mask"){net(JNET[name])} (uuid "{U()}"))')
a(' )')

# ---- perfboard holes (all the rest) ----
a(f' (footprint "card:Perfboard_{NC}x{NR}" (layer "F.Cu") (uuid "{U()}") (at {OX} {OY})')
a(f'  (property "Reference" "PB1" (at 0 -3 0) (layer "F.SilkS") (hide yes) (uuid "{U()}") (effects (font (size 1 1) (thickness 0.15))))')
a(f'  (property "Value" "perfboard {NC}x{NR}" (at 0 -5 0) (layer "F.Fab") (hide yes) (uuid "{U()}") (effects (font (size 1 1) (thickness 0.15))))')
a('  (attr exclude_from_pos_files exclude_from_bom)')
for c in range(1, NC + 1):
    for r in range(1, NR + 1):
        if (c, r) not in used and not (2 <= c <= 6 and r <= 12):   # holes under the module are covered, not drawn
            a(f'  (pad "" thru_hole circle (at {x(c)-OX:.3f} {y(r)-OY:.3f}) (size 1.5 1.5) (drill 1.0) (layers "*.Cu" "*.Mask") (uuid "{U()}"))')
a(' )')

# ---- battery outline (front, taped) ----
a(f' (gr_rect (start {x(7.85)} {y(8.0)}) (end {x(13.0)} {y(-0.6)}) (stroke (width 0.15) (type dash)) (fill no) (layer "F.Fab") (uuid "{U()}"))')
txt("BT1 battery (tape)", x(10.4), y(-0.1), "F.Fab", 0.8)

# ---- OK wires on the front (silkscreen drawing) + labels ----
for no, cl, path, s0, s1, use, dash in WIRES:
    for (c0, r0), (c1, r1) in zip(path, path[1:]):
        a(f' (gr_line (start {x(c0)} {y(r0)}) (end {x(c1)} {y(r1)}) (stroke (width 0.4) (type {"dash" if dash else "solid"})) (layer "F.SilkS") (uuid "{U()}"))')
LBL = {"K1": (4.0, 4.85), "K2": (9.5, 15.0), "K3": (8.5, 7.25), "K4": (10.45, 5.0), "K5": (11.0, 15.0), "K6": (6.1, 6.5),
       "K8": (11.3, 9.8), "K9": (11.3, 3.85), "K11": (4.0, 1.05), "K12": (4.0, 1.9)}
for k, (c, r) in LBL.items():
    txt(k, x(c), y(r), "F.SilkS", 0.8)
for c in range(1, NC + 1):
    txt(str(c), x(c), y(NR + 0.5) - 0.9, "Cmts.User", 0.7)
for r in range(1, NR + 1):
    txt(str(r), x(0.5) - 1.0, y(r), "Cmts.User", 0.7)
txt("讀卡機 PCB v8（正面俯視，插卡口在上）洞洞板 11x24 孔 27.9 x 61.0 mm", x(0.5) + 28, y(NR + 0.5) - 3.5, "Cmts.User", 1.2)
a(")")
open(OUT, "w", encoding="utf-8").write("\n".join(o))
print("ok", OUT)
