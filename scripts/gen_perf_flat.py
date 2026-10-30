"""Perfboard product layout (option A): both dev boards on top, battery + point-to-point wiring
underneath, inside a 3D-printable enclosure. Writes VRML models + KiCad boards for 3D renders.
Perfboard holes are addressed as (c, r): column 1-23 left->right, row 1-18 bottom->top (top view)."""
import sys, os, math, uuid
from collections import defaultdict

OUT = sys.argv[1]
P = 2.54
NC, NR = 23, 18
HX = lambda c: (c - 12) * P
HY = lambda r: (r - 9.5) * P
BW, BH = NC * P / 2, NR * P / 2          # half board size: 29.21 x 22.86
T = 1.6                                  # perfboard thickness; top surface z=0
GAP = 1.0                                # low-profile module stand-off (header plastic removed)
BAT_GAP = 0.8                            # battery below board bottom (on Kapton tape)

MAT = {
    "pcb": ((0.07, 0.07, 0.08), 0), "gold": ((0.85, 0.66, 0.28), 0), "silver": ((0.8, 0.8, 0.82), 0),
    "solder": ((0.72, 0.73, 0.75), 0), "chip": ((0.13, 0.13, 0.14), 0), "gpcb": ((0.08, 0.5, 0.2), 0),
    "redpart": ((0.8, 0.12, 0.12), 0), "cap": ((0.15, 0.15, 0.15), 0), "led": ((0.95, 0.95, 0.95), 0),
    "w_red": ((0.88, 0.1, 0.1), 0), "w_blk": ((0.08, 0.08, 0.08), 0), "w_yel": ((0.97, 0.82, 0.08), 0),
    "w_org": ((0.97, 0.45, 0.1), 0), "lead": ((0.7, 0.7, 0.72), 0), "res": ((0.86, 0.76, 0.56), 0),
    "band": ((0.45, 0.25, 0.1), 0), "lipo": ((0.82, 0.82, 0.84), 0), "kapton": ((0.92, 0.58, 0.12), 0.1),
    "case": ((0.75, 0.8, 0.88), 0.72), "shell": ((0.86, 0.87, 0.9), 0), "shell_in": ((0.7, 0.72, 0.76), 0),
}

class Model:
    def __init__(self):
        self.mesh = defaultdict(lambda: ([], []))
    def face(self, mat, pts):
        v, f = self.mesh[mat]; b = len(v); v.extend(pts); f.append(list(range(b, b + len(pts))))
    def prism(self, mat, poly, z0, z1):
        self.face(mat, [(x, y, z1) for x, y in poly]); self.face(mat, [(x, y, z0) for x, y in reversed(poly)])
        for i in range(len(poly)):
            (x0, y0), (x1, y1) = poly[i], poly[(i + 1) % len(poly)]
            self.face(mat, [(x0, y0, z0), (x1, y1, z0), (x1, y1, z1), (x0, y0, z1)])
    def box(self, mat, x0, y0, z0, x1, y1, z1):
        self.prism(mat, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], min(z0, z1), max(z0, z1))
    def rbox(self, mat, cx, cy, w, h, ang, z0, z1):
        c, s = math.cos(math.radians(ang)), math.sin(math.radians(ang))
        self.prism(mat, [(cx + x*c - y*s, cy + x*s + y*c) for x, y in [(-w/2, -h/2), (w/2, -h/2), (w/2, h/2), (-w/2, h/2)]], z0, z1)
    def disk(self, mat, cx, cy, r, z0, z1, n=12):
        self.prism(mat, [(cx + r*math.cos(2*math.pi*i/n), cy + r*math.sin(2*math.pi*i/n)) for i in range(n)], min(z0, z1), max(z0, z1))
    def tube(self, mat, pts, r=0.35, n=8, smooth=True):
        if smooth:
            pts = chaikin(pts)
        tans = [norm(sub(pts[min(i+1, len(pts)-1)], pts[max(i-1, 0)])) for i in range(len(pts))]
        u = norm(cross(tans[0], (0, 0, 1) if abs(tans[0][2]) < 0.9 else (1, 0, 0)))
        rings = []
        for p, t in zip(pts, tans):
            u0 = sub(u, mul(t, dot(u, t))); u = norm(u0) if dot(u0, u0) > 1e-6 else norm(cross(t, (0, 0, 1) if abs(t[2]) < 0.9 else (1, 0, 0))); w = cross(t, u)
            rings.append([add(p, add(mul(u, r*math.cos(2*math.pi*k/n)), mul(w, r*math.sin(2*math.pi*k/n)))) for k in range(n)])
        for a, b in zip(rings, rings[1:]):
            for k in range(n):
                self.face(mat, [a[k], a[(k+1) % n], b[(k+1) % n], b[k]])
    def write(self, path):
        with open(path, "w", encoding="utf-8") as f:
            f.write("#VRML V2.0 utf8\n")
            for mat, (v, faces) in self.mesh.items():
                col, tr = MAT[mat]
                pts = ",\n".join(f"{x/P:.4f} {y/P:.4f} {z/P:.4f}" for x, y, z in v)
                idx = ",".join(",".join(map(str, fc)) + ",-1" for fc in faces)
                f.write(f"Shape {{ appearance Appearance {{ material Material {{ diffuseColor {col[0]} {col[1]} {col[2]} "
                        f"specularColor 0.25 0.25 0.25 shininess 0.3 transparency {tr} }} }}\n geometry IndexedFaceSet {{ solid FALSE creaseAngle 0.9\n"
                        f"  coord Coordinate {{ point [\n{pts}\n ] }}\n  coordIndex [ {idx} ] }} }}\n")

