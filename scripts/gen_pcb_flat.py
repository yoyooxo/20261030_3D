"""2-layer PCB, flat layout: BlackPill (top half) and nice!nano (bottom half) both on the TOP side,
DMC2038LVT (SOT-23-6) + R1 (0805) beside the nice!nano antenna end, back side kept free for the card connector.
Board coordinates: mm, origin at board centre, y down (KiCad)."""
import sys, os, uuid, math
from collections import defaultdict

OUT = sys.argv[1]
OX, OY = 150.0, 100.0
P = 2.54
U = lambda: str(uuid.uuid4())
f = lambda v: f"{v:.4f}".rstrip("0").rstrip(".")
BX, BY = 26.5, 20.0                                   # board 53.0 x 40.0 mm

NETS = ["", "GND", "+5V", "UART_PA9_P0.08", "N_G1_D2", "N_D1"]
NI = {n: i for i, n in enumerate(NETS)}
net = lambda n: f'(net {NI[n]} "{n}")' if n else ""

# ---------- placement ----------
BP_Y2, BP_Y1 = -17.12, -1.88                          # BlackPill header 2 (top) / header 1 (bottom) rows
BP_X = [24.13 - i * P for i in range(20)]             # index 0 = USB end (+X)
NANO_CX, NANO_CY = -9.85, 11.0
NANO_T, NANO_B = NANO_CY - 7.62, NANO_CY + 7.62       # RAW row (top) / P0.06 row (bottom)
NANO_X = [NANO_CX - 13.97 + i * P for i in range(12)] # index 0 = USB end (-X)
U3_AT = (17.0, 9.0)
R1_AT = (21.0, 9.0)
ANT = (5.2, 2.5, 10.0, 18.8)                          # antenna keep-out x0, y0, x1, y1

def tht(num, x, y, n="", shape="circle", zc=""):
    return (f'(pad "{num}" thru_hole {shape} (at {f(x)} {f(y)}) (size 1.7 1.7) (drill 1.0) '
            f'(layers "*.Cu" "*.Mask") {net(n)} {zc} (uuid "{U()}"))')
def smd(num, x, y, w, h, n=""):
    return (f'(pad "{num}" smd roundrect (at {f(x)} {f(y)}) (size {f(w)} {f(h)}) (layers "F.Cu" "F.Paste" "F.Mask") '
            f'(roundrect_rratio 0.25) {net(n)} (uuid "{U()}"))')
def rect(layer, x0, y0, x1, y1, w=0.12):
    return f'(fp_rect (start {f(x0)} {f(y0)}) (end {f(x1)} {f(y1)}) (stroke (width {w}) (type solid)) (fill no) (layer "{layer}") (uuid "{U()}"))'
def text(layer, s, x, y, size=1.0):
    return f'(fp_text user "{s}" (at {f(x)} {f(y)} 0) (layer "{layer}") (uuid "{U()}") (effects (font (size {size} {size}) (thickness 0.15))))'
def fp(ref, value, at, pads, graphics, model=None, ref_at=(0, 0), attr="through_hole"):
    s = [f'(footprint "pcb:{value}" (layer "F.Cu") (uuid "{U()}") (at {f(OX + at[0])} {f(OY + at[1])})',
         f'  (property "Reference" "{ref}" (at {f(ref_at[0])} {f(ref_at[1])} 0) (layer "F.SilkS") (uuid "{U()}") (effects (font (size 1 1) (thickness 0.15))))',
         f'  (property "Value" "{value}" (at 0 0 0) (layer "F.Fab") (hide yes) (uuid "{U()}") (effects (font (size 1 1) (thickness 0.15))))',
         f'  (attr {attr})'] + ["  " + g for g in graphics] + ["  " + p for p in pads]
    if model:
        s.append(f'  (model "{model}" (offset (xyz 0 0 0)) (scale (xyz 1 1 1)) (rotate (xyz 0 0 0)))')
    return "\n".join(s + [")"])

