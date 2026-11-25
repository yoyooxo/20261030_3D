"""3D renders:
  立體_整體_斜視.png / 立體_整體_正面.png : adapter PCB + ICA-609 socket + card + breadboard + nRF52840 SuperMini
                                          + every jumper wire of 接線圖_含nRF.png + LiPo battery
  立體_PCB_斜視.png / 立體_PCB_正面.png / 立體_PCB_背面.png : the bare PCB only (no parts)
usage: python gen_scene_nrf.py   (after gen_scene.py, which writes _scene_render_only.kicad_pcb)"""
import os, re, math, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import models3d

KCLI = os.environ.get("KICAD_CLI", "kicad-cli")   # set KICAD_CLI to your kicad-cli path (KiCad 9+)
P = 2.54
ROWS = {"a": -7.62, "b": -5.08, "c": -2.54, "d": 0, "e": 2.54, "f": 10.16, "g": 12.7, "h": 15.24, "i": 17.78, "j": 20.32}
ZT = -models3d.PCB_T - models3d.HDR_PLASTIC      # breadboard top, relative to the adapter PCB top (J2 frame)
ZTAB = ZT - 8.5                                  # table

# wiring = the same list the 2D drawing uses
_s = open(os.path.join(HERE, "gen_wiring_nrf.py"), encoding="utf-8").read()
_g = {}
for name in ("MC0, MC1 = ", "TOP = ", "BOT = "):
    i = _s.index(name); exec(_s[i:_s.index("\n", i)].split("  #")[0], _g)
i = _s.index("WIRES = ["); exec(_s[i:_s.index("\n]", i) + 2], _g)
WIRES, MC0, MC1 = _g["WIRES"], _g["MC0"], _g["MC1"]
hx = lambda c: (c - 1) * P
hole = lambda r, c: (hx(c), ROWS[r])


def wrl(path, shapes):
    """shapes: (8 vertices (x, y_pcb_down, z) in mm, rgb, transparency)"""
    out = ["#VRML V2.0 utf8"]
    for v, rgb, tr in shapes:
        pts = ", ".join(f"{x / P:.4f} {-y / P:.4f} {z / P:.4f}" for x, y, z in v)
        out.append("Shape { appearance Appearance { material Material { diffuseColor %.3f %.3f %.3f "
                   "specularColor 0.3 0.3 0.3 shininess 0.4 transparency %.2f } }" % (rgb + (tr,)))
        out.append("  geometry IndexedFaceSet { coord Coordinate { point [ %s ] }" % pts)
        out.append("    coordIndex [ 0 1 2 3 -1 7 6 5 4 -1 4 5 1 0 -1 5 6 2 1 -1 6 7 3 2 -1 7 4 0 3 -1 ] } }")  # y is mirrored: reversed winding
    open(path, "w", encoding="utf-8").write("\n".join(out))


def box(x0, x1, y0, y1, z0, z1):
    x0, x1 = sorted((x0, x1)); y0, y1 = sorted((y0, y1)); z0, z1 = sorted((z0, z1))
    return [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0), (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]


def tube(p0, p1, w=0.45):
    d = [p1[k] - p0[k] for k in range(3)]
    n = math.sqrt(sum(v * v for v in d)) or 1e-6
    d = [v / n for v in d]
    up = (0, 0, 1) if abs(d[2]) < 0.9 else (1, 0, 0)
    u = [d[1] * up[2] - d[2] * up[1], d[2] * up[0] - d[0] * up[2], d[0] * up[1] - d[1] * up[0]]
    un = math.sqrt(sum(v * v for v in u)); u = [v / un for v in u]
    v_ = [d[1] * u[2] - d[2] * u[1], d[2] * u[0] - d[0] * u[2], d[0] * u[1] - d[1] * u[0]]
    return [tuple(q[k] + w * (a * u[k] + b * v_[k]) for k in range(3))
            for q in (p0, p1) for a, b in ((-1, -1), (1, -1), (1, 1), (-1, 1))]


rgb = lambda h: tuple(int(h.lstrip("#")[k:k + 2], 16) / 255 for k in (0, 2, 4))
GOLD, BLK = (0.85, 0.68, 0.25), (0.08, 0.08, 0.09)

# ---------------- nRF52840 SuperMini on its two header strips ----------------
S = []
mx0, mx1 = hx(MC0) - 1.6, hx(MC1) + 1.6
my0, my1 = ROWS["d"] - 1.4, ROWS["h"] + 1.4
zb = ZT + 2.5                                   # module PCB bottom (header plastic 2.5)
S.append((box(mx0, mx1, my0, my1, zb, zb + 1.0), (0.10, 0.18, 0.38), 0.0))                  # module PCB
for r in ("d", "h"):
    y = ROWS[r]
    S.append((box(hx(MC0) - 1.27, hx(MC1) + 1.27, y - 1.25, y + 1.25, ZT, zb), BLK, 0.0))     # header plastic
    for c in range(MC0, MC1 + 1):
        S.append((box(hx(c) - 0.32, hx(c) + 0.32, y - 0.32, y + 0.32, ZT - 6, zb + 1.6), GOLD, 0.0))
        S.append((box(hx(c) - 0.8, hx(c) + 0.8, y - 0.8, y + 0.8, zb + 1.0, zb + 1.05), GOLD, 0.0))   # pad ring
