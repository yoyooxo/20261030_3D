"""Build a VRML model of the breadboard build (from the photo-derived coordinates) plus a
.kicad_pcb that carries it, so KiCad's 3D viewer / `kicad-cli pcb render` can show it."""
import sys, os, math, uuid
from collections import defaultdict

OUTDIR = sys.argv[1]
WRL = os.path.join(OUTDIR, "breadboard_3d.wrl")
PCB = os.path.join(OUTDIR, "breadboard_3d.kicad_pcb")

P = 2.54
X = lambda c: (c - 32) * P
ROWY = dict(zip("abcdefghij", [-13.97, -11.43, -8.89, -6.35, -3.81, 3.81, 6.35, 8.89, 11.43, 13.97]))
Y = lambda r: ROWY[r]
TOP = 8.5          # breadboard top surface (mm above PCB)
HOLE_Z = TOP - 1.2

MAT = {
    "bb": ((0.95, 0.95, 0.93), 0), "hole": ((0.18, 0.18, 0.18), 0), "groove": ((0.80, 0.80, 0.78), 0),
    "redline": ((0.85, 0.2, 0.2), 0), "blueline": ((0.2, 0.45, 0.85), 0),
    "pcb": ((0.07, 0.07, 0.08), 0), "gold": ((0.85, 0.66, 0.28), 0), "silver": ((0.78, 0.78, 0.8), 0),
    "chip": ((0.13, 0.13, 0.14), 0), "hdr": ((0.09, 0.09, 0.09), 0), "yel_pl": ((0.96, 0.82, 0.12), 0),
    "gpcb": ((0.08, 0.5, 0.2), 0), "redpart": ((0.8, 0.12, 0.12), 0), "cap": ((0.15, 0.15, 0.15), 0),
    "w_red": ((0.88, 0.1, 0.1), 0), "w_grn": ((0.12, 0.72, 0.2), 0), "w_yel": ((0.97, 0.82, 0.08), 0),
    "w_org": ((0.97, 0.45, 0.1), 0), "w_pur": ((0.62, 0.42, 0.88), 0), "w_blk": ((0.06, 0.06, 0.06), 0),
    "lead": ((0.7, 0.7, 0.72), 0), "res": ((0.86, 0.76, 0.56), 0), "band": ((0.45, 0.25, 0.1), 0),
    "lipo": ((0.82, 0.82, 0.84), 0), "kapton": ((0.92, 0.58, 0.12), 0.15), "shrink": ((0.96, 0.88, 0.6), 0.25),
    "x1": ((1.0, 1.0, 1.0), 0.35), "led": ((0.95, 0.95, 0.95), 0),
}
mesh = defaultdict(lambda: ([], []))   # mat -> (points, faces)

def add_face(mat, pts):
    v, f = mesh[mat]
    base = len(v)
    v.extend(pts)
    f.append(list(range(base, base + len(pts))))

def prism(mat, poly, z0, z1, top_only=False):
    n = len(poly)
    add_face(mat, [(x, y, z1) for x, y in poly])
    if top_only:
        return
    add_face(mat, [(x, y, z0) for x, y in reversed(poly)])
    for i in range(n):
        (x0, y0), (x1, y1) = poly[i], poly[(i + 1) % n]
        add_face(mat, [(x0, y0, z0), (x1, y1, z0), (x1, y1, z1), (x0, y0, z1)])

def box(mat, x0, y0, z0, x1, y1, z1, **kw):
    prism(mat, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], z0, z1, **kw)

def rbox(mat, cx, cy, w, h, ang, z0, z1):
    c, s = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    pts = [(-w/2, -h/2), (w/2, -h/2), (w/2, h/2), (-w/2, h/2)]
    prism(mat, [(cx + x*c - y*s, cy + x*s + y*c) for x, y in pts], z0, z1)

def disk(mat, cx, cy, r, z0, z1, n=12):
    prism(mat, [(cx + r*math.cos(2*math.pi*i/n), cy + r*math.sin(2*math.pi*i/n)) for i in range(n)], z0, z1)

# ---------- tubes (wires) ----------
def sub(a, b): return tuple(p - q for p, q in zip(a, b))
def addv(a, b): return tuple(p + q for p, q in zip(a, b))
def mul(a, k): return tuple(p * k for p in a)
def dot(a, b): return sum(p * q for p, q in zip(a, b))
def cross(a, b): return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])
def norm(a):
    l = math.sqrt(dot(a, a)) or 1
    return mul(a, 1 / l)

