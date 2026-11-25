"""2D drawings read back from card609_breakout.kicad_pcb (v2: socket hangs under the PCB, breadboard on the right):
  配置圖_麵包板.png  - same style as the reference: top view on a 400-point breadboard + side view
  尺寸圖.png         - every distance on the board, in mm
usage: python gen_drawings.py   (after gen_breakout.py)"""
import os, re
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon, Circle, FancyArrowPatch

plt.rcParams["font.family"] = ["Microsoft JhengHei", "DejaVu Sans"]
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, "card609_breakout.kicad_pcb"), encoding="utf-8").read()

# ---- read geometry back (board top view, origin = J1 footprint origin, y down) ----
fps = {}
for m in re.finditer(r'\(footprint "([^"]+)" \(layer "([FB]).Cu"\).*?\(at ([-\d.]+) ([-\d.]+)\)(.*?)\n \)', src, re.S):
    ref = re.search(r'"Reference" "(\w+)"', m.group(5)).group(1)
    fps[ref] = (float(m.group(3)), float(m.group(4)), m.group(5), m.group(2))
OX, OY = fps["J1"][:2]
pads = {}
for ref, (fx, fy, body, _) in fps.items():
    for p in re.finditer(r'\(pad "([^"]*)" \w+ \w+ \(at ([-\d.]+) ([-\d.]+)\) \(size ([\d.]+)', body):
        if p.group(1):
            pads[f"{ref}.{p.group(1)}"] = (fx + float(p.group(2)) - OX, fy + float(p.group(3)) - OY, float(p.group(4)))
edge = [(float(a) - OX, float(b) - OY) for a, b in
        re.findall(r'\(xy ([-\d.]+) ([-\d.]+)\)', re.search(r'\(gr_poly \(pts (.*?)\) \(stroke \(width 0.1\)', src).group(1))]
segs = [tuple(float(v) for v in s) for s in re.findall(r'\(segment \(start ([-\d.]+) ([-\d.]+)\) \(end ([-\d.]+) ([-\d.]+)\) \(width ([\d.]+)\)', src)]
segs = [(a - OX, b - OY, c - OX, d - OY, w) for a, b, c, d, w in segs]
rects = re.findall(r'\(fp_rect \(start ([-\d.]+) ([-\d.]+)\) \(end ([-\d.]+) ([-\d.]+)\) \(stroke \(width 0.1\) \(type (\w+)\)\) \(fill no\) \(layer "[FB].Fab"\)', fps["J1"][2])
norm = lambda r: (min(float(r[0]), float(r[2])), min(float(r[1]), float(r[3])), max(float(r[0]), float(r[2])), max(float(r[1]), float(r[3])))
FX0, FY0, FX1, FY1 = norm([r for r in rects if r[4] == "default"][0])
CX0, CY0, CX1, CY1 = norm([r for r in rects if r[4] == "dash"][0])
BACK = fps["J1"][3] == "B"
P = lambda k: pads[k][:2]
J2N = ["C1", "C2", "C3", "C4", "SW1"]; J3N = ["C5", "C6", "C7", "C8", "SW2"]
ys = sorted({y for _, y in edge})
BY0, TY0, TY1, BY1 = ys
span = lambda x: max(y for X_, y in edge if X_ == x) - min(y for X_, y in edge if X_ == x)
full = sorted(x for x in {x for x, _ in edge} if span(x) > 30)
TIP = [x for x in {x for x, _ in edge} if x not in full][0]
S0, S1 = full                                  # stem edges
SIN = S1 if abs(S1 - TIP) < abs(S0 - TIP) else S0   # stem edge on the tongue side
SOUT = S0 if SIN == S1 else S1
DIR = 1 if TIP > SIN else -1                   # +1: tongue/breadboard to the right

GREEN, GOLD, TRACE, CARDC = "#ffffff", "#d4a017", "#4a7fd0", "#9cc8f0"
BBC, HOLE, MAG = "#f1efe9", "#555555", "#e0218a"
T, HP, BB_H, SOCK_H, PIN_DN = 1.6, 2.5, 8.5, 6.25 - 2.80, 2.80

# breadboard (400 points), d1 = J2 pin 1; its end is 5 mm before column 1 (assumed, measure yours)
BB_RM, BB_L, BB_W = 5.0, 83.5, 54.5
d1 = P("J2.1")
colx = lambda c: d1[0] + DIR * (c - 1) * 2.54
ROWS = {"a": -7.62, "b": -5.08, "c": -2.54, "d": 0, "e": 2.54, "f": 10.16, "g": 12.7, "h": 15.24, "i": 17.78, "j": 20.32}
RAILS = (-13.97, -16.51, 26.67, 29.21)
bxa = d1[0] - DIR * BB_RM
bxb = bxa + DIR * BB_L
bx0, bx1 = min(bxa, bxb), max(bxa, bxb)
by0 = d1[1] + 6.35 - BB_W / 2