def sub(a, b): return tuple(p - q for p, q in zip(a, b))
def add(a, b): return tuple(p + q for p, q in zip(a, b))
def mul(a, k): return tuple(p * k for p in a)
def dot(a, b): return sum(p * q for p, q in zip(a, b))
def cross(a, b): return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])
def norm(a):
    l = math.sqrt(dot(a, a)) or 1
    return mul(a, 1 / l)
def chaikin(pts, it=3):
    for _ in range(it):
        out = [pts[0]]
        for a, b in zip(pts, pts[1:]):
            out += [add(mul(a, .75), mul(b, .25)), add(mul(a, .25), mul(b, .75))]
        out.append(pts[-1]); pts = out
    return pts

asm, bat, case, case_open, case_closed = Model(), Model(), Model(), Model(), Model()
ZB = -T                                   # board bottom surface
used_holes = []

def pin(c, r, top=GAP + T + 0.3):
    """through-hole pin soldered from the bottom (trimmed 1 mm below the board)"""
    x, y = HX(c), HY(r)
    asm.box("gold", x - 0.32, y - 0.32, ZB - 1.0, x + 0.32, y + 0.32, top)
    used_holes.append((c, r))

# ---------- U1 nice!nano (top side, USB-C toward -X) ----------
z0, z1 = GAP, GAP + T
for c in range(2, 14):
    for r in (2, 8):
        pin(c, r)
        asm.disk("gold", HX(c), HY(r), 0.85, z1, z1 + 0.05, 10)
cx, cy = (HX(2) + HX(13)) / 2, (HY(2) + HY(8)) / 2
asm.box("pcb", cx - 16.65, cy - 9, z0, cx + 16.65, cy + 9, z1)
asm.box("silver", cx - 16.65 - 1.5, cy - 4.5, z1, cx - 16.65 + 7, cy + 4.5, z1 + 3.2)       # USB-C
asm.rbox("chip", cx + 1.5, cy, 7, 7, 45, z1, z1 + 0.9)
asm.box("silver", cx - 6.5, cy + 4.5, z1, cx - 3.5, cy + 6.5, z1 + 1.0)
asm.box("redpart", cx + 12.2, cy - 1.5, z1, cx + 13.8, cy + 2.5, z1 + 0.6)                # far-end part (antenna side)
for k in range(3):
    asm.disk("gold", cx + 9.8, cy + 2.6 - k * 2.6, 0.8, z1, z1 + 0.05)
NANO = dict(cx=cx, cy=cy)

