"""Perfboard v1, smallest footprint: BlackPill on top, nice!nano + U3 (DMC2038LVT) + R1 + LiPo stacked
underneath. Board is 22 x 10 holes. Hole (c, r): c 1-22 left->right, r 1-10 bottom->top, top view."""
import sys, os, math, uuid
from collections import defaultdict

OUT = sys.argv[1]
P = 2.54
NC, NR = 22, 10
HX = lambda c: (c - 11.5) * P
HY = lambda r: (r - 5.5) * P
BW, BH = NC * P / 2, NR * P / 2
T = 1.6
ZB = -T
GAP = 1.5                                   # module stand-off (wires run in this gap)

MAT = {
    "pcb": ((0.07, 0.07, 0.08), 0), "gold": ((0.85, 0.66, 0.28), 0), "silver": ((0.8, 0.8, 0.82), 0),
    "solder": ((0.72, 0.73, 0.75), 0), "chip": ((0.13, 0.13, 0.14), 0), "gpcb": ((0.08, 0.5, 0.2), 0),
    "redpart": ((0.8, 0.12, 0.12), 0), "cap": ((0.15, 0.15, 0.15), 0), "led": ((0.95, 0.95, 0.95), 0),
    "w_red": ((0.88, 0.1, 0.1), 0), "w_blk": ((0.08, 0.08, 0.08), 0), "w_yel": ((0.97, 0.82, 0.08), 0),
    "w_org": ((0.97, 0.45, 0.1), 0), "lead": ((0.7, 0.7, 0.72), 0), "res": ((0.86, 0.76, 0.56), 0),
    "band": ((0.45, 0.25, 0.1), 0), "lipo": ((0.82, 0.82, 0.84), 0), "kapton": ((0.92, 0.58, 0.12), 0.1),
}

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

class Model:
    def __init__(self):
        self.mesh = defaultdict(lambda: ([], []))
    def face(self, mat, pts):
        v, f = self.mesh[mat]; b = len(v); v.extend(pts); f.append(list(range(b, b + len(pts))))
    def prism(self, mat, poly, z0, z1):
        z0, z1 = min(z0, z1), max(z0, z1)
        self.face(mat, [(x, y, z1) for x, y in poly]); self.face(mat, [(x, y, z0) for x, y in reversed(poly)])
        for i in range(len(poly)):
            (x0, y0), (x1, y1) = poly[i], poly[(i + 1) % len(poly)]
            self.face(mat, [(x0, y0, z0), (x1, y1, z0), (x1, y1, z1), (x0, y0, z1)])
    def box(self, mat, x0, y0, z0, x1, y1, z1):
        self.prism(mat, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], z0, z1)
    def rbox(self, mat, cx, cy, w, h, ang, z0, z1):
        c, s = math.cos(math.radians(ang)), math.sin(math.radians(ang))
        self.prism(mat, [(cx + x*c - y*s, cy + x*s + y*c) for x, y in [(-w/2, -h/2), (w/2, -h/2), (w/2, h/2), (-w/2, h/2)]], z0, z1)
    def disk(self, mat, cx, cy, r, z0, z1, n=12):
        self.prism(mat, [(cx + r*math.cos(2*math.pi*i/n), cy + r*math.sin(2*math.pi*i/n)) for i in range(n)], z0, z1)
    def tube(self, mat, pts, r=0.32, n=8, smooth=True):
        if smooth:
            pts = chaikin(pts)
        tans = [norm(sub(pts[min(i+1, len(pts)-1)], pts[max(i-1, 0)])) for i in range(len(pts))]
        u = norm(cross(tans[0], (0, 0, 1) if abs(tans[0][2]) < 0.9 else (1, 0, 0)))
        rings = []
        for p, t in zip(pts, tans):
            u0 = sub(u, mul(t, dot(u, t)))
            u = norm(u0) if dot(u0, u0) > 1e-6 else norm(cross(t, (0, 0, 1) if abs(t[2]) < 0.9 else (1, 0, 0)))
            w = cross(t, u)
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
                f.write(f"Shape {{ appearance Appearance {{ material Material {{ diffuseColor {col[0]:.3f} {col[1]:.3f} {col[2]:.3f} "
                        f"specularColor 0.25 0.25 0.25 shininess 0.3 transparency {tr} }} }}\n geometry IndexedFaceSet {{ solid FALSE creaseAngle 0.9\n"
                        f"  coord Coordinate {{ point [\n{pts}\n ] }}\n  coordIndex [ {idx} ] }} }}\n")