def draw_pcb(ax, labels=True):
    ax.add_patch(Polygon(edge, closed=True, fc=GREEN, ec="#000000", lw=1.4, zorder=3))
    for x0, y0, x1, y1, w in segs:
        ax.plot([x0, x1], [y0, y1], color=TRACE, lw=1.6, solid_capstyle="round", zorder=4)
    for k, (x, y, s) in pads.items():
        ax.add_patch(Circle((x, y), s / 2, fc=GOLD, ec="#7a5c00", lw=0.6, zorder=5))
        ax.add_patch(Circle((x, y), 0.5, fc="white", ec="none", zorder=6))
    if labels:
        for n in J2N + J3N:
            x, y = P("J1." + n)
            sw = n.startswith("SW")
            ax.text(x - DIR * 2.4 if sw else x, y if sw else (y - 1.8 if y < 19 else y + 2.1),
                    n, ha="center", va="center", fontsize=6.5, color="black", zorder=7)


# =====================================================================
# 1) reference-style placement drawing
# =====================================================================
fig = plt.figure(figsize=(15, 14))
ax = fig.add_axes([0.03, 0.31, 0.94, 0.64])
ax.add_patch(Rectangle((bx0, by0), BB_L, BB_W, fc=BBC, ec="#999", lw=1, zorder=1))
ax.add_patch(Rectangle((bx0 + 2, d1[1] + 5.1), BB_L - 4, 2.5, fc="#dedad0", ec="none", zorder=1))
for r, dy in ROWS.items():
    y = d1[1] + dy
    ax.text(bxb - DIR * 1.6, y, r, ha="center", va="center", fontsize=7, color="#777", zorder=2)
    for c in range(1, 31):
        ax.add_patch(Rectangle((colx(c) - 0.5, y - 0.5), 1, 1, fc=HOLE, ec="none", zorder=2))
for c in (1, 5, 10, 15, 20, 25, 30):
    ax.text(colx(c), d1[1] - 10.2, str(c), ha="center", fontsize=7, color="#777", zorder=2)
for ry in RAILS:
    y = d1[1] + ry
    for c in range(1, 30):
        if c % 6:
            x = colx(c) + DIR * 2.54
            ax.add_patch(Rectangle((x - 0.5, y - 0.5), 1, 1, fc=HOLE, ec="none", zorder=2))
    col = "#d33" if ry in (-13.97, 26.67) else "#33c"
    yl = y + (1.6 if ry in (-13.97, 29.21) else -1.6)
    ax.plot([bx0 + 3, bx1 - 3], [yl, yl], color=col, lw=1, zorder=2)

# socket + card are UNDER the PCB: draw them first, PCB on top, then a dashed frame outline over everything
ax.add_patch(Rectangle((CX0, CY0), CX1 - CX0, CY1 - CY0, fc=CARDC, ec="#5f97c9", lw=1, ls="--", alpha=0.45, zorder=2.4))
ax.add_patch(Rectangle((FX0, FY0), FX1 - FX0, FY1 - FY0, fc="#555", ec="#222", lw=1.2, alpha=0.55, zorder=2.5))
draw_pcb(ax)
ax.add_patch(Rectangle((FX0, FY0), FX1 - FX0, FY1 - FY0, fc="none", ec="#111", lw=1.2, ls="--", zorder=8))
ax.text(FX0 + 1, FY0 + 2.2, "卡座 ICA-609 Type2（62 × 40）在 PCB 底下", fontsize=9, color="white", zorder=9)
for names, j in ((J2N, "J2"), (J3N, "J3")):
    for i in range(5):
        x, y = P(f"{j}.{i+1}")
        ax.add_patch(Circle((x, y), 1.25, fc="none", ec=MAG, lw=1.4, zorder=9))
        ax.text(x, y + (-2.2 if j == "J2" else 2.4), names[i], ha="center", va="center", fontsize=7.5, color=MAG, weight="bold", zorder=9)
tx = d1[0] + DIR * 16
ax.text(tx, d1[1] - 4.4, "← J2 插 d1 d2 d3 d4 d5 ＝ C1 C2 C3 C4 SW1", fontsize=9.5, color=MAG, ha="left" if DIR > 0 else "right", zorder=9,
        bbox=dict(fc="white", ec="none", alpha=0.85))