# BlackPill: header 2 (y=-17.12): B12 at USB end ... PA9 index 5 ... 5V/G/3V3 index 17/18/19
#            header 1 (y=-1.88): 5V index 0, G index 1, 3V3 index 2 ... VB index 19
H2 = ["B12", "B13", "B14", "B15", "A8", "A9", "A10", "A11", "A12", "A15", "B3", "B4", "B5", "B6", "B7", "B8", "B9", "5V", "G", "3V3"]
H1 = ["5V", "G", "3V3", "B10", "B2", "B1", "B0", "A7", "A6", "A5", "A4", "A3", "A2", "A1", "A0", "R", "C15", "C14", "C13", "VB"]
bp_net = {("H", 5): "UART_PA9_P0.08", ("H", 18): "GND", ("L", 0): "+5V", ("L", 1): "GND"}
bp_pads = []
for i in range(20):
    bp_pads.append(tht(f"H{i+1}", BP_X[i], BP_Y2, bp_net.get(("H", i), "")))
    bp_pads.append(tht(f"L{i+1}", BP_X[i], BP_Y1, bp_net.get(("L", i), ""), "rect" if i == 0 else "circle"))
bp_g = [rect("F.Fab", -26.5, -20.0, 26.5, 1.0, 0.1), rect("F.CrtYd", -26.75, -20.25, 28.3, 1.25, 0.05),
        text("F.SilkS", "BlackPill", -2, -9.5, 1.2), text("F.SilkS", "USB", 23.0, -9.5, 0.9),
        text("F.SilkS", "PA9", BP_X[5], BP_Y2 + 1.9, 0.8), text("F.SilkS", "5V", BP_X[0], BP_Y1 - 1.9, 0.8)]

# nice!nano: bottom row (y=18.62): P0.06 index 0 (USB end) ... P1.06 index 11 ; top row (y=3.38): RAW index 0, GND 1, RST 2, VCC 3 ...
NB = ["P0.06", "P0.08", "GND", "GND", "P0.17", "P0.20", "P0.22", "P0.24", "P1.00", "P0.11", "P1.04", "P1.06"]
NT = ["RAW", "GND", "RST", "VCC", "P0.31", "P0.29", "P0.02", "P1.15", "P1.13", "P1.11", "P0.10", "P0.09"]
nb_net = {1: "UART_PA9_P0.08", 2: "GND", 3: "GND", 11: "N_D1"}
nt_net = {1: "GND"}
nano_pads = []
for i in range(12):
    nano_pads.append(tht(str(i + 1), NANO_X[i], NANO_B, nb_net.get(i, ""), "rect" if i == 0 else "circle",
                         "(zone_connect 2)" if nb_net.get(i) == "GND" else ""))
    nano_pads.append(tht(str(24 - i), NANO_X[i], NANO_T, nt_net.get(i, "")))
nano_g = [rect("F.Fab", NANO_CX - 16.65, NANO_CY - 9, NANO_CX + 16.65, NANO_CY + 9, 0.1),
          rect("F.CrtYd", NANO_CX - 18.4, NANO_CY - 9.25, NANO_CX + 16.9, NANO_CY + 9.25, 0.05),
          text("F.SilkS", "nice!nano", NANO_CX - 1, NANO_CY, 1.2), text("F.SilkS", "USB", NANO_CX - 13.5, NANO_CY, 0.9),
          text("F.SilkS", "RAW", NANO_X[0], NANO_T + 1.9, 0.8), text("F.SilkS", "P0.08", NANO_X[1] + 0.5, NANO_B - 1.9, 0.8)]