def chaikin(pts, it=4):
    for _ in range(it):
        out = [pts[0]]
        for a, b in zip(pts, pts[1:]):
            out += [addv(mul(a, .75), mul(b, .25)), addv(mul(a, .25), mul(b, .75))]
        out.append(pts[-1])
        pts = out
    return pts

def tube(mat, pts, r=0.55, n=8, smooth=True):
    if smooth:
        pts = chaikin(pts)
    tans = [norm(sub(pts[min(i+1, len(pts)-1)], pts[max(i-1, 0)])) for i in range(len(pts))]
    ref = (0, 0, 1) if abs(tans[0][2]) < 0.9 else (1, 0, 0)
    u = norm(cross(tans[0], ref))
    rings = []
    for p, t in zip(pts, tans):
        u0 = sub(u, mul(t, dot(u, t))); u = norm(u0) if dot(u0, u0) > 1e-6 else norm(cross(t, (0, 0, 1) if abs(t[2]) < 0.9 else (1, 0, 0)))
        w = cross(t, u)
        rings.append([addv(p, addv(mul(u, r*math.cos(2*math.pi*k/n)), mul(w, r*math.sin(2*math.pi*k/n)))) for k in range(n)])
    for a, b in zip(rings, rings[1:]):
        for k in range(n):
            add_face(mat, [a[k], a[(k+1) % n], b[(k+1) % n], b[k]])

def wire(mat, a, b, via=(), h=10.0, r=0.55):
    """a,b: (x,y) hole positions; via: list of (x,y[,z]) waypoints at height h"""
    (xa, ya), (xb, yb) = a, b
    pts = [(xa, ya, HOLE_Z), (xa, ya, TOP + 0.3), (xa, ya, h - 1.0)]
    for v in via:
        pts.append((v[0], v[1], v[2] if len(v) > 2 else h))
    pts += [(xb, yb, h - 1.0), (xb, yb, TOP + 0.3), (xb, yb, HOLE_Z)]
    # keep the vertical ends straight
    tube(mat, pts[:2], r, smooth=False)
    tube(mat, pts[1:-1], r)
    tube(mat, pts[-2:], r, smooth=False)

def H(c, r): return (X(c), Y(r))

# ---------- breadboard ----------
BX, BY = 82.55, 27.3
box("bb", -BX, -BY, 0, BX, BY, TOP)
box("groove", X(0.5), -1.5, TOP - 0.01, X(63.5), 1.5, TOP + 0.01, top_only=True)
hs = 0.55
for c in range(1, 64):
    for r in "abcdefghij":
        x, y = H(c, r)
        box("hole", x - hs, y - hs, TOP, x + hs, y + hs, TOP + 0.02, top_only=True)
rail_cols = [3 + g * 6 + i for g in range(10) for i in range(5) if 3 + g * 6 + i <= 62]
for ry in (19.05, 21.59, -19.05, -21.59):
    for c in rail_cols:
        x = X(c)
        box("hole", x - hs, ry - hs, TOP, x + hs, ry + hs, TOP + 0.02, top_only=True)
for y, m in ((17.4, "redline"), (23.3, "blueline"), (-17.4, "blueline"), (-23.3, "redline")):
    box(m, X(1), y - 0.25, TOP, X(63), y + 0.25, TOP + 0.02, top_only=True)

# ---------- generic module on headers ----------
def headers(c0, c1, rows, z1=TOP + 2.5):
    for r in rows:
        box("hdr", X(c0) - 1.27, Y(r) - 1.27, TOP, X(c1) + 1.27, Y(r) + 1.27, z1)
        for c in range(c0, c1 + 1):
            box("gold", X(c) - 0.32, Y(r) - 0.32, HOLE_Z, X(c) + 0.32, Y(r) + 0.32, z1 + 1.6 + 0.6)
            disk("gold", X(c), Y(r), 0.85, z1 + 1.6, z1 + 1.65, 10)