ax.text(tx, d1[1] + 17.4, "← J3 插 g1 g2 g3 g4 g5 ＝ C5 C6 C7 C8 SW2", fontsize=9.5, color=MAG, ha="left" if DIR > 0 else "right", zorder=9,
        bbox=dict(fc="white", ec="none", alpha=0.85))
mx = (CX0 + CX1) / 2
ax.add_patch(FancyArrowPatch((mx, CY1 + 12), (mx, CY1 - 3), arrowstyle="-|>", mutation_scale=22, lw=2.5, color="#1f4e8c", zorder=9))
ax.text(mx, CY1 + 15, "IC 卡 85.6 × 54（晶片朝上，從下方往上推入）", ha="center", fontsize=11, color="#1f4e8c", zorder=9)
ax.set_xlim(min(FX0, bx0) - 3, max(FX1, bx1) + 3)
ax.set_ylim(CY1 + 19, by0 - 8)
ax.set_aspect("equal"); ax.axis("off")
ax.set_title("讀卡座轉接板（純 T 字、單層 F.Cu）插在 400 孔麵包板上　俯視圖，單位 mm\n"
             "卡座吊在 PCB 底下、在麵包板旁邊；排針插 d1–d5 與 g1–g5（第 1 欄靠卡座）", fontsize=13)

# side view (looking from the card-entry edge), z = 0 at the table
az = fig.add_axes([0.03, 0.02, 0.94, 0.26])
zbb = BB_H                       # breadboard top
zpb = zbb + HP                   # PCB bottom
zpt = zpb + T                    # PCB top
az.plot([min(FX0, bx0) - 3, max(FX1, bx1) + 3], [0, 0], color="#888", lw=1)
az.text(max(FX1, bx1) + 2, 0.6, "桌面", ha="right", fontsize=9, color="#666")
az.add_patch(Rectangle((bx0, 0), BB_L, BB_H, fc=BBC, ec="#999"))
az.text(bx1 - 3, 3.0, "麵包板（高約 8.5）", fontsize=10, ha="right")
xs_e = sorted({x for x, _ in edge})
az.add_patch(Rectangle((xs_e[0], zpb), xs_e[-1] - xs_e[0], T, fc=GREEN, ec="#000000"))
az.text(SOUT + DIR * 2, zpt + 2.4, "PCB 1.6（銅箔、焊點都在上面）", fontsize=9, color="#1b4030", ha="left" if DIR > 0 else "right")
hx = [P(f"J2.{i+1}")[0] for i in range(5)]
az.add_patch(Rectangle((min(hx) - 1.27, zbb), max(hx) - min(hx) + 2.54, HP, fc="#222"))
for x in hx:
    az.plot([x, x], [zbb - 6.0 + 0.0, zpt + 1.4], color=GOLD, lw=2.2)
az.text(max(hx) + 2 if DIR > 0 else min(hx) - 2, zpt + 1.2, "排針塑膠座在 PCB 和麵包板中間", fontsize=9)
az.add_patch(Rectangle((FX0, zpb - SOCK_H), FX1 - FX0, SOCK_H, fc="#333", ec="#000", alpha=0.9))
for n in ("C1", "C2", "C3", "C4", "SW1"):
    x = P("J1." + n)[0]
    az.plot([x, x], [zpb, zpb + PIN_DN], color=GOLD, lw=2)
az.add_patch(Rectangle((CX0, zpb - 1.9 - 0.76), CX1 - CX0, 0.76, fc=CARDC, ec="#5f97c9"))
az.text((FX0 + FX1) / 2, zpb - SOCK_H - 2.2, "卡座吊在 PCB 底下（高約 3.45），IC 卡在卡座裡、晶片朝上", ha="center", fontsize=9)
# dims: socket bottom above table, gap socket <-> breadboard, PCB top above table
zs = zpb - SOCK_H
xd = SOUT - DIR * 0 if False else (FX0 + 4 if DIR > 0 else FX1 - 4)
az.annotate("", xy=(xd, 0), xytext=(xd, zs), arrowprops=dict(arrowstyle="<->", lw=1, color="#c0392b"))
az.text(xd + 1, zs / 2, f"{zs:.2f}", fontsize=9, color="#c0392b", va="center")
gx0, gx1 = (FX1, bx0) if DIR > 0 else (bx1, FX0)
az.annotate("", xy=(gx0, zs + 1), xytext=(gx1, zs + 1), arrowprops=dict(arrowstyle="<->", lw=1, color="#c0392b"))
az.text((gx0 + gx1) / 2, zs - 1.8, f"{abs(gx1 - gx0):.1f}", ha="center", fontsize=9, color="#c0392b")
xr = max(hx) + 30 if DIR > 0 else min(hx) - 30
az.annotate("", xy=(xr, 0), xytext=(xr, zpt), arrowprops=dict(arrowstyle="<->", lw=1, color="#c0392b"))
az.text(xr + 1, zpt / 2 + 2, f"PCB 頂面\n{zpt:.1f}", fontsize=9, color="#c0392b", va="center")
az.set_xlim(min(FX0, bx0) - 3, max(FX1, bx1) + 3); az.set_ylim(-3, zpt + 6)
az.set_aspect("equal"); az.axis("off")
az.set_title("側視圖（從插卡口看過去，單位 mm，高度依規格書推算，麵包板高度請實量）", fontsize=11)
fig.savefig(os.path.join(HERE, "配置圖_麵包板.png"), dpi=130)
plt.close(fig)