base, bp, nano, bat = Model(), Model(), Model(), Model()

def pin(m, c, r, z0, z1):
    x, y = HX(c), HY(r)
    m.box("gold", x - 0.32, y - 0.32, z0, x + 0.32, y + 0.32, z1)

def joint(c, r, top):
    z0, z1 = (0, 0.45) if top else (ZB, ZB - 0.45)
    base.disk("solder", HX(c), HY(r), 0.95, z0, z1, 10)

# ---------- U2 BlackPill: top side, face up, USB-C toward -X ----------
# header 2 (row 2): B12 c2 ... A9 c7 ... 5V c19, G c20, 3.3 c21 ; header 1 (row 8): 5V c2, G c3, 3.3 c4 ... VB c21
z0, z1 = GAP, GAP + T
for c in range(2, 22):
    for r in (2, 8):
        pin(bp, c, r, ZB - 1.0, z1 + 0.3)
        bp.disk("gold", HX(c), HY(r), 0.85, z1, z1 + 0.05, 10)
        joint(c, r, top=False)
cx, cy = (HX(2) + HX(21)) / 2, (HY(2) + HY(8)) / 2
bp.box("pcb", cx - 26.5, cy - 10.5, z0, cx + 26.5, cy + 10.5, z1)
bp.box("silver", cx - 26.5 - 1.5, cy - 4.5, z1, cx - 26.5 + 7, cy + 4.5, z1 + 3.2)
bp.rbox("chip", cx - 1.0, cy, 7, 7, 45, z1, z1 + 0.9)
for bx, by in ((cx + 12.0, cy - 3.0), (cx - 13.5, cy - 4.0), (cx - 13.5, cy + 2.5)):
    bp.box("silver", bx - 2.2, by - 1.8, z1, bx + 2.2, by + 1.8, z1 + 1.6)
    bp.disk("cap", bx, by, 1.0, z1 + 1.6, z1 + 2.3)
bp.box("led", cx + 11.3, cy + 5.2, z1, cx + 12.5, cy + 6.0, z1 + 0.5)
BP_TOP = z1 + 3.2

# ---------- U1 nice!nano: bottom side, face down, USB-C toward +X ----------
# row 9: RAW c21, GND c20, RST c19, VCC c18 ... P0.09 c10 ; row 3: P0.06 c21, P0.08 c20, GND c19, GND c18 ... P1.06 c10
nb1 = ZB - GAP                     # nano PCB top (facing the perfboard)
nb0 = nb1 - T                      # nano PCB bottom (components side)
for c in range(10, 22):
    for r in (3, 9):
        pin(nano, c, r, nb0 - 0.3, 1.0)
        nano.disk("gold", HX(c), HY(r), 0.85, nb0 - 0.05, nb0, 10)
        joint(c, r, top=True)
ncx, ncy = (HX(10) + HX(21)) / 2, (HY(3) + HY(9)) / 2
nano.box("pcb", ncx - 16.65, ncy - 9, nb0, ncx + 16.65, ncy + 9, nb1)
nano.box("silver", ncx + 16.65 - 7, ncy - 4.5, nb0 - 3.2, ncx + 16.65 + 1.5, ncy + 4.5, nb0)
nano.rbox("chip", ncx - 1.5, ncy, 7, 7, 45, nb0 - 0.9, nb0)
nano.box("silver", ncx + 3.5, ncy - 6.5, nb0 - 1.0, ncx + 6.5, ncy - 4.5, nb0)
nano.box("redpart", ncx - 13.8, ncy - 2.5, nb0 - 0.6, ncx - 12.2, ncy + 1.5, nb0)
NANO_BOT = nb0 - 3.2