# nice!nano (cols 1-12, rows h/d), USB toward -X
z0 = TOP + 2.5
headers(1, 12, "hd")
cx, cy = (X(1) + X(12)) / 2, (Y("h") + Y("d")) / 2
L, W = 33.3, 18.0
box("pcb", cx - L/2, cy - W/2, z0, cx + L/2, cy + W/2, z0 + 1.6)
zt = z0 + 1.6
box("silver", cx - L/2 - 1.5, cy - 4.5, zt, cx - L/2 + 7.0, cy + 4.5, zt + 3.2)        # USB-C
rbox("chip", cx + 1.5, cy, 7, 7, 45, zt, zt + 0.9)                                    # nRF52840
box("silver", cx - 6.5, cy + 4.5, zt, cx - 3.5, cy + 6.5, zt + 1.0)                   # crystal
box("silver", cx - 4.5, cy - 7.0, zt, cx - 1.0, cy - 5.6, zt + 0.8)
box("redpart", cx + 12.2, cy - 1.5, zt, cx + 13.8, cy + 2.5, zt + 0.6)               # C3
for k in range(3):
    disk("gold", cx + 9.8, cy + 2.6 - k * 2.6, 0.8, zt, zt + 0.05)                   # P1.01/P1.02/P1.07

# BlackPill (cols 44-63, rows h/d), USB toward +X
headers(44, 63, "hd")
cx, cy = (X(44) + X(63)) / 2, (Y("h") + Y("d")) / 2
L, W = 53.0, 21.0
box("pcb", cx - L/2, cy - W/2, z0, cx + L/2, cy + W/2, z0 + 1.6)
box("silver", cx + L/2 - 7.0, cy - 4.5, zt, cx + L/2 + 1.5, cy + 4.5, zt + 3.2)        # USB-C
rbox("chip", cx + 1.0, cy, 7, 7, 45, zt, zt + 0.9)                                    # STM32F411
for bx, by in ((cx - 12.0, cy + 3.0), (cx + 13.5, cy + 4.0), (cx + 13.5, cy - 2.5)):  # KEY, BOOT0, NRST
    box("silver", bx - 2.2, by - 1.8, zt, bx + 2.2, by + 1.8, zt + 1.6)
    disk("cap", bx, by, 1.0, zt + 1.6, zt + 2.3)
box("silver", cx - 5.5, cy + 6.0, zt, cx - 2.5, cy + 7.5, zt + 1.0)
box("led", cx - 12.5, cy - 6.0, zt, cx - 11.3, cy - 5.2, zt + 0.5)
for k in range(4):                                                                     # SWD pads 3V3/DIO/SCK/GND
    disk("gold", cx - 20.5, cy + 3.8 - k * 2.54, 0.75, zt, zt + 0.05)
# NRST flying wire on top of the BlackPill (purple loop)
tube("w_pur", [(cx + 11.0, cy - 6.2, zt + 0.2), (cx + 13.5, cy - 8.0, zt + 1.2), (cx + 18.0, cy - 7.8, zt + 1.0), (cx + 20.0, cy - 6.0, zt + 0.2)], 0.25)

# U3 SOT-23-6 adapter (cols 27-29, rows f/e)
headers(27, 29, "fe")
cx = X(28)
box("gpcb", cx - 5.2, -5.8, z0, cx + 5.2, 5.8, z0 + 1.2)
for c in (27, 28, 29):
    for r in "fe":
        disk("gold", X(c), Y(r), 0.9, z0 + 1.2, z0 + 1.6)
box("chip", cx - 1.45, -0.8, z0 + 1.3, cx + 1.45, 0.8, z0 + 2.4)
for dx in (-0.95, 0, 0.95):
    box("silver", cx + dx - 0.2, 0.8, z0 + 1.2, cx + dx + 0.2, 1.5, z0 + 1.45)
for dx in (-0.95, 0.95):
    box("silver", cx + dx - 0.2, -1.5, z0 + 1.2, cx + dx + 0.2, -0.8, z0 + 1.45)
disk("gold", cx - 0.95, 0.35, 0.15, z0 + 2.4, z0 + 2.42, 8)   # pin-1 dot
for dx in (-0.95, 0.95):                                            # 6-pin: middle lead on both sides
    pass