U3P = {1: (-1.1375, -0.95), 2: (-1.1375, 0), 3: (-1.1375, 0.95), 4: (1.1375, 0.95), 5: (1.1375, 0), 6: (1.1375, -0.95)}
U3N = {1: "N_G1_D2", 2: "GND", 3: "+5V", 4: "N_G1_D2", 5: "GND", 6: "N_D1"}
u3_pads = [smd(n, x, y, 1.325, 0.6, U3N[n]) for n, (x, y) in U3P.items()]
u3_g = [f'(fp_line (start -0.8 -1.56) (end 0.8 -1.56) (stroke (width 0.12) (type solid)) (layer "F.SilkS") (uuid "{U()}"))',
        f'(fp_line (start -0.8 1.56) (end 0.8 1.56) (stroke (width 0.12) (type solid)) (layer "F.SilkS") (uuid "{U()}"))',
        f'(fp_circle (center -1.9 -1.6) (end -1.75 -1.6) (stroke (width 0.3) (type solid)) (fill yes) (layer "F.SilkS") (uuid "{U()}"))',
        rect("F.CrtYd", -2.05, -1.7, 2.05, 1.7, 0.05), rect("F.Fab", -0.8, -1.45, 0.8, 1.45, 0.1)]
r1_pads = [smd(1, 0, 0.9125, 1.4, 1.025, "N_G1_D2"), smd(2, 0, -0.9125, 1.4, 1.025, "N_D1")]
r1_g = [rect("F.CrtYd", -0.95, -1.68, 0.95, 1.68, 0.05), rect("F.Fab", -0.625, -1.0, 0.625, 1.0, 0.1)]

MD = "${KIPRJMOD}"
footprints = [
    fp("U2", "WeAct_BlackPill", (0, 0), bp_pads, bp_g, f"{MD}/flatpcb_blackpill.wrl", ref_at=(-2, -7.6)),
    fp("U1", "nice!nano_v2", (0, 0), nano_pads, nano_g, f"{MD}/flatpcb_nicenano.wrl", ref_at=(NANO_CX - 1, NANO_CY + 1.8)),
    fp("U3", "DMC2038LVT_SOT-23-6", U3_AT, u3_pads, u3_g, "${KICAD10_3DMODEL_DIR}/Package_TO_SOT_SMD.3dshapes/SOT-23-6.step",
       ref_at=(0, -2.6), attr="smd"),
    fp("R1", "R_0805", R1_AT, r1_pads, r1_g, "${KICAD10_3DMODEL_DIR}/Resistor_SMD.3dshapes/R_0805_2012Metric.step",
       ref_at=(1.9, 0), attr="smd"),
]

# ---------- tracks ----------
items = []
def track(layer, n, pts, w=0.25):
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        items.append(f'(segment (start {f(OX+x0)} {f(OY+y0)}) (end {f(OX+x1)} {f(OY+y1)}) (width {w}) (layer "{layer}") (net {NI[n]}) (uuid "{U()}"))')
def via(n, x, y):
    items.append(f'(via (at {f(OX+x)} {f(OY+y)}) (size 0.6) (drill 0.3) (layers "F.Cu" "B.Cu") (net {NI[n]}) (uuid "{U()}"))')
u = lambda n: (U3_AT[0] + U3P[n][0], U3_AT[1] + U3P[n][1])
R1p1, R1p2 = (R1_AT[0], R1_AT[1] + 0.9125), (R1_AT[0], R1_AT[1] - 0.9125)