# ---------- U3 DMC2038LVT on SOT-23-6 adapter: bottom side, face down ----------
# row 7: G2 c3, S2 c4, G1 c5 ; row 4: D2 c3, S1 c4, D1 c5
ab1 = ZB - GAP
ab0 = ab1 - 1.2
for c in (3, 4, 5):
    for r in (4, 7):
        pin(base, c, r, ab0 - 0.3, 1.0)
        base.disk("gold", HX(c), HY(r), 0.9, ab0 - 0.3, ab0)
        joint(c, r, top=True)
ux, uy = HX(4), (HY(4) + HY(7)) / 2
base.box("gpcb", ux - 5.1, uy - 5.7, ab0, ux + 5.1, uy + 5.7, ab1)
base.box("chip", ux - 1.45, uy - 0.8, ab0 - 1.1, ux + 1.45, uy + 0.8, ab0)
for dx in (-0.95, 0, 0.95):
    for sy in (1, -1):
        base.box("silver", ux + dx - 0.2, uy + sy * 0.8, ab0 - 0.25, ux + dx + 0.2, uy + sy * 1.5, ab0)
# G1 <-> D2 link on the adapter's exposed face (same as the red loop on the breadboard)
zl = ab0 - 0.45
base.tube("w_red", [(HX(5), HY(7), ab0 - 0.3), (HX(5.6), HY(6.6), zl - 0.6), (HX(6.3), HY(6.0), zl - 0.8),
                    (HX(6.3), HY(4.3), zl - 0.8), (HX(5.6), HY(3.45), zl - 0.8), (HX(3.4), HY(3.45), zl - 0.8),
                    (HX(3), HY(4), ab0 - 0.3)], 0.3)

# ---------- R1: bottom side, row 1, legs c3 / c6 ----------
rz = ZB - 1.0
base.tube("res", [(HX(3.75), HY(1), rz), (HX(5.25), HY(1), rz)], 0.95, smooth=False)
for dx in (-0.4, 0.4):
    base.tube("band", [(HX(4.5) + dx - 0.15, HY(1), rz), (HX(4.5) + dx + 0.15, HY(1), rz)], 1.0, smooth=False)
for c, d in ((3, 1), (6, -1)):
    base.tube("lead", [(HX(c), HY(1), 0.6), (HX(c), HY(1), rz), (HX(c) + d * 0.75, HY(1), rz)], 0.25, smooth=False)
    joint(c, 1, top=True)

# ---------- point-to-point wires ----------
def wire(mat, path, top):
    z = 0.55 if top else ZB - 0.55
    zj = 0.3 if top else ZB - 0.3
    p3 = [(HX(c), HY(r), z) for c, r in path]
    p3 = [(p3[0][0], p3[0][1], zj)] + p3 + [(p3[-1][0], p3[-1][1], zj)]
    base.tube(mat, p3, 0.3)