box("silver", cx - 0.2, -1.5, z0 + 1.2, cx + 0.2, -0.8, z0 + 1.45)
# 27上 <-> 29下 link on the adapter (red marking in the corrected photo)
zt = z0 + 1.65
tube("w_red", [(X(27), Y("f"), zt), (X(27), Y("f") + 1.4, zt + 0.8), (X(28), Y("f") + 2.4, zt + 1.0), (X(29) + 1.8, Y("f") + 1.6, zt + 1.0),
               (X(29) + 2.9, 0, zt + 1.0), (X(29) + 1.8, Y("e") - 1.4, zt + 0.8), (X(29), Y("e"), zt)], 0.32)

# pin headers J1/J2 (black, row j), J3/J4 (yellow, rows d/c)
def strip(mat, c0, c1, r):
    box(mat, X(c0) - 1.27, Y(r) - 1.27, TOP, X(c1) + 1.27, Y(r) + 1.27, TOP + 2.5)
    for c in range(c0, c1 + 1):
        box("gold", X(c) - 0.32, Y(r) - 0.32, HOLE_Z, X(c) + 0.32, Y(r) + 0.32, TOP + 2.5 + 6.0)
strip("hdr", 15, 18, "j"); strip("hdr", 36, 41, "j")
strip("yel_pl", 15, 18, "c"); strip("yel_pl", 36, 39, "d")

# R1 (row c, cols 27-29)
rz = TOP + 1.4
tube("res", [(X(27) + 0.9, Y("c"), rz), (X(29) - 0.9, Y("c"), rz)], 0.95, smooth=False)
for dx in (-0.4, 0.4):
    tube("band", [(X(28) + dx - 0.15, Y("c"), rz), (X(28) + dx + 0.15, Y("c"), rz)], 1.0, smooth=False)
for c, d in ((27, 1), (29, -1)):
    tube("lead", [(X(c), Y("c"), HOLE_Z), (X(c), Y("c"), rz), (X(c) + d * 0.9, Y("c"), rz)], 0.25, smooth=False)

# ---------- wires (from the photo-derived wiring table) ----------
xc = lambda c: X(c)
wire("w_red", H(1, "i"), H(22, "i"), [(X(4), 12.0), (X(20), 12.0)], h=10.2)                          # RAW
wire("w_grn", H(2, "i"), H(28, "d"), [(X(5), 12.8), (X(15), 12.6, 10.8), (X(21), 6.0, 11.6),
     (X(25), -0.5, 13.0), (X(26.3), -3.6, 13.4), (X(27.3), -5.6, 12.0)], h=10.6)                       # GND -> col28 lower
wire("w_yel", H(1, "c"), H(23, "f"), [(X(0.2), -12.0, 9.6), (X(3), -14.6), (X(14), -14.6), (X(17), -12.5, 10.2),
     (X(19.5), -6.5, 10.8), (X(21.5), -1.0, 11.4), (X(22.7), 2.2, 11.5)], h=9.8)                                              # P0.06 -> col23
wire("w_org", H(2, "c"), H(19, "f"), [(X(3), -9.9), (X(13), -9.9), (X(16), -5.0, 10.8), (X(18.4), 1.5, 11.2)], h=10.0)
wire("w_yel", H(3, "c"), H(20, "f"), [(X(4), -10.6), (X(13), -10.6), (X(16.5), -5.0, 11.4), (X(19.4), 1.5, 11.8)], h=10.4)
wire("w_yel", H(19, "h"), H(41, "h"), [(X(21), 12.4), (X(39), 12.4)], h=10.8)                            # UART
wire("w_red", H(20, "h"), H(40, "h"), [(X(22), 10.6), (X(38), 10.6)], h=10.0)                            # col20 -> J2.5
wire("w_pur", H(28, "h"), H(36, "h"), [], h=TOP + 0.9, r=0.55)                                                # U3 col28 -> col36
wire("w_yel", H(29, "j"), H(46, "j"), [(X(31), 14.8), (X(44), 14.8)], h=10.6)                          # 5V
wire("w_grn", H(41, "i"), H(58, "i"), [(X(42.5), 11.6), (X(56.5), 11.6)], h=9.4)                       # under BlackPill -> PA9
wire("w_red", H(12, "c"), H(27, "c"), [(X(13), -10.2), (X(21), -10.6), (X(25.3), -8.5, 11.5), (X(26), -6.6, 12.5),
     (X(27.6), -7.0, 11.5)], h=10.2)                                                                   # col12 -> col27 loop
