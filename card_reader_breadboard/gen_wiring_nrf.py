"""接線圖_含nRF.png: the ICA-609 breakout + nRF52840 SuperMini (nice!nano pinout) on one 400-point breadboard,
with every jumper wire, wired like the teacher's board (card GND on B-, I/O on P0.22 with P0.20 tied to it,
battery + on RAW, B+ left open).
usage: python gen_wiring_nrf.py   (reuses the geometry part of gen_drawings.py)"""
import os, itertools
HERE = os.path.dirname(os.path.abspath(__file__))
_src = open(os.path.join(HERE, "gen_drawings.py"), encoding="utf-8").read()
exec(_src.split("# =====================================================================\n# 1)")[0])   # geometry + draw_pcb only

import matplotlib.patheffects as pe

# ---------------- module: USB-C to the right, pins in rows d (top) and h (bottom), columns 18-30 ----------------
MC0, MC1 = 18, 30
TOP = ["P1.06", "P1.04", "P0.11", "P1.00", "P0.24", "P0.22", "P0.20", "P0.17", "GND", "GND", "P0.08", "P0.06", "B-"]   # row d, col 18..30
BOT = ["P0.09", "P0.10", "P1.11", "P1.13", "P1.15", "P0.02", "P0.29", "P0.31", "VCC", "RST", "GND", "RAW", "B+"]        # row h, col 18..30
hole = lambda r, c: (colx(c), d1[1] + ROWS[r])

# ---------------- wires: (colour, label, from hole, to hole, purpose) ----------------
WIRES = [
    ("#d62728", "W1", ("a", 1), ("j", 26), "C1 VCC → VCC"),
    ("#1f77b4", "W2", ("b", 2), ("b", 22), "C2 RST → P0.24"),
    ("#2ca02c", "W3", ("a", 3), ("a", 25), "C3 CLK → P0.17"),
    ("#9467bd", "W4", ("b", 5), ("b", 21), "SW1 插卡偵測 → P1.00"),
    ("#333333", "W5", ("j", 1), ("a", 30), "C5 GND → B-（照老師）"),
    ("#e6b800", "W6", ("j", 3), ("a", 23), "C7 I/O → P0.22"),
    ("#7f7f7f", "W7", ("i", 5), ("i", 28), "SW2 → GND"),
]
CROSS_X = {"W1": 8.5, "W6": 11.5, "W5": 14.5}          # columns (between holes) where a wire crosses the middle gap
side = lambda r: "T" if r in "abcde" else "B"

# horizontal runs per side: (wire, x0, x1) in column units; vertical drops at the ends
runs = {"T": [], "B": []}
for col, lab, (r0, c0), (r1, c1), _ in WIRES:
    if side(r0) == side(r1):
        runs[side(r0)].append((lab, c0, c1))
    else:
        xc = CROSS_X[lab]
        runs[side(r0)].append((lab, c0, xc))
        runs[side(r1)].append((lab, xc, c1))


def best_order(rs):
    """lane order (index 0 = nearest the breadboard) with the fewest wire crossings"""
    best = None
    for perm in itertools.permutations(range(len(rs))):
        k = {rs[i][0]: perm[i] for i in range(len(rs))}
        n = 0
        for a in rs:
            lo, hi = sorted(a[1:])
            for b in rs:
                if b is a or k[b[0]] <= k[a[0]]:
                    continue
                n += sum(lo < x < hi for x in b[1:])
        if best is None or n < best[0]:
            best = (n, k)
    return best


ordT, ordB = best_order(runs["T"]), best_order(runs["B"])
print("crossings: top", ordT[0], "bottom", ordB[0])
LANE0_T, LANE0_B, LSTEP = by0 - 3.0, by0 + BB_W + 3.0, 2.6
laneT = {k: LANE0_T - v * LSTEP for k, v in ordT[1].items()}
laneB = {k: LANE0_B + v * LSTEP for k, v in ordB[1].items()}
X = lambda c: colx(c)

# ---------------- figure ----------------
fig = plt.figure(figsize=(17, 17))
ax = fig.add_axes([0.02, 0.24, 0.96, 0.72])
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
    colr = "#d33" if ry in (-13.97, 26.67) else "#33c"
    yl = y + (1.6 if ry in (-13.97, 29.21) else -1.6)
    ax.plot([bx0 + 3, bx1 - 3], [yl, yl], color=colr, lw=1, zorder=2)