WIRES = [  # (no, mat, side, from, to, path, purpose)
    ("W1", "w_red", "反面", "電池 +", "U1 RAW (c21,r9)", None, "電池正極 → RAW"),
    ("W2", "w_blk", "反面", "電池 −", "U1 GND (c20,r9)", None, "電池負極 → GND（產品改接）"),
    ("W3", "w_yel", "反面", "U2 PA9 (c7,r2)", "U1 P0.08 (c20,r3)", [(7, 2), (7.5, 2.6), (7.5, 4.5), (8.5, 5), (19.5, 5), (20, 4), (20, 3)], "UART：BlackPill TX → nRF RX"),
    ("W4", "w_blk", "反面", "U1 GND (c19,r3)", "U2 G (c20,r2)", [(19, 3), (19.5, 2.5), (20, 2)], "nRF GND ↔ BlackPill GND"),
    ("W5", "w_red", "正面", "U2 5V (c2,r8)", "U3 G2 (c3,r7)", [(2, 8), (2.5, 7.5), (3, 7)], "BlackPill 5V → G2"),
    ("W6", "w_blk", "正面", "U2 G (c3,r8)", "U3 S2 (c4,r7)", [(3, 8), (3.5, 7.5), (4, 7)], "S2 → GND"),
    ("W7", "w_blk", "正面", "U3 S2 (c4,r7)", "U3 S1 (c4,r4)", [(4, 7), (4, 4)], "S1 → GND"),
    ("W8", "w_red", "U3 轉接板上", "U3 G1 (c5,r7)", "U3 D2 (c3,r4)", None, "G1 ↔ D2 相連"),
    ("W9", "w_red", "正面", "U3 D2 (c3,r4)", "R1 (c3,r1)", [(3, 4), (2.5, 3.4), (2.5, 1.6), (3, 1)], "D2 → R1"),
    ("W10", "w_org", "正面", "U3 D1 (c5,r4)", "R1 (c6,r1)", [(5, 4), (5.5, 3.4), (5.5, 1.6), (6, 1)], "D1 → R1"),
    ("W11", "w_org", "正面", "R1 (c6,r1)", "U1 P1.06 (c10,r3)", [(6, 1), (6.6, 1.0), (9.4, 1.0), (9.5, 2.5), (10, 3)], "D1 → nRF P1.06"),
]
for no, mat, side, a, b, path, note in WIRES:
    if path:
        wire(mat, path, top=(side == "正面"))

# ---------- LiPo: under the nice!nano, beside its USB-C ----------
BX0, BX1 = HX(19) - 30.0, HX(19)
BY0, BY1 = -12.5, 12.5                       # assumed 30 x 25 x 5 mm
bz1 = nb0 - 1.2
bz0 = bz1 - 5.0
bat.box("lipo", BX0, BY0, bz0, BX1, BY1, bz1)
bat.box("kapton", BX1 - 9, BY0 - 0.05, bz0 - 0.05, BX1 + 0.05, BY1 + 0.05, bz1 + 0.05)
bat.box("kapton", BX0, BY0, bz1, BX1, BY1, bz1 + 0.12)
for mat, c, dy in (("w_red", 21, 0.0), ("w_blk", 20, -0.9)):
    bat.tube(mat, [(BX1 - 2 + dy, BY1 - 1, bz0 + 3), (BX1 + 0.5 + dy, BY1 + 0.4, bz0 + 3.5), (HX(c - 0.3), BH - 0.6, nb1 - 0.3),
                   (HX(c), HY(9) + 1.4, ZB - 0.5), (HX(c), HY(9), ZB - 0.25)], 0.35)

# ---------- write models + KiCad boards ----------
for m, name in ((base, "v1_base.wrl"), (bp, "v1_blackpill.wrl"), (nano, "v1_nicenano.wrl"), (bat, "v1_battery.wrl")):
    m.write(os.path.join(OUT, name))

U = lambda: str(uuid.uuid4())
OX, OY = 150, 100
layers = """(layers
 (0 "F.Cu" signal) (2 "B.Cu" signal) (9 "F.Adhes" user "F.Adhesive") (11 "B.Adhes" user "B.Adhesive")
 (13 "F.Paste" user) (15 "B.Paste" user) (5 "F.SilkS" user "F.Silkscreen") (7 "B.SilkS" user "B.Silkscreen")
 (1 "F.Mask" user) (3 "B.Mask" user) (17 "Dwgs.User" user "User.Drawings") (19 "Cmts.User" user "User.Comments")
 (25 "Edge.Cuts" user) (27 "Margin" user) (31 "F.CrtYd" user "F.Courtyard") (29 "B.CrtYd" user "B.Courtyard")
 (35 "F.Fab" user) (33 "B.Fab" user))"""