wire("w_red", H(15, "b"), H(36, "b"), [(X(16), -12.0), (X(35), -12.0)], h=9.6)                         # S6
for c, m in ((15, "w_yel"), (17, "w_red"), (18, "w_red"), (36, "w_grn"), (38, "w_red"), (39, "w_red")):
    wire(m, H(c, "f"), H(c, "e"), [(X(c), 0, 11.8)], h=11.0, r=0.6)                                   # cross-channel jumpers
wire("w_red", H(36, "a"), (X(36), -19.05), [(X(36), -16.5, 11.3)], h=10.8, r=0.6)                      # col36 -> lower − rail
# purple bundles: J4 -> under nice!nano end, J3 -> under BlackPill SWD end (endpoints hidden, approximate)
for i, c in enumerate(range(15, 19)):
    tube("w_pur", [(X(c), Y("c"), TOP + 3.0), (X(c) - 1.0, Y("c") + 2.0, TOP + 5.5), (X(13.5), -2.0 + i * 1.3, TOP + 4.0),
                   (X(12.2), -2.0 + i * 1.3, TOP + 2.0)], 0.22)
for i, c in enumerate(range(36, 40)):
    tube("w_pur", [(X(c), Y("d"), TOP + 3.0), (X(c) + 1.0, Y("d") + 1.5, TOP + 5.5), (X(42.5), -2.5 + i * 1.6, TOP + 4.0),
                   (X(43.8), -2.5 + i * 1.6, TOP + 2.0)], 0.22)

# battery: heat-shrink 2-pin plug at cols 22(+)/23(−) row g, pouch lying beyond the top edge
box("shrink", X(22) - 1.7, Y("g") - 1.9, TOP, X(23) + 1.7, Y("g") + 1.9, TOP + 6.0)
for c in (22, 23):
    box("gold", X(c) - 0.32, Y("g") - 0.32, HOLE_Z, X(c) + 0.32, Y("g") + 0.32, TOP + 4.5)
pcx, pcy = X(22.5), 47.0
box("lipo", pcx - 12.5, pcy - 15, -1.6, pcx + 12.5, pcy + 15, 3.4)
box("kapton", pcx - 12.6, pcy - 15.1, -1.55, pcx + 12.6, pcy - 4, 3.5)
tube("w_red", [(pcx - 5, pcy - 15, 2.0), (pcx - 6, pcy - 19, 9), (X(22) - 1, 24, 22), (X(22), 12, 20), (X(22), Y("g"), TOP + 6.0)], 0.4)
tube("w_blk", [(pcx + 3, pcy - 15, 2.0), (pcx + 4, pcy - 19, 9), (X(23) + 2, 24, 20), (X(23), 12, 18), (X(23), Y("g"), TOP + 6.0)], 0.4)
# X1: unidentified white translucent object at cols 22-23, row j
box("x1", X(22) - 0.9, Y("j") - 1.4, TOP, X(23) + 0.9, Y("j") + 1.4, TOP + 2.6)

# ---------- write VRML (KiCad WRL units: 1 = 2.54 mm) ----------
with open(WRL, "w", encoding="utf-8") as f:
    f.write("#VRML V2.0 utf8\n# breadboard build reconstructed from photos\n")
    for mat, (v, faces) in mesh.items():
        col, tr = MAT[mat]
        pts = ",\n".join(f"{x/P:.4f} {y/P:.4f} {z/P:.4f}" for x, y, z in v)
        idx = ",".join(",".join(map(str, fc)) + ",-1" for fc in faces)
        f.write(f"""Shape {{
 appearance Appearance {{ material Material {{ diffuseColor {col[0]} {col[1]} {col[2]} specularColor 0.25 0.25 0.25 shininess 0.3 transparency {tr} }} }}
 geometry IndexedFaceSet {{ solid FALSE creaseAngle 0.9
  coord Coordinate {{ point [
{pts}
 ] }}
  coordIndex [ {idx} ] }}
}}
""")