# ---------- U2 BlackPill (top side, USB-C toward +X; header 2 on row 17, header 1 on row 11) ----------
# header 2 (row 17): B12 at c22 (USB end) ... PA9 c17 ... 5V c5, G c4, 3.3 c3
# header 1 (row 11): 5V at c22 (USB end), G c21, 3.3 c20 ... VB c3
for c in range(3, 23):
    for r in (11, 17):
        pin(c, r)
        asm.disk("gold", HX(c), HY(r), 0.85, z1, z1 + 0.05, 10)
cx, cy = (HX(3) + HX(22)) / 2, (HY(11) + HY(17)) / 2
asm.box("pcb", cx - 26.5, cy - 10.5, z0, cx + 26.5, cy + 10.5, z1)
asm.box("silver", cx + 26.5 - 7, cy - 4.5, z1, cx + 26.5 + 1.5, cy + 4.5, z1 + 3.2)        # USB-C
asm.rbox("chip", cx + 1.0, cy, 7, 7, 45, z1, z1 + 0.9)
for bx, by in ((cx - 12.0, cy + 3.0), (cx + 13.5, cy + 4.0), (cx + 13.5, cy - 2.5)):          # KEY, BOOT0, NRST
    asm.box("silver", bx - 2.2, by - 1.8, z1, bx + 2.2, by + 1.8, z1 + 1.6)
    asm.disk("cap", bx, by, 1.0, z1 + 1.6, z1 + 2.3)
asm.box("led", cx - 12.5, cy - 6.0, z1, cx - 11.3, cy - 5.2, z1 + 0.5)
for k in range(4):
    asm.disk("gold", cx - 20.5, cy + 3.8 - k * 2.54, 0.75, z1, z1 + 0.05)                      # SWD pads (unused)
BP = dict(cx=cx, cy=cy)

# ---------- U3 DMC2038LVT on SOT-23-6 adapter (top side; row 6: G1 c19, S2 c20, G2 c21 / row 3: D1 c19, S1 c20, D2 c21) ----------
ua = GAP + 1.2
for c in (19, 20, 21):
    for r in (3, 6):
        pin(c, r, ua + 0.3)
ux, uy = HX(20), (HY(3) + HY(6)) / 2
asm.box("gpcb", ux - 5.1, uy - 5.7, GAP, ux + 5.1, uy + 5.7, ua)
for c in (19, 20, 21):
    for r in (3, 6):
        asm.disk("gold", HX(c), HY(r), 0.9, ua, ua + 0.3)
asm.box("chip", ux - 1.45, uy - 0.8, ua + 0.1, ux + 1.45, uy + 0.8, ua + 1.2)
for dx in (-0.95, 0, 0.95):                                                                       # G1 / S2 / G2 toward row 6
    asm.box("silver", ux + dx - 0.2, uy + 0.8, ua, ux + dx + 0.2, uy + 1.5, ua + 0.25)
for dx in (-0.95, 0, 0.95):                                                                       # D1 / S1 / D2 toward row 3
    asm.box("silver", ux + dx - 0.2, uy - 1.5, ua, ux + dx + 0.2, uy - 0.8, ua + 0.25)
asm.disk("gold", ux - 0.95, uy + 0.35, 0.15, ua + 1.2, ua + 1.22, 8)
zt = ua + 0.35                                                                                    # G1 <-> D2 link on the adapter
asm.tube("w_red", [(HX(19), HY(6), zt), (HX(19), HY(6) + 1.4, zt + 0.8), (HX(20), HY(6) + 2.4, zt + 1.0), (HX(21) + 1.8, HY(6) + 1.6, zt + 1.0),
                   (HX(21) + 2.9, uy, zt + 1.0), (HX(21) + 1.8, HY(3) - 1.4, zt + 0.8), (HX(21), HY(3), zt)], 0.32)

# ---------- R1 (top side, row 1, cols 19-22) ----------
rz = 1.0
asm.tube("res", [(HX(19.9), HY(1), rz), (HX(21.1), HY(1), rz)], 0.95, smooth=False)
for dx in (-0.4, 0.4):
    asm.tube("band", [(HX(20.5) + dx - 0.15, HY(1), rz), (HX(20.5) + dx + 0.15, HY(1), rz)], 1.0, smooth=False)