# socket, card, breakout PCB
ax.add_patch(Rectangle((CX0, CY0), CX1 - CX0, CY1 - CY0, fc=CARDC, ec="#5f97c9", lw=1, ls="--", alpha=0.45, zorder=2.4))
ax.add_patch(Rectangle((FX0, FY0), FX1 - FX0, FY1 - FY0, fc="#555", ec="#222", lw=1.2, alpha=0.55, zorder=2.5))
draw_pcb(ax)
ax.add_patch(Rectangle((FX0, FY0), FX1 - FX0, FY1 - FY0, fc="none", ec="#111", lw=1.2, ls="--", zorder=8))
ax.text(FX0 + 1, FY1 - 1.5, "卡座 ICA-609（在轉接板底下）", fontsize=9, color="white", zorder=9)
mx = (CX0 + CX1) / 2
ax.add_patch(FancyArrowPatch((mx, CY1 + 12), (mx, CY1 - 3), arrowstyle="-|>", mutation_scale=22, lw=2.5, color="#1f4e8c", zorder=9))
ax.text(mx, CY1 + 15, "IC 卡（晶片朝上，從下方往上推入）", ha="center", fontsize=11, color="#1f4e8c", zorder=9)
for names, j, dy in ((J2N, "J2", -2.0), (J3N, "J3", 2.2)):
    for i in range(5):
        x, y = P(f"{j}.{i+1}")
        ax.text(x, y + dy, names[i], ha="center", va="center", fontsize=6.5, color=MAG, weight="bold", zorder=9,
                bbox=dict(fc="white", ec="none", pad=0.3, alpha=0.8))

# nRF52840 SuperMini
yd, yh = d1[1] + ROWS["d"], d1[1] + ROWS["h"]
mx0, mx1 = X(MC0) - 1.6, X(MC1) + 1.6
ax.add_patch(Rectangle((mx0, yd - 1.4), mx1 - mx0, yh - yd + 2.8, fc="#1d3557", ec="#0b1a2e", lw=1.2, zorder=10))
ax.add_patch(Rectangle((mx1 - 0.6, (yd + yh) / 2 - 4.5), 4.0, 9.0, fc="#b8bcc2", ec="#666", lw=1, zorder=10.5))
ax.text(mx1 + 1.4, (yd + yh) / 2, "USB-C", rotation=90, ha="center", va="center", fontsize=7, zorder=11)
ax.text((mx0 + mx1) / 2 - 1, (yd + yh) / 2, "nRF52840 SuperMini\n（nice!nano 腳位，USB 朝右）",
        ha="center", va="center", fontsize=9, color="white", zorder=11)
used = {"P0.24", "P0.17", "P1.00", "P0.22", "P0.20", "B-", "VCC", "RAW"}
for names, y, dy in ((TOP, yd, 2.0), (BOT, yh, -2.0)):
    for i, n in enumerate(names):
        x = X(MC0 + i)
        ax.add_patch(Circle((x, y), 0.75, fc=GOLD, ec="#7a5c00", lw=0.6, zorder=11))
        hot = n in used or (n == "GND" and names is BOT)
        ax.text(x, y + dy, n, ha="center", va="center", fontsize=6.2, rotation=90, zorder=11,
                color="#ffd166" if hot else "#c9d3e0", weight="bold" if hot else "normal")

# wires
OUT = [pe.Stroke(linewidth=4.6, foreground="white"), pe.Normal()]


def wire(pts, col, z=12):
    ax.plot([p[0] for p in pts], [p[1] for p in pts], color=col, lw=2.6, solid_joinstyle="round",
            solid_capstyle="round", zorder=z, path_effects=OUT)
    for p in (pts[0], pts[-1]):
        ax.add_patch(Circle(p, 0.7, fc=col, ec="white", lw=0.8, zorder=z + 0.5))


for col, lab, (r0, c0), (r1, c1), _ in WIRES:
    p0, p1 = hole(r0, c0), hole(r1, c1)
    if lab == "W7":       # shares column 28 with the battery minus lead: come in beside it
        yl = laneB[lab]
        wire([p0, (p0[0], yl), (X(c1) - 1.1, yl), (X(c1) - 1.1, p1[1]), p1], col)
    elif side(r0) == side(r1):
        yl = (laneT if side(r0) == "T" else laneB)[lab]
        wire([p0, (p0[0], yl), (p1[0], yl), p1], col)
    else:
        y0 = (laneT if side(r0) == "T" else laneB)[lab]
        y1 = (laneT if side(r1) == "T" else laneB)[lab]
        xc = X(CROSS_X[lab])
        wire([p0, (p0[0], y0), (xc, y0), (xc, y1), (p1[0], y1), p1], col)
    # tag near the far end
    ax.text(p1[0] + 1.2, (laneT if side(r1) == "T" else laneB)[lab], lab, fontsize=7.5, color=col, va="center",
            weight="bold", zorder=13, bbox=dict(fc="white", ec="none", pad=0.2))