# UART on the back: BlackPill PA9 -> nice!nano P0.08
px, py = BP_X[5], BP_Y2
qx, qy = NANO_X[1], NANO_B
track("B.Cu", "UART_PA9_P0.08", [(px, py), (px, -14.0), (-20.32, -14.0), (-20.32, 0.0), (-20.01, 0.75), (-20.01, 17.35), (qx, qy)])
# +5V : BlackPill 5V (header 1, USB end) -> G2
track("F.Cu", "+5V", [(BP_X[0], BP_Y1), (BP_X[0], 13.5), (14.6, 13.5), (14.6, 11.2), u(3)], 0.4)
# GND : S2 / S1 to the pours
track("F.Cu", "GND", [u(2), (14.0, 9.0)], 0.3); via("GND", 14.0, 9.0)
track("F.Cu", "GND", [u(5), (19.6, 9.0)], 0.3); via("GND", 19.6, 9.0)
# G1 <-> D2 <-> R1.1
track("F.Cu", "N_G1_D2", [u(1), (14.2, 7.3)]); via("N_G1_D2", 14.2, 7.3)
track("B.Cu", "N_G1_D2", [(14.2, 7.3), (13.0, 8.5), (13.0, 12.0), (21.0, 12.0)]); via("N_G1_D2", 21.0, 12.0)
track("F.Cu", "N_G1_D2", [(21.0, 12.0), R1p1])
track("F.Cu", "N_G1_D2", [u(4), (19.0, 9.95), (20.0, R1p1[1]), R1p1])
# D1 <-> R1.2 <-> nice!nano P1.06 (kept outside the antenna keep-out)
track("F.Cu", "N_D1", [u(6), (19.0, 8.05), (20.0, R1p2[1]), R1p2])
track("F.Cu", "N_D1", [R1p2, (21.0, 6.6)]); via("N_D1", 21.0, 6.6)
track("B.Cu", "N_D1", [(21.0, 6.6), (11.0, 6.6), (11.0, 19.4), (4.9, 19.4), (NANO_X[11], NANO_B)])

# ---------- zones ----------
poly = lambda pts: " ".join(f"(xy {f(OX+x)} {f(OY+y)})" for x, y in pts)
board = [(-BX, -BY), (BX, -BY), (BX, BY), (-BX, BY)]
zones = [f'''(zone (net {NI["GND"]}) (net_name "GND") (layer "{l}") (uuid "{U()}") (hatch edge 0.5)
  (connect_pads (clearance 0.3)) (min_thickness 0.25) (filled_areas_thickness no)
  (fill yes (thermal_gap 0.4) (thermal_bridge_width 0.4) (island_removal_mode 0))
  (polygon (pts {poly(board)})))''' for l in ("F.Cu", "B.Cu")]
a0, b0, a1, b1 = ANT
zones.append(f'''(zone (net 0) (net_name "") (layers "F.Cu" "B.Cu") (uuid "{U()}") (name "nRF_antenna_keepout") (hatch edge 0.5)
  (connect_pads (clearance 0)) (min_thickness 0.25) (filled_areas_thickness no)
  (keepout (tracks not_allowed) (vias not_allowed) (pads allowed) (copperpour not_allowed) (footprints allowed))
  (fill (thermal_gap 0.5) (thermal_bridge_width 0.5))
  (polygon (pts {poly([(a0, b0), (a1, b0), (a1, b1), (a0, b1)])})))''')

gr = [f'(gr_rect (start {f(OX-BX)} {f(OY-BY)}) (end {f(OX+BX)} {f(OY+BY)}) (stroke (width 0.1) (type default)) (fill no) (layer "Edge.Cuts") (uuid "{U()}"))',
      f'(gr_text "DMC2038LVT" (at {f(OX+17.0)} {f(OY+5.2)} 0) (layer "F.SilkS") (uuid "{U()}") (effects (font (size 0.9 0.9) (thickness 0.15))))',
      f'(gr_text "flat v2  2026-10-30" (at {f(OX+17.5)} {f(OY+17.6)} 0) (layer "F.SilkS") (uuid "{U()}") (effects (font (size 0.8 0.8) (thickness 0.15))))',
      f'(gr_text "IC CARD CONNECTOR AREA (TBD)" (at {f(OX)} {f(OY)} 0) (layer "B.SilkS") (uuid "{U()}") (effects (font (size 1.2 1.2) (thickness 0.18)) (justify mirror)))',
      f'(gr_text "ANT" (at {f(OX+7.6)} {f(OY+10.6)} 90) (layer "F.Fab") (uuid "{U()}") (effects (font (size 0.8 0.8) (thickness 0.12))))']