for c, d in ((19, 1), (22, -1)):
    asm.tube("lead", [(HX(c), HY(1), ZB - 1.0), (HX(c), HY(1), rz), (HX(c) + d * 1.6, HY(1), rz)], 0.25, smooth=False)
    used_holes.append((c, 1))

# ---------- solder joints on the bottom ----------
for c, r in set(used_holes):
    asm.disk("solder", HX(c), HY(r), 0.95, ZB, ZB - 0.45, 10)

# ---------- point-to-point wires on the bottom side ----------
ZW = ZB - 0.35
def bwire(mat, pts, z=ZW):
    p3 = [(HX(c), HY(r), z) for c, r in pts]
    p3 = [(p3[0][0], p3[0][1], ZB - 0.2)] + p3 + [(p3[-1][0], p3[-1][1], ZB - 0.2)]
    asm.tube(mat, p3, 0.32)
WIRES = [  # (no, colour, from, to, path in hole units, note)
    ("W1", "w_red", "BAT +", "U1 RAW (c2,r8)", None, "電池正極"),
    ("W2", "w_blk", "BAT −", "U1 GND (c3,r8)", None, "電池負極（改接 GND）"),
    ("W3", "w_yel", "U2 PA9 (c17,r17)", "U1 P0.08 (c3,r2)", [(17, 17), (17.5, 16.5), (17.5, 14), (4.5, 14), (4.5, 2.5), (3, 2.5), (3, 2)], "UART：BlackPill TX → nRF RX"),
    ("W4", "w_blk", "U1 GND (c3,r8)", "U2 G (c4,r17)", [(3, 8), (3.5, 8.5), (3.5, 16.5), (4, 17)], "兩板共地（新增）"),
    ("W5", "w_red", "U2 5V (c22,r11)", "U3 G2 (c21,r6)", [(22, 11), (22, 7), (21.5, 6.5), (21, 6)], "BlackPill 5V → G2"),
    ("W6", "w_blk", "U2 G (c21,r11)", "U3 S2 (c20,r6)", [(21, 11), (21, 10), (20, 9.5), (20, 6)], "S2 → GND"),
    ("W7", "w_blk", "U3 S2 (c20,r6)", "U3 S1 (c20,r3)", [(20, 6), (20, 3)], "S1 → GND"),
    ("W8", "w_red", "U3 G1 (c19,r6)", "U3 D2 (c21,r3)", None, "G1 ↔ D2 相連（焊在轉接板上）"),
    ("W9", "w_red", "U3 D2 (c21,r3)", "R1 (c22,r1)", [(21, 3), (22, 2), (22, 1)], "D2 → R1"),
    ("W10", "w_org", "U3 D1 (c19,r3)", "R1 (c19,r1)", [(19, 3), (19, 1)], "D1 → R1"),
    ("W11", "w_org", "R1 (c19,r1)", "U1 P1.06 (c13,r2)", [(19, 1), (18, 1.5), (14, 1.5), (13, 2)], "D1 → nRF P1.06"),
]
for no, mat, a, b, path, note in WIRES:
    if path:
        bwire(mat, path)

# ---------- battery (bottom, under the BlackPill, on Kapton tape) ----------
BX0, BX1, BY0, BY1 = -27.5, 2.5, -1.2, 23.4          # assumed 30 x 25 x 5 mm LiPo
bz0, bz1 = ZB - BAT_GAP - 5.0, ZB - BAT_GAP
bat.box("lipo", BX0, BY0, bz0, BX1, BY1, bz1)
bat.box("kapton", BX0 - 0.05, BY0 - 0.05, bz0 - 0.05, BX0 + 9, BY1 + 0.05, bz1 + 0.05)
bat.box("kapton", BX0, BY0, bz1, BX1, BY1, bz1 + 0.12)                                         # insulation tape
bat.tube("w_red", [(BX0 + 6, BY0 + 1, bz0 + 3.5), (BX0 + 5, BY0 - 1.2, bz0 + 3.5), (HX(2), HY(8) + 1.0, ZW - 0.4), (HX(2), HY(8), ZB - 0.2)], 0.35)
bat.tube("w_blk", [(BX0 + 9, BY0 + 1, bz0 + 3.5), (BX0 + 8.5, BY0 - 1.0, bz0 + 3.5), (HX(3) + 0.4, HY(8) + 1.0, ZW - 0.6), (HX(3), HY(8), ZB - 0.2)], 0.35)