pads = "\n".join(f'  (pad "" thru_hole circle (at {HX(c):.3f} {-HY(r):.3f}) (size 1.8 1.8) (drill 1.0) (layers "*.Cu" "*.Mask") (uuid "{U()}"))'
                 for c in range(1, NC + 1) for r in range(1, NR + 1))
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
 (footprint "product:Perfboard_22x10" (layer "F.Cu") (uuid "{U()}") (at {OX} {OY})
  (property "Reference" "PB1" (at 0 -16 0) (layer "F.SilkS") (hide yes) (uuid "{U()}") (effects (font (size 1 1) (thickness 0.15))))
  (property "Value" "perfboard" (at 0 16 0) (layer "F.Fab") (hide yes) (uuid "{U()}") (effects (font (size 1 1) (thickness 0.15))))
  (attr exclude_from_pos_files exclude_from_bom)
{pads}
{mdl}
 )
 (gr_rect (start {OX-BW} {OY-BH}) (end {OX+BW} {OY+BH}) (stroke (width 0.1) (type default)) (fill no) (layer "Edge.Cuts") (uuid "{U()}"))
)
"""
    open(os.path.join(OUT, name), "w", encoding="utf-8").write(txt)

ALL = ["v1_base.wrl", "v1_blackpill.wrl", "v1_nicenano.wrl", "v1_battery.wrl"]
board("perfboard_v1.kicad_pcb", ALL)
board("perfboard_v1_no_blackpill.kicad_pcb", ["v1_base.wrl", "v1_nicenano.wrl", "v1_battery.wrl"])
board("perfboard_v1_no_bottom.kicad_pcb", ["v1_base.wrl", "v1_blackpill.wrl"])

# ---------- wiring table ----------
x0 = min(-BW, cx - 26.5 - 1.5); x1 = max(BW, ncx + 16.65 + 1.5)
DIM = (x1 - x0, 2 * BH, BP_TOP - bz0)
with open(os.path.join(OUT, "第一版接線表.md"), "w", encoding="utf-8") as f:
    f.write(f"# 洞洞板第一版（最小化）\n\n洞洞板 {NC}×{NR} 孔（{2*BW:.1f}×{2*BH:.1f} mm）；含兩端 USB-C 整體約 **{DIM[0]:.1f} × {DIM[1]:.1f} × {DIM[2]:.1f} mm**。\n")
    f.write("孔位 (c, r)：c 為欄 1–22（左→右）、r 為列 1–10（下→上），一律以**正面俯視**標示。\n\n")
    f.write("## 零件位置\n\n| 零件 | 面 | 孔位 | 備註 |\n|---|---|---|---|\n")
    f.write("| U2 BlackPill | 正面，朝上 | c2–c21 × r2（B12…A9(c7)…5V c19/G c20/3.3 c21）、r8（5V c2/G c3/3.3 c4…VB c21） | USB-C 朝左緣 |\n")
    f.write("| U1 nice!nano | 反面，朝下 | c10–c21 × r9（RAW c21/GND c20/RST/VCC…P0.09 c10）、r3（P0.06 c21/P0.08 c20/GND c19/GND c18…P1.06 c10） | USB-C 朝右緣 |\n")
    f.write("| U3 DMC2038LVT（SOT-23-6 轉接板） | 反面，朝下 | r7：G2 c3、S2 c4、G1 c5；r4：D2 c3、S1 c4、D1 c5 | |\n")
    f.write("| R1 | 反面 | c3 r1 ↔ c6 r1 | |\n")
    f.write("| 電池 | 反面，貼在 nice!nano 下方（Kapton 絕緣） | 避開 nice!nano 的 USB-C | 假設 30×25×5 mm |\n\n")
    f.write("## 接線\n\n| 線號 | 顏色 | 面 | 起點 | 終點 | 用途 |\n|---|---|---|---|---|---|\n")
    cn = {"w_red": "紅", "w_blk": "黑", "w_yel": "黃", "w_org": "橘"}
    for no, mat, side, a, b, path, note in WIRES:
        f.write(f"| {no} | {cn[mat]} | {side} | {a} | {b} | {note} |\n")
    f.write("\n正面的線在 BlackPill 底下、反面的線在 nice!nano 底下，所以要**先焊線、再裝模組**。\n")
print("overall mm: %.1f x %.1f x %.1f" % DIM)