# I/O pair: P0.20 (c24) tied to P0.22 (c23), short jumper in row b
wire([hole("b", 23), hole("b", 24)], "#e6b800", z=13)
ax.text(X(23.5), d1[1] + ROWS["b"] - 1.4, "W8", fontsize=7.5, color="#b08900", ha="center", weight="bold", zorder=13)

# battery (taped down below the breadboard), + to RAW (c29), - to GND (c28)
bt_y0 = max(laneB.values()) + 4
bx_ = X(28.5)
ax.add_patch(Rectangle((bx_ - 11.5, bt_y0), 23, 13, fc="#d9dce1", ec="#666", lw=1.2, zorder=10))
ax.text(bx_, bt_y0 + 7.5, "LiPo 電池（約 13 × 23）", ha="center", va="center", fontsize=9, zorder=11)
wire([(X(29), bt_y0), hole("j", 29)], "#d62728")
wire([(X(28), bt_y0), hole("j", 28)], "#111111")
ax.text(X(29) + 0.9, bt_y0 - 1.6, "W9 ＋→RAW", fontsize=7.5, color="#d62728", weight="bold", zorder=13)
ax.text(X(28) - 0.9, bt_y0 - 1.6, "W10 －→GND", fontsize=7.5, color="#111", weight="bold", ha="right", zorder=13)

ax.set_xlim(min(FX0, bx0) - 3, max(mx1 + 6, bx_ + 14))
ax.set_ylim(max(CY1 + 19, bt_y0 + 16), min(laneT.values()) - 3)
ax.set_aspect("equal"); ax.axis("off")
ax.set_title("讀卡機接線圖：ICA-609 轉接板＋nRF52840 SuperMini 插在同一塊 400 孔麵包板（俯視）\n"
             "轉接板排針插 d1–d5／g1–g5；模組插 d18–d30／h18–h30、USB-C 朝右；接法照老師的板子", fontsize=13)

# wire table
at = fig.add_axes([0.06, 0.01, 0.88, 0.2]); at.axis("off")
ROWS_T = [(c, l, f"{r0}{c0}", f"{r1}{c1}", u) for c, l, (r0, c0), (r1, c1), u in WIRES] + [
    ("#e6b800", "W8", "b23", "b24", "P0.22 ↔ P0.20 併接（老師用短跳線）"),
    ("#d62728", "W9", "電池 ＋", "j29", "電池＋ → RAW（B+ 空著）"),
    ("#111111", "W10", "電池 －", "j28", "電池－ → GND"),
    ("#cccccc", "—", "d4、g2、g4", "", "C4、C6、C8 不接")]
at.text(0.0, 1.0, "線號　顏色　從　　　　→ 到　　用途", fontsize=11, weight="bold", va="top")
for i, (c, l, a_, b_, u) in enumerate(ROWS_T):
    y = 0.9 - i * 0.082
    at.add_patch(Rectangle((0.045, y - 0.025), 0.03, 0.05, fc=c, ec="#555", transform=at.transAxes))
    at.text(0.0, y, l, fontsize=10.5, va="center")
    at.text(0.09, y, a_, fontsize=10.5, va="center")
    at.text(0.17, y, ("→ " + b_) if b_ else "", fontsize=10.5, va="center")
    at.text(0.25, y, u, fontsize=10.5, va="center")
NOTE = ["轉接板排針對應（同一欄的 a–e 或 f–j 是通的）：",
        "　d1 C1 VCC｜d2 C2 RST｜d3 C3 CLK｜d4 C4｜d5 SW1",
        "　g1 C5 GND｜g2 C6｜g3 C7 I/O｜g4 C8｜g5 SW2",
        "跳線插在 a／b 列和 i／j 列：c–h 列被轉接板的舌片蓋住。",
        "W1、W5、W6 要跨過麵包板中間的溝，用長一點的杜邦線。",
        "模組蓋住 d–h 列；它上下各還有 a–c、i–j 列可以插線。",
        "SW1／SW2 是常開開關，插卡才導通；P1.00 要開內部上拉。",
        "模組腳位照洞洞板 v9（老師照片），插之前對一下模組背面的印字。"]
for i, s in enumerate(NOTE):
    at.text(0.58, 1.0 - i * 0.1, s, fontsize=10, va="top")

out = os.path.join(HERE, "接線圖_含nRF.png")
fig.savefig(out, dpi=130)
print("saved", out)