# ---------- enclosure (1.4 mm walls; nice!nano USB-C on the -X wall, BlackPill USB-C on the +X wall) ----------
WALL = 1.4
ix0, ix1 = -BW - 0.6, BW + 0.6
iy0, iy1 = -BH - 0.7, max(BH, BY1) + 0.5
iz0, iz1 = bz0 - 0.5, GAP + T + 3.2 + 0.5
ox0, ox1, oy0, oy1, oz0, oz1 = ix0 - WALL, ix1 + WALL, iy0 - WALL, iy1 + WALL, iz0 - WALL, iz1 + WALL
uz0, uz1 = GAP + T - 0.8, GAP + T + 4.0
def xwall(m, mat, xa, xb, hole):
    a, b = hole
    m.box(mat, xa, iy0, iz0, xb, a, iz1)
    m.box(mat, xa, b, iz0, xb, iy1, iz1)
    m.box(mat, xa, a, iz0, xb, b, uz0)
    m.box(mat, xa, a, uz1, xb, b, iz1)
NANO_HOLE = (NANO["cy"] - 5.0, NANO["cy"] + 5.0)
BP_HOLE = (BP["cy"] - 5.0, BP["cy"] + 5.0)
CASE_DIM = (ox1 - ox0, oy1 - oy0, oz1 - oz0)
def shell(m, lid):
    m.box("shell_in", ox0, oy0, oz0, ox1, oy1, iz0)
    if lid:
        m.box("shell", ox0, oy0, iz1, ox1, oy1, oz1)
    m.box("shell", ox0, oy0, iz0, ox1, iy0, iz1)
    m.box("shell", ox0, iy1, iz0, ox1, oy1, iz1)
    xwall(m, "shell", ox0, ix0, NANO_HOLE)          # left wall: nice!nano USB-C
    xwall(m, "shell", ix1, ox1, BP_HOLE)            # right wall: BlackPill USB-C
shell(case_open, False)
shell(case_closed, True)

# ---------- write models + KiCad boards ----------
asm.write(os.path.join(OUT, "product_assembly.wrl"))
bat.write(os.path.join(OUT, "product_battery.wrl"))

U = lambda: str(uuid.uuid4())
OX, OY = 150, 100
pads = "\n".join(f'  (pad "" thru_hole circle (at {HX(c):.3f} {-HY(r):.3f}) (size 1.8 1.8) (drill 1.0) (layers "*.Cu" "*.Mask") (uuid "{U()}"))'
                 for c in range(1, NC + 1) for r in range(1, NR + 1))
layers = """(layers
 (0 "F.Cu" signal) (2 "B.Cu" signal) (9 "F.Adhes" user "F.Adhesive") (11 "B.Adhes" user "B.Adhesive")
 (13 "F.Paste" user) (15 "B.Paste" user) (5 "F.SilkS" user "F.Silkscreen") (7 "B.SilkS" user "B.Silkscreen")
 (1 "F.Mask" user) (3 "B.Mask" user) (17 "Dwgs.User" user "User.Drawings") (19 "Cmts.User" user "User.Comments")
 (25 "Edge.Cuts" user) (27 "Margin" user) (31 "F.CrtYd" user "F.Courtyard") (29 "B.CrtYd" user "B.Courtyard")
 (35 "F.Fab" user) (33 "B.Fab" user))"""