# ---------- carrier board ----------
U = lambda: str(uuid.uuid4())
layers = """(layers
 (0 "F.Cu" signal) (2 "B.Cu" signal) (9 "F.Adhes" user "F.Adhesive") (11 "B.Adhes" user "B.Adhesive")
 (13 "F.Paste" user) (15 "B.Paste" user) (5 "F.SilkS" user "F.Silkscreen") (7 "B.SilkS" user "B.Silkscreen")
 (1 "F.Mask" user) (3 "B.Mask" user) (17 "Dwgs.User" user "User.Drawings") (19 "Cmts.User" user "User.Comments")
 (25 "Edge.Cuts" user) (27 "Margin" user) (31 "F.CrtYd" user "F.Courtyard") (29 "B.CrtYd" user "B.Courtyard")
 (35 "F.Fab" user) (33 "B.Fab" user))"""
OX, OY = 150, 100
def silk(t, mx, my, size=2.6, just="center"):
    j = "" if just == "center" else f" (justify {just})"
    return f'(gr_text "{t}" (at {OX+mx:.2f} {OY-my:.2f} 0) (layer "F.SilkS") (uuid "{U()}") (effects (font (size {size} {size}) (thickness 0.4)){j}))'
def lead(mx, my0, my1):
    return f'(gr_line (start {OX+mx:.2f} {OY-my0:.2f}) (end {OX+mx:.2f} {OY-my1:.2f}) (stroke (width 0.3) (type default)) (layer "F.SilkS") (uuid "{U()}"))'
LB = [silk("U1 nice!nano 相容 (nRF52840)", X(1) - 2, -34, 2.2, "left"), lead((X(1)+X(12))/2, -28.3, -32.0),
      silk("U3 DMC2038LVT 互補 MOSFET", X(28), -40.5, 2.2), silk("N+P 通道 TSOT26；S1 接 GND、G1↔D2 相連", X(28), -44.5, 1.8), lead(X(28), -28.3, -38.5),
      silk("U2 WeAct BlackPill (STM32F401/F411)", X(63) + 3, -34, 2.2, "right"), lead((X(44)+X(63))/2, -28.3, -32.0),
      silk("[!] 電池負極在欄23，與 P0.06 同欄（不是 GND）", X(1) - 2, -51, 2.0, "left"),
      silk("BT1 LiPo（欄22 + / 欄23 −）", X(22.5) + 16, 47, 2.2, "left")]
labels = chr(10).join(LB)
pcb = f"""(kicad_pcb (version 20241229) (generator "pcbnew") (generator_version "9.0")
 (general (thickness 1.6) (legacy_teardrops no))
 (paper "A4")
 {layers}
 (setup
  (stackup
   (layer "F.SilkS" (type "Top Silk Screen") (color "Black"))
   (layer "F.Mask" (type "Top Solder Mask") (color "White") (thickness 0.01))
   (layer "F.Cu" (type "copper") (thickness 0.035))
   (layer "dielectric 1" (type "core") (color "#D8D8D8") (thickness 1.51) (material "FR4") (epsilon_r 4.5) (loss_tangent 0.02))
   (layer "B.Cu" (type "copper") (thickness 0.035))
   (layer "B.Mask" (type "Bottom Solder Mask") (color "White") (thickness 0.01))
   (copper_finish "None") (dielectric_constraints no))
  (pad_to_mask_clearance 0) (allow_soldermask_bridges_in_footprints no))
 (net 0 "")
 (footprint "restore:Breadboard_Assembly" (layer "F.Cu") (uuid "{U()}") (at {OX} {OY})
  (property "Reference" "BB1" (at 0 -30 0) (layer "F.SilkS") (hide yes) (uuid "{U()}") (effects (font (size 1 1) (thickness 0.15))))
  (property "Value" "breadboard_build" (at 0 30 0) (layer "F.Fab") (hide yes) (uuid "{U()}") (effects (font (size 1 1) (thickness 0.15))))
  (attr exclude_from_pos_files exclude_from_bom)
  (model "${{KIPRJMOD}}/breadboard_3d.wrl" (offset (xyz 0 0 0)) (scale (xyz 1 1 1)) (rotate (xyz 0 0 0)))
 )
{labels}
 (gr_rect (start {OX-BX-3} {OY-BY-42}) (end {OX+BX+3} {OY+BY+30}) (stroke (width 0.1) (type default)) (fill no) (layer "Edge.Cuts") (uuid "{U()}"))
)
"""
open(PCB, "w", encoding="utf-8").write(pcb)
print("faces:", sum(len(f) for _, f in mesh.values()), "->", WRL)