layers = """(layers
 (0 "F.Cu" signal) (2 "B.Cu" signal) (9 "F.Adhes" user "F.Adhesive") (11 "B.Adhes" user "B.Adhesive")
 (13 "F.Paste" user) (15 "B.Paste" user) (5 "F.SilkS" user "F.Silkscreen") (7 "B.SilkS" user "B.Silkscreen")
 (1 "F.Mask" user) (3 "B.Mask" user) (17 "Dwgs.User" user "User.Drawings") (19 "Cmts.User" user "User.Comments")
 (25 "Edge.Cuts" user) (27 "Margin" user) (31 "F.CrtYd" user "F.Courtyard") (29 "B.CrtYd" user "B.Courtyard")
 (35 "F.Fab" user) (33 "B.Fab" user))"""
pcb = f"""(kicad_pcb (version 20241229) (generator "pcbnew") (generator_version "9.0")
 (general (thickness 1.6) (legacy_teardrops no))
 (paper "A4")
 {layers}
 (setup
  (stackup
   (layer "F.SilkS" (type "Top Silk Screen"))
   (layer "F.Paste" (type "Top Solder Paste"))
   (layer "F.Mask" (type "Top Solder Mask") (color "Purple") (thickness 0.01))
   (layer "F.Cu" (type "copper") (thickness 0.035))
   (layer "dielectric 1" (type "core") (thickness 1.51) (material "FR4") (epsilon_r 4.5) (loss_tangent 0.02))
   (layer "B.Cu" (type "copper") (thickness 0.035))
   (layer "B.Mask" (type "Bottom Solder Mask") (color "Purple") (thickness 0.01))
   (layer "B.Paste" (type "Bottom Solder Paste"))
   (layer "B.SilkS" (type "Bottom Silk Screen"))
   (copper_finish "HAL lead-free") (dielectric_constraints no))
  (pad_to_mask_clearance 0) (allow_soldermask_bridges_in_footprints no))
{chr(10).join(f' (net {i} "{n}")' for i, n in enumerate(NETS))}
{chr(10).join(footprints)}
{chr(10).join(gr)}
{chr(10).join(items)}
{chr(10).join(zones)}
)
"""
name = "flat_pcb"
open(os.path.join(OUT, f"{name}.kicad_pcb"), "w", encoding="utf-8").write(pcb)
open(os.path.join(OUT, f"{name}.kicad_pro"), "w", encoding="utf-8").write(
    '{"board": {"design_settings": {"rule_severities": {"lib_footprint_issues": "ignore", "lib_footprint_mismatch": "ignore"}, '
    '"rules": {"min_clearance": 0.2, "min_track_width": 0.2, "min_via_diameter": 0.5, "min_through_hole_diameter": 0.3, "min_copper_edge_clearance": 0.3}}}, '
    f'"meta": {{"filename": "{name}.kicad_pro", "version": 3}}}}')