# =====================================================================
# 2) dimension drawing
# =====================================================================
fig, ax = plt.subplots(figsize=(17, 12.5))
ax.add_patch(Rectangle((FX0, FY0), FX1 - FX0, FY1 - FY0, fc="none", ec="#999", lw=1, ls="--", zorder=2))
ax.text(FX0 + 1, FY0 + 1.6, "卡座外框（虛線，在 PCB 底下）62 × 40", ha="left", fontsize=9, color="#777")
draw_pcb(ax)
for j, names in (("J2", J2N), ("J3", J3N)):
    for i in range(5):
        x, y = P(f"{j}.{i+1}")
        ax.text(x, y + (-1.9 if j == "J2" else 2.0), names[i], ha="center", va="center", fontsize=6.5, color="black", zorder=7)
DC = "#c0392b"


def hdim(x0, x1, y, yref0, yref1, txt, above=True):
    for x, yr in ((x0, yref0), (x1, yref1)):
        ax.plot([x, x], [yr, y + (-0.6 if above else 0.6)], color=DC, lw=0.5, zorder=9)
    ax.annotate("", xy=(x0, y), xytext=(x1, y), arrowprops=dict(arrowstyle="<|-|>", color=DC, lw=0.9, mutation_scale=9), zorder=9)
    ax.text((x0 + x1) / 2, y + (-0.6 if above else 0.9), txt, ha="center", va="bottom" if above else "top", fontsize=9, color=DC, zorder=10,
            bbox=dict(fc="white", ec="none", pad=0.4, alpha=0.85))


def vdim(y0, y1, x, xref0, xref1, txt, left=True):
    for y, xr in ((y0, xref0), (y1, xref1)):
        ax.plot([xr, x + (0.6 if left else -0.6)], [y, y], color=DC, lw=0.5, zorder=9)
    ax.annotate("", xy=(x, y0), xytext=(x, y1), arrowprops=dict(arrowstyle="<|-|>", color=DC, lw=0.9, mutation_scale=9), zorder=9)
    ax.text(x + (-0.7 if left else 0.7), (y0 + y1) / 2, txt, ha="right" if left else "left", va="center", fontsize=9, color=DC, zorder=10,
            bbox=dict(fc="white", ec="none", pad=0.4, alpha=0.85))