cx, cy = (mx0 + mx1) / 2 - 3, (my0 + my1) / 2
S.append((box(cx - 5.5, cx + 5.5, cy - 5.5, cy + 5.5, zb + 1.0, zb + 2.2), (0.75, 0.76, 0.78), 0.0))  # nRF52840 can
S.append((box(mx1 - 7.3, mx1 + 1.2, cy - 4.5, cy + 4.5, zb + 1.0, zb + 4.2), (0.80, 0.81, 0.83), 0.0))  # USB-C
S.append((box(mx0 + 2, mx0 + 5, cy - 1.5, cy + 1.5, zb + 1.0, zb + 1.8), BLK, 0.0))                     # regulator etc.

# ---------------- jumper wires: dupont heads + an arch over everything ----------------
HEAD = 6.0
for k, (col, lab, (r0, c0), (r1, c1), _) in enumerate(WIRES):
    zh = 6.0 + 1.6 * k
    a, b = hole(r0, c0), hole(r1, c1)
    pts = [(a[0], a[1], ZT + HEAD), (a[0], a[1], zh), (b[0], b[1], zh), (b[0], b[1], ZT + HEAD)]
    for p0, p1 in zip(pts, pts[1:]):
        S.append((tube(p0, p1), rgb(col), 0.0))
    for x, y in (a, b):
        S.append((box(x - 1.1, x + 1.1, y - 1.1, y + 1.1, ZT, ZT + HEAD), BLK, 0.0))
        S.append((box(x - 0.3, x + 0.3, y - 0.3, y + 0.3, ZT - 5, ZT), GOLD, 0.0))
# W8: short jumper b23-b24 (P0.22 <-> P0.20)
a, b = hole("b", 23), hole("b", 24)
for x, y in (a, b):
    S.append((box(x - 1.1, x + 1.1, y - 1.1, y + 1.1, ZT, ZT + HEAD), BLK, 0.0))
S.append((tube((a[0], a[1], ZT + HEAD), (a[0], a[1], ZT + HEAD + 1.5)), rgb("#e6b800"), 0.0))
S.append((tube((a[0], a[1], ZT + HEAD + 1.5), (b[0], b[1], ZT + HEAD + 1.5)), rgb("#e6b800"), 0.0))
S.append((tube((b[0], b[1], ZT + HEAD + 1.5), (b[0], b[1], ZT + HEAD)), rgb("#e6b800"), 0.0))

# ---------------- LiPo battery on the table, below the breadboard; + to j29 (RAW), - to j28 (GND) ----------------
bx = hx(28.5)
S.append((box(bx - 11.5, bx + 11.5, 37.0, 50.0, ZTAB, ZTAB + 4.5), (0.80, 0.82, 0.86), 0.0))
S.append((box(bx - 11.5, bx + 11.5, 37.0, 39.0, ZTAB + 4.5, ZTAB + 5.2), (0.2, 0.3, 0.65), 0.0))   # protection board
for c, colr, k in ((29, "#d62728", 0), (28, "#222222", 1)):
    x, y = hole("j", c)
    zl = ZT + HEAD + 2.0 + 1.2 * k
    pts = [(x, 38.0, ZTAB + 5.2), (x, 38.0, zl), (x, y, zl), (x, y, ZT + HEAD)]
    for p0, p1 in zip(pts, pts[1:]):
        S.append((tube(p0, p1, 0.4), rgb(colr), 0.0))
    S.append((box(x - 1.1, x + 1.1, y - 1.1, y + 1.1, ZT, ZT + HEAD), BLK, 0.0))

wrl(os.path.join(HERE, "3d", "nrf_wires_battery.wrl"), S)

# ---------------- scene: hang the new model on J2 (same frame as the breadboard model) ----------------
scene_src = open(os.path.join(HERE, "_scene_render_only.kicad_pcb"), encoding="utf-8").read()
bb = '(model "${KIPRJMOD}/3d/breadboard_400.wrl"'
assert scene_src.count(bb) == 1
scene_src = scene_src.replace(bb, '(model "${KIPRJMOD}/3d/nrf_wires_battery.wrl" (offset (xyz 0 0 0)) (scale (xyz 1 1 1)) (rotate (xyz 0 0 0)))\n  ' + bb, 1)
scene = os.path.join(HERE, "_scene_nrf_render_only.kicad_pcb")
open(scene, "w", encoding="utf-8").write(scene_src)

# bare PCB: drop every 3D model
bare_src = open(os.path.join(HERE, "card609_breakout.kicad_pcb"), encoding="utf-8").read()
bare_src = re.sub(r'\n\s*\(model "[^"]*"[^\n]*', "", bare_src)
bare = os.path.join(HERE, "_bare_pcb_render_only.kicad_pcb")
open(bare, "w", encoding="utf-8").write(bare_src)


def render(pcb, name, *args):
    subprocess.run([KCLI, "pcb", "render", "-o", os.path.join(HERE, name), "-w", "1800", "-h", "1200",
                    "--quality", "high", "--background", "opaque", *args, pcb], check=True, capture_output=True)
    print("rendered", name)


render(scene, "立體_整體_斜視.png", "--rotate", "-50,0,15", "--zoom", "0.42", "--perspective")
render(scene, "立體_整體_正面.png", "--side", "top", "--zoom", "0.45")
render(bare, "立體_PCB_斜視.png", "--rotate", "-45,0,30", "--zoom", "1.0", "--perspective")
render(bare, "立體_PCB_正面.png", "--side", "top", "--zoom", "1.0")
render(bare, "立體_PCB_背面.png", "--side", "bottom", "--zoom", "1.0")