# ---------- simple VRML module models (absolute board coords; footprint origin = board centre) ----------
class M:
    def __init__(s): s.mesh = defaultdict(lambda: ([], []))
    def box(s, mat, x0, y0, z0, x1, y1, z1):
        x0, x1 = sorted((x0, x1)); y0, y1 = sorted((-y0, -y1)); z0, z1 = sorted((z0, z1))
        v, fc = s.mesh[mat]; b = len(v)
        for z in (z0, z1):
            v += [(x0, y0, z), (x1, y0, z), (x1, y1, z), (x0, y1, z)]
        fc += [[b+3, b+2, b+1, b], [b+4, b+5, b+6, b+7]] + [[b+i, b+(i+1) % 4, b+4+(i+1) % 4, b+4+i] for i in range(4)]
    def disk(s, mat, cx, cy, r, z0, z1, n=12):
        cy = -cy; v, fc = s.mesh[mat]; b = len(v)
        for z in (z0, z1):
            v += [(cx + r*math.cos(2*math.pi*i/n), cy + r*math.sin(2*math.pi*i/n), z) for i in range(n)]
        fc += [list(range(b+n-1, b-1, -1)), list(range(b+n, b+2*n))] + [[b+i, b+(i+1) % n, b+n+(i+1) % n, b+n+i] for i in range(n)]
    def diamond(s, mat, cx, cy, a, z0, z1):
        cy = -cy; v, fc = s.mesh[mat]; b = len(v)
        for z in (z0, z1):
            v += [(cx + a, cy, z), (cx, cy + a, z), (cx - a, cy, z), (cx, cy - a, z)]
        fc += [[b+3, b+2, b+1, b], [b+4, b+5, b+6, b+7]] + [[b+i, b+(i+1) % 4, b+4+(i+1) % 4, b+4+i] for i in range(4)]
    def write(s, path):
        col = {"pcb": "0.07 0.07 0.08", "silver": "0.8 0.8 0.82", "chip": "0.13 0.13 0.14", "gold": "0.85 0.66 0.28",
               "red": "0.8 0.12 0.12", "cap": "0.15 0.15 0.15", "white": "0.95 0.95 0.95"}
        with open(path, "w", encoding="utf-8") as fh:
            fh.write("#VRML V2.0 utf8\n")
            for mat, (v, fc) in s.mesh.items():
                pts = ",\n".join(f"{x/P:.4f} {y/P:.4f} {z/P:.4f}" for x, y, z in v)
                idx = ",".join(",".join(map(str, q)) + ",-1" for q in fc)
                fh.write(f"Shape {{ appearance Appearance {{ material Material {{ diffuseColor {col[mat]} specularColor 0.25 0.25 0.25 shininess 0.3 }} }}\n"
                         f" geometry IndexedFaceSet {{ solid FALSE creaseAngle 0.5 coord Coordinate {{ point [\n{pts}\n] }} coordIndex [ {idx} ] }} }}\n")
GAP, T = 0.5, 1.6
z0, z1 = 1.6 + GAP, 1.6 + GAP + T
bp = M(); cy = (BP_Y1 + BP_Y2) / 2
bp.box("pcb", -26.5, cy - 10.5, z0, 26.5, cy + 10.5, z1)
bp.box("silver", 26.5 - 7, cy - 4.5, z1, 28.0, cy + 4.5, z1 + 3.2)
bp.diamond("chip", 1.0, cy, 4.9, z1, z1 + 0.9)
for bx, by in ((-12.0, cy - 3.0), (13.5, cy - 4.0), (13.5, cy + 2.5)):
    bp.box("silver", bx - 2.2, by - 1.8, z1, bx + 2.2, by + 1.8, z1 + 1.6); bp.disk("cap", bx, by, 1.0, z1 + 1.6, z1 + 2.3)
for x in BP_X:
    for y in (BP_Y1, BP_Y2):
        bp.disk("gold", x, y, 0.85, z1, z1 + 0.05, 10); bp.box("gold", x - 0.32, y - 0.32, -1.0, x + 0.32, y + 0.32, z1 + 0.3)
bp.write(os.path.join(OUT, "flatpcb_blackpill.wrl"))
nn = M()
nn.box("pcb", NANO_CX - 16.65, NANO_CY - 9, z0, NANO_CX + 16.65, NANO_CY + 9, z1)
nn.box("silver", NANO_CX - 16.65 - 1.5, NANO_CY - 4.5, z1, NANO_CX - 16.65 + 7, NANO_CY + 4.5, z1 + 3.2)
nn.diamond("chip", NANO_CX + 1.5, NANO_CY, 4.9, z1, z1 + 0.9)
nn.box("red", NANO_CX + 12.2, NANO_CY - 1.5, z1, NANO_CX + 13.8, NANO_CY + 2.5, z1 + 0.6)
for x in NANO_X:
    for y in (NANO_T, NANO_B):
        nn.disk("gold", x, y, 0.85, z1, z1 + 0.05, 10); nn.box("gold", x - 0.32, y - 0.32, -1.0, x + 0.32, y + 0.32, z1 + 0.3)
nn.write(os.path.join(OUT, "flatpcb_nicenano.wrl"))
print("board %.1f x %.1f mm" % (2 * BX, 2 * BY))
