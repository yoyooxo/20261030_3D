"""Independent dimension check: parse the .kicad_pcb and compare against the ICA-609 datasheet + breadboard."""
import re, sys, math

src = open(sys.argv[1], encoding="utf-8").read()
pads = {}
for m in re.finditer(r'\(footprint "([^"]+)".*?\(at ([-\d.]+) ([-\d.]+)\)(.*?)\n \)', src, re.S):
    fx, fy, body = float(m.group(2)), float(m.group(3)), m.group(4)
    ref = re.search(r'"Reference" "(\w+)"', body).group(1)
    for p in re.finditer(r'\(pad "([^"]*)" (\w+) \w+ \(at ([-\d.]+) ([-\d.]+)\) \(size ([\d.]+) [\d.]+\) \(drill ([\d.]+)\)', body):
        pads[f"{ref}.{p.group(1)}"] = (fx + float(p.group(3)), fy + float(p.group(4)), float(p.group(5)), float(p.group(6)))
edge = [tuple(map(float, xy)) for xy in re.findall(r'\(xy ([-\d.]+) ([-\d.]+)\)', re.search(r'\(gr_poly \(pts (.*?)\) \(stroke', src).group(1))]

ok_all = True
def chk(name, got, want, tol=0.005):
    global ok_all
    ok = abs(got - want) <= tol
    ok_all &= ok
    print(f"{'OK ' if ok else 'BAD'} {name:<42} {got:8.3f}  (spec {want:.3f})")

BACK = re.search(r'\(footprint "card609:ICA-609_Type2" \(layer "B.Cu"\)', src) is not None
M = -1 if BACK else 1          # socket on the back: seen from the top the datasheet pattern is mirrored left-right
P = lambda k: (M * pads[k][0],) + pads[k][1:] if k.startswith("J1.") else pads[k]
print("== J1 socket pads vs datasheet 'Reference dimension for PCB layout' ==" + ("  [socket on BACK: x mirrored back to the datasheet view]" if BACK else ""))
for row in (("C1", "C2", "C3", "C4"), ("C5", "C6", "C7", "C8")):
    for a, b in zip(row, row[1:]):
        chk(f"{a}-{b} pitch", P("J1." + b)[0] - P("J1." + a)[0], 2.54)
    chk(f"{row[0]}-{row[3]} span", P("J1." + row[3])[0] - P("J1." + row[0])[0], 7.62)
for a, b in (("C1", "C5"), ("C2", "C6"), ("C3", "C7"), ("C4", "C8")):
    chk(f"{a}-{b} row spacing (38.10)", P("J1." + b)[1] - P("J1." + a)[1], 38.10)
    chk(f"{a}/{b} same x", P("J1." + b)[0] - P("J1." + a)[0], 0)
chk("C4-SW1 horizontal (3.81)", P("J1.SW1")[0] - P("J1.C4")[0], 3.81)
chk("C4/SW1 same row", P("J1.SW1")[1] - P("J1.C4")[1], 0)
chk("SW1-SW2 vertical (2.54)", P("J1.SW2")[1] - P("J1.SW1")[1], 2.54)
chk("SW1/SW2 same x", P("J1.SW2")[0] - P("J1.SW1")[0], 0)
for k in [k for k in pads if k.startswith("J1.") and k[3:]]:
    chk(f"{k} drill (1.00)", P(k)[3], 1.00)

print("== headers vs breadboard ==")
for j in ("J2", "J3"):
    for i in range(1, 5):
        chk(f"{j} pin{i}-pin{i+1} pitch", abs(P(f"{j}.{i}")[0] - P(f"{j}.{i+1}")[0]), 2.54)
for i in range(1, 6):
    chk(f"J2.{i}-J3.{i} row spacing (0.5\" = 12.70)", P(f"J3.{i}")[1] - P(f"J2.{i}")[1], 12.70)
cy = (P("J1.C1")[1] + P("J1.C5")[1]) / 2
chk("header rows centred on socket centre line", (P("J2.1")[1] + P("J3.1")[1]) / 2 - cy, 0)

print("== placement (informative) ==")
P = lambda k: pads[k]
d = 1 if P("J1.C5")[0] > P("J1.C8")[0] else -1  # direction from C8 towards C5 (towards the header side)
frame_left = P("J1.C5")[0] + d * (22.08 + 2.0)  # snap hole 22.08 past C5, frame 2.0 beyond the hole (62 vs 58)
frame_bot = cy + 20.0
print(f"    socket frame edge -> header pin 1 (nearest)        {abs(frame_left - P('J2.1')[0]):6.2f} mm")
print(f"    C1 pin -> header pin 1, horizontal                  {abs(P('J1.C1')[0] - P('J2.1')[0]):6.2f} mm")
print(f"    header pin 1 -> pin 5                               {abs(P('J2.1')[0] - P('J2.5')[0]):6.2f} mm")
xs = [x for x, _ in edge]; ys = [y for _, y in edge]
print(f"    board bbox {max(xs)-min(xs):.2f} x {max(ys)-min(ys):.2f} mm")
ux = sorted(set(xs)); full = [x for x in ux if max(y for X_, y in edge if X_ == x) - min(y for X_, y in edge if X_ == x) > 30]
tip = [x for x in ux if x not in full][0]; inner = min(full, key=lambda x: abs(x - tip))
print(f"    T stem width {max(full)-min(full):.2f} mm, tongue length {abs(inner-tip):.2f} mm, tongue height {sorted(set(ys))[2]-sorted(set(ys))[1]:.2f} mm")

def seg_d(px, py, a, b):
    (x0, y0), (x1, y1) = a, b
    dx, dy = x1 - x0, y1 - y0
    t = max(0, min(1, ((px - x0) * dx + (py - y0) * dy) / (dx * dx + dy * dy)))
    return math.hypot(px - x0 - t * dx, py - y0 - t * dy)
m = min((seg_d(x, y, edge[i], edge[(i + 1) % len(edge)]) - s / 2, k) for k, (x, y, s, d) in pads.items() for i in range(len(edge)))
print(f"    min pad-to-board-edge {m[0]:.2f} mm ({m[1]})")
print("ALL SPEC CHECKS PASS" if ok_all else "SOME CHECKS FAILED")