c1, c4, c5, c8 = P("J1.C1"), P("J1.C4"), P("J1.C5"), P("J1.C8")
sw1, sw2 = P("J1.SW1"), P("J1.SW2")
h21, h25, h31 = P("J2.1"), P("J2.5"), P("J3.1")
L, R = min(S0, TIP), max(S1, TIP)
out_side = SOUT                                   # stem edge away from the tongue
far = lambda d: out_side - DIR * d                # x beyond the stem's outer edge
tipx = lambda d: TIP + DIR * d                    # x beyond the tongue tip
# overall
hdim(L, R, BY0 - 7, BY0 if L == S0 else TY0, TY0 if R == TIP else BY0, f"板子總寬 {R - L:.2f}")
vdim(BY0, BY1, far(11), out_side, out_side, f"板子總高\n{BY1 - BY0:.2f}", left=DIR > 0)
hdim(S0, S1, BY1 + 4.5, BY1, BY1, f"直條寬 {S1 - S0:.2f}", above=False)
hdim(min(SIN, TIP), max(SIN, TIP), TY1 + 4.5, TY1, TY1, f"舌片長 {abs(TIP - SIN):.2f}", above=False)
vdim(TY0, TY1, tipx(8), TIP, TIP, f"舌片高\n{TY1 - TY0:.2f}", left=DIR < 0)
vdim(BY0, TY0, SIN + DIR * 3, SIN, SIN, f"{TY0 - BY0:.2f}", left=DIR < 0)
vdim(TY1, BY1, SIN + DIR * 3, SIN, SIN, f"{BY1 - TY1:.2f}", left=DIR < 0)
# socket pins
hdim(min(c1[0], c4[0]), max(c1[0], c4[0]), BY0 - 2.5, c1[1] - 1, c4[1] - 1, f"C1–C4 {abs(c4[0] - c1[0]):.2f}（腳距 2.54）")
hdim(min(c4[0], sw1[0]), max(c4[0], sw1[0]), BY0 - 4.8, c4[1] - 1, sw1[1] - 1, f"{abs(sw1[0] - c4[0]):.2f}")
vdim(sw1[1], sw2[1], far(2.5), sw1[0] - DIR, sw2[0] - DIR, f"{sw2[1] - sw1[1]:.2f}", left=DIR > 0)
vdim(c4[1], c8[1], far(6), c4[0] - DIR, c8[0] - DIR, f"C1–C5 兩排\n{c5[1] - c1[1]:.2f}", left=DIR > 0)
hdim(min(SIN, c1[0]), max(SIN, c1[0]), BY1 + 1.6, BY1 if True else 0, c5[1] + 1, f"{abs(c1[0] - SIN):.2f}", above=False)
hdim(min(c8[0], SOUT), max(c8[0], SOUT), BY1 + 1.6, c8[1] + 1, BY1, f"{abs(SOUT - c8[0]):.2f}", above=False)
vdim(BY0, c1[1], SIN + DIR * 6.5, SIN, c1[0] + DIR, f"{c1[1] - BY0:.2f}", left=DIR < 0)
vdim(c5[1], BY1, SIN + DIR * 6.5, c5[0] + DIR, SIN, f"{BY1 - c5[1]:.2f}", left=DIR < 0)
# headers
hdim(min(h25[0], h21[0]), max(h25[0], h21[0]), TY0 - 3.2, h25[1] - 1, h21[1] - 1, f"排針 1–5 腳 {abs(h21[0] - h25[0]):.2f}（腳距 2.54）")
hdim(min(TIP, h25[0]), max(TIP, h25[0]), TY0 - 6.5, TY0, h25[1] - 1, f"{abs(h25[0] - TIP):.2f}")
vdim(h21[1], h31[1], tipx(4.5), h25[0] + DIR, h25[0] + DIR, f"兩排排針\n{h31[1] - h21[1]:.2f}\n（0.5\"）", left=DIR < 0)
vdim(TY0, h21[1], tipx(1.5), TIP, h25[0] + DIR, f"{h21[1] - TY0:.2f}", left=DIR < 0)
hdim(min(h21[0], c1[0]), max(h21[0], c1[0]), (h21[1] + h31[1]) / 2 - 1.2, h21[1] + 1, c1[1] + 1, f"排針第 1 腳 → C1：{abs(c1[0] - h21[0]):.2f}")
fe = FX1 if DIR > 0 else FX0
hdim(min(h21[0], fe), max(h21[0], fe), TY1 + 8.5, h31[1] + 1, FY1, f"排針第 1 腳 → 卡座框邊 {abs(fe - h21[0]):.2f}", above=False)
cy = (c1[1] + c5[1]) / 2
ax.plot([min(FX0, L) - 1, max(FX1, R) + 2], [cy, cy], color="#888", lw=0.6, ls="-.", zorder=8)
ax.text(min(FX0, L) - 1.5, cy, "卡座中心線\n（排針兩排上下對稱）", fontsize=8, color="#666", va="center", ha="right")
ax.text(min(FX0, L), BY1 + 10.5,
        "孔徑：卡座 10 孔 Ø1.00（焊盤 Ø1.8）｜排針 10 孔 Ø1.00（焊盤 Ø1.7）｜走線寬 0.40、全部在 F.Cu（正面）\n"
        "卡座裝在背面、腳從下面穿上來在正面焊；從正面看腳位是規格書「Reference dimension for PCB layout」的左右鏡像（公差 ±0.05）\n"
        f"卡座框邊 → 麵包板邊緣的空隙 ≈ {abs(fe - h21[0]) - BB_RM:.1f}（假設麵包板第 1 欄到板邊 {BB_RM:.1f}，請實際量）",
        fontsize=10, va="top")
ax.set_xlim(min(FX0, L) - 14, max(FX1, R) + 14)
ax.set_ylim(BY1 + 16, BY0 - 10)
ax.set_aspect("equal"); ax.axis("off")
ax.set_title("讀卡座轉接板 尺寸圖（俯視、正面，單位 mm）", fontsize=15)
fig.tight_layout()
fig.savefig(os.path.join(HERE, "尺寸圖.png"), dpi=130)
print("ok")