def board(name, models):
    mdl = "\n".join(f'  (model "${{KIPRJMOD}}/{m}" (offset (xyz 0 0 0)) (scale (xyz 1 1 1)) (rotate (xyz 0 0 0)))' for m in models)
    txt = f"""(kicad_pcb (version 20241229) (generator "pcbnew") (generator_version "9.0")
 (general (thickness {T}) (legacy_teardrops no))
 (paper "A4")
 {layers}
 (setup
  (stackup
   (layer "F.SilkS" (type "Top Silk Screen") (color "White"))
   (layer "F.Mask" (type "Top Solder Mask") (color "Green") (thickness 0.01))
   (layer "F.Cu" (type "copper") (thickness 0.035))
   (layer "dielectric 1" (type "core") (thickness 1.51) (material "FR4") (epsilon_r 4.5) (loss_tangent 0.02))
   (layer "B.Cu" (type "copper") (thickness 0.035))
   (layer "B.Mask" (type "Bottom Solder Mask") (color "Green") (thickness 0.01))
   (copper_finish "HAL SnPb") (dielectric_constraints no))
  (pad_to_mask_clearance 0) (allow_soldermask_bridges_in_footprints no))
 (net 0 "")
 (footprint "product:Perfboard_23x18" (layer "F.Cu") (uuid "{U()}") (at {OX} {OY})
  (property "Reference" "PB1" (at 0 -26 0) (layer "F.SilkS") (hide yes) (uuid "{U()}") (effects (font (size 1 1) (thickness 0.15))))
  (property "Value" "perfboard" (at 0 26 0) (layer "F.Fab") (hide yes) (uuid "{U()}") (effects (font (size 1 1) (thickness 0.15))))
  (attr exclude_from_pos_files exclude_from_bom)
{pads}
{mdl}
 )
 (gr_rect (start {OX-BW} {OY-BH}) (end {OX+BW} {OY+BH}) (stroke (width 0.1) (type default)) (fill no) (layer "Edge.Cuts") (uuid "{U()}"))
)
"""
    open(os.path.join(OUT, name), "w", encoding="utf-8").write(txt)

board("perfboard_product.kicad_pcb", ["product_assembly.wrl", "product_battery.wrl"])
board("perfboard_product_nobattery.kicad_pcb", ["product_assembly.wrl"])

# ---------- wiring table ----------
with open(os.path.join(OUT, "洞洞板接線表.md"), "w", encoding="utf-8") as f:
    f.write(f"# 洞洞板接線表（平面版：兩板並排）\n\n洞洞板 {NC}×{NR} 孔（{NC*P:.1f}×{NR*P:.1f} mm），孔位 (c, r)：c 為欄 1–{NC}（左→右）、r 為列 1–{NR}（下→上，正面俯視）。\n\n")
    f.write("## 零件位置（正面）\n\n| 零件 | 孔位 | 備註 |\n|---|---|---|\n")
    f.write("| U1 nice!nano | c2–c13 × r2（P0.06 側）、r8（RAW 側） | USB-C 朝左緣；遠離 USB 的一端（天線側）右方淨空 |\n")
    f.write("| U2 BlackPill | c3–c22 × r17（3.3/G/5V…B12 排）、r11（VB…3.3/G/5V 排） | 轉 180°，USB-C 朝右緣 |\n")
    f.write("| U3 DMC2038LVT（SOT-23-6 轉接板） | r6：G1 c19、S2 c20、G2 c21；r3：D1 c19、S1 c20、D2 c21 | 互補 MOSFET（N+P） |\n")
    f.write("| R1 | c19 r1 ↔ c22 r1 | 跨在 D1 與 D2 之間 |\n")
    f.write("| 電池 | 反面，貼在 BlackPill 正下方（Kapton 膠帶絕緣） | 假設 30×25×5 mm |\n\n")
    f.write("## 接線（全部走反面，點對點）\n\n| 線號 | 顏色 | 起點 | 終點 | 用途 |\n|---|---|---|---|---|\n")
    cn = {"w_red": "紅", "w_blk": "黑", "w_yel": "黃", "w_org": "橘"}
    for no, mat, a, b, path, note in WIRES:
        f.write(f"| {no} | {cn[mat]} | {a} | {b} | {note} |\n")
    f.write(f"\n整體（含兩端 USB-C）約 {2*BW + 3:.1f} × {2*BH:.1f} mm。\n")
print("board mm: %.2f x %.2f" % (2 * BW, 2 * BH))
