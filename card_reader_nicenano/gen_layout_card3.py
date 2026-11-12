"""Card-reader demo layout (v3): socket long side (62 mm) horizontal, card slot on top.
Perfboard 25.4 x 61 mm (10 x 24 holes) STANDING (rotated 90 deg), on the left part of the socket and
reaching below it; nice!nano at the bottom with USB-C pointing down (opposite the card slot).
All wires on the FRONT (OK wire). Battery taped elsewhere (only its two leads shown)."""
import sys

OUT = sys.argv[1]
S = 30
SOCK_H = 40.0                                   # socket short side (ESTIMATED from photo)
RTOP = 24.5                                     # socket top edge (card slot) = board top edge
RBOT = RTOP - SOCK_H / 2.54                     # socket bottom edge
BX = 62.0 - 25.4                               # board flush with the socket RIGHT edge
c_of = lambda X: 0.5 + (X - BX) / 2.54          # socket X (mm from its left edge) -> column
LEG = {"C4": c_of(31.2), "C3": c_of(33.8), "C2": c_of(36.3), "C1": c_of(39.2)}   # bottom-edge legs
TOPL = {"C8": c_of(31.2), "C7": c_of(33.8), "C6": c_of(36.3), "C5": c_of(39.2)}  # top-edge legs (slot side)
SWL = {"SW1": c_of(26.0), "SW2": c_of(28.4)}    # detect switch legs, bottom edge (ASSUMED)
C0, C1_, R0, R1_ = -16.0, 12.5, -2.2, RTOP + 8.0
PW = int((C1_ - C0) * S)
PH = int((R1_ - R0) * S)
W, H = PW + 700, max(PH + 150, 1100)
COL = {"red": "#d62828", "blk": "#1b1b1b", "yel": "#e3b505", "blu": "#1f6fd1", "grn": "#2a9d4b", "pur": "#8e44ad", "brn": "#8a5a2b"}
o = []; a = o.append
a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
a("""<style>text{font-family:'Microsoft JhengHei','Noto Sans TC',sans-serif;fill:#1f2328}
.h1{font-size:26px;font-weight:700}.h2{font-size:19px;font-weight:700}.sub{font-size:14px;fill:#57606a}
.ax{font-size:11px;fill:#6e7781}.pl{font-size:12px;font-weight:700}.pt{font-size:15px;font-weight:700}
.tb{font-size:13px}.th{font-size:13px;font-weight:700}.wn{font-size:12px;font-weight:700}</style>""")
a(f'<rect width="{W}" height="{H}" fill="#fff"/>')
a('<text x="30" y="42" class="h1">讀卡機 Layout Demo v3 — 洞洞板直放靠右，USB-C 在插卡口對面（正面俯視）</text>')
a('<text x="30" y="66" class="sub">依老師 261103_nrf_card 線路圖＋紅字腳位（上排 C5–C8、下排 C1–C4）。線全部在正面，OK 線手焊；電池另外用雙面膠黏，只畫出它的兩條線。</text>')
X = lambda c: 30 + (c - C0) * S
Y = lambda r: 90 + (R1_ - r) * S
def rect(c0, c1, r0, r1, **kw):
    at = " ".join(f'{k.replace("_", "-")}="{v}"' for k, v in kw.items())
    a(f'<rect x="{X(min(c0,c1)):.1f}" y="{Y(max(r0,r1)):.1f}" width="{abs(c1-c0)*S:.1f}" height="{abs(r1-r0)*S:.1f}" {at}/>')
def label(c, r, t, cls="pl", color="#fff", dy=4, anchor="middle", halo=True):
    st = ";paint-order:stroke;stroke:rgba(0,0,0,0.45);stroke-width:2.5px" if halo else ""
    a(f'<text x="{X(c):.1f}" y="{Y(r)+dy:.1f}" class="{cls}" text-anchor="{anchor}" style="fill:{color}{st}">{t}</text>')
def wire(pts, color, dash=False):
    d = "M" + " L".join(f"{X(c):.1f},{Y(r):.1f}" for c, r in pts)
    da = ' stroke-dasharray="8 5"' if dash else ""
    a(f'<path d="{d}" stroke="#fff" stroke-width="7" fill="none" stroke-linecap="round" stroke-linejoin="round"/>')
    a(f'<path d="{d}" stroke="{color}" stroke-width="4" fill="none" stroke-linecap="round" stroke-linejoin="round"{da}/>')
    for c, r in (pts[0], pts[-1]):
        a(f'<circle cx="{X(c):.1f}" cy="{Y(r):.1f}" r="5" fill="{color}" stroke="#fff" stroke-width="1.5"/>')

# card above the slot
rect(c_of(4), c_of(58), RTOP - 2.0, RTOP + 7.6, fill="rgba(31,111,209,0.06)", stroke="#1f6fd1", stroke_width="2", stroke_dasharray="10 6", rx="12")
label((c_of(4) + c_of(58)) / 2, RTOP + 5.2, "健保卡 85.6 × 54（從上往下插，約一半露在外面）", color="#1f6fd1", halo=False, cls="pt")
label((c_of(4) + c_of(58)) / 2, RTOP + 4.0, "▼ 插卡方向", color="#1f6fd1", halo=False, cls="pt")
# socket (behind the board)
rect(c_of(0), c_of(62), RBOT, RTOP, fill="#2b2f36", stroke="#000", stroke_width="1.5", rx="5")
label(c_of(14), RTOP - 2.0, "J1 卡座（在板子背面）", color="#cfd6de", halo=False, cls="pt")
label(c_of(14), RTOP - 3.0, "62 × 40（寬為照片估計）", color="#cfd6de", halo=False)
label(c_of(14), RTOP - 4.0, "上緣＝插卡口", color="#cfd6de", halo=False)
# perfboard (standing)
rect(0.5, 10.5, 0.5, 24.5, fill="#1f5a3a", stroke="#0f3b25", rx="5")
for c in range(1, 11):
    for r in range(1, 25):
        a(f'<circle cx="{X(c)}" cy="{Y(r)}" r="6.5" fill="#d9dde3"/><circle cx="{X(c)}" cy="{Y(r)}" r="2.8" fill="#1f5a3a"/>')
for c in range(1, 11):
    a(f'<text x="{X(c)}" y="{Y(24.5)-6}" class="ax" text-anchor="middle" style="fill:#cfd6de">{c}</text>')
for r in range(1, 25):
    a(f'<text x="{X(0.5)-14}" y="{Y(r)+4}" class="ax" text-anchor="middle">{r}</text>')
label(5.5, -1.6, "洞洞板 25.4 × 61（10 × 24 孔）直放", color="#1f2328", halo=False)

# legs
for name, c in TOPL.items():
    a(f'<rect x="{X(c)-3:.1f}" y="{Y(RTOP)-12:.1f}" width="6" height="16" fill="#c0c4c9" stroke="#555"/>')
    label(c, RTOP + 0.75, name, color="#1f2328", halo=False)
for name, c in LEG.items():
    a(f'<rect x="{X(c)-3:.1f}" y="{Y(RBOT)-4:.1f}" width="6" height="16" fill="#c0c4c9" stroke="#555"/>')
    label(c, RBOT + 0.75, name, color="#e6edf3", halo=False)
for name, c in SWL.items():
    a(f'<rect x="{X(c)-3:.1f}" y="{Y(RBOT)-4:.1f}" width="6" height="16" fill="#9fb3c8" stroke="#555"/>')
    label(c, RBOT + 0.75, name, color="#e6edf3", halo=False)

# nice!nano rotated 180 deg (USB-C down): right column c9 = pins 1..12 (bottom->top), left column c3 = pins 24..13
NR_ = ["P0.06", "P0.08", "GND", "GND", "P0.17", "P0.20", "P0.22", "P0.24", "P1.00", "P0.11", "P1.04", "P1.06"]
NL_ = ["RAW", "GND", "RST", "VCC", "P0.31", "P0.29", "P0.02", "P1.15", "P1.13", "P1.11", "P0.10", "P0.09"]
rect(2.45, 9.55, -0.05, 12.95, fill="rgba(20,20,20,0.66)", stroke="#000", stroke_width="1.5", rx="3")
rect(4.4, 7.6, -0.8, 1.25, fill="#e9ecef", stroke="#555"); label(6.0, -0.1, "USB-C ↓", color="#333", halo=False)
rect(4.3, 7.7, 11.0, 12.95, fill="rgba(220,40,40,0.22)", stroke="#d62828", stroke_dasharray="4 3"); label(6.0, 12.0, "天線", color="#ffd0d0")
label(6.0, 3.6, "U1 nice!nano", cls="pt"); label(6.0, 2.7, "轉 180°", color="#ddd")
for i in range(12):
    for c in (3, 9):
        a(f'<rect x="{X(c)-5}" y="{Y(i+1)-5}" width="10" height="10" fill="#e8b84a" stroke="#7a5a10"/>')
    label(8.55, i + 1, NR_[i], color="#ffe9a8", anchor="end", cls="ax")
    label(3.45, i + 1, NL_[i], color="#ffe9a8", anchor="start", cls="ax")
# C10 0.1uF between (1,2) GND and (1,4) VCC
rect(0.72, 1.28, 2.2, 3.8, fill="#d9b34a", stroke="#6b4d1e", rx="3"); label(1.0, 3.0, "C10", color="#3d2a00", halo=False, cls="ax")

WIRES = [  # no, colour, path, from, to, use, dashed
    ("K1", "red", [(3, 4), (1, 4), (1, RBOT - 0.55), (LEG["C1"], RBOT)], "VCC 腳21 (c3,r4)", "J1 C1 VCC（下排）", "+3V3_CARD（經 C10 腳）", False),
    ("K2", "blk", [(9, 4), (10.0, 4.5), (10.0, RTOP - 1.2), (TOPL["C5"], RTOP - 1.2), (TOPL["C5"], RTOP)], "GND 腳4 (c9,r4)", "J1 C5 GND（上排）", "卡片 GND", False),
    ("K3", "blu", [(9, 8), (8.5, 8.4), (LEG["C2"], 8.4), (LEG["C2"], RBOT)], "P0.24 腳8 (c9,r8)", "J1 C2 RST（下排）", "RST（跨過 nice!nano 上方）", False),
    ("K4", "grn", [(9, 5), (8.5, 5.4), (LEG["C3"], 5.4), (LEG["C3"], RBOT)], "P0.17 腳5 (c9,r5)", "J1 C3 CLK（下排）", "CLK（跨過 nice!nano 上方）", False),
    ("K5", "yel", [(9, 6), (10.3, 6.6), (10.3, RTOP - 0.6), (TOPL["C7"], RTOP - 0.6), (TOPL["C7"], RTOP)], "P0.20 腳6 (c9,r6)", "J1 C7 I/O（上排）", "I/O", False),
    ("K6", "yel", [(9, 6), (9.7, 6.5), (9, 7)], "P0.20 腳6 (c9,r6)", "P0.22 腳7 (c9,r7)", "I/O 兩腳併接", False),
    ("K7", "blk", [(9, 3), (9.7, 3.5), (9, 4)], "GND 腳3 (c9,r3)", "GND 腳4 (c9,r4)", "GND 兩腳併接", False),
    ("K8", "pur", [(9, 9), (8.6, 10.35), (SWL["SW1"], 10.35), (SWL["SW1"], RBOT)], "P1.00 腳9 (c9,r9)", "J1 SW1 DET", "插卡偵測（選配，跨過 nice!nano）", True),
    ("K9", "blk", [(1, 2), (SWL["SW2"], 2), (SWL["SW2"], RBOT)], "C10 接地腳 (c1,r2)", "J1 SW2 DET_G", "偵測開關接地（選配）", True),
    ("K10", "brn", [(3, 2), (1, 2)], "GND 腳23 (c3,r2)", "C10 另一腳 (c1,r2)", "C10 接地", False),
    ("K11", "red", [(-5.0, 0.9), (2.2, 0.9), (3, 1)], "電池 ＋（另外黏）", "RAW 腳24 (c3,r1)", "VBAT", False),
    ("K12", "blk", [(-5.0, 1.45), (1.8, 1.45), (3, 2)], "電池 －", "GND 腳23 (c3,r2)", "電池負極", False),
]
for no, cl, path, s0, s1, use, dash in WIRES:
    wire(path, COL[cl], dash)
for c, r, t in ((1.0, 6.5, "K1"), (10.0, 15.0, "K2"), (5.6, 8.7, "K3"), (5.6, 5.7, "K4"), (10.3, 19.0, "K5"),
                (10.3, 7.1, "K6"), (10.3, 3.0, "K7"), (5.6, 10.65, "K8"), (-2.2, 4.0, "K9"), (2.0, 2.4, "K10")):
    label(c, r, t, cls="wn")
label(-4.0, 0.3, "電池線 K11/K12", color="#1f2328", halo=False)

# ---------- table (right) ----------
tx = PW + 40
ty = 120
a(f'<text x="{tx}" y="{ty}" class="h2">接線表（全部在正面，OK 線）</text>')
cols = [tx, tx + 40, tx + 84, tx + 250, tx + 430]
for x, h in zip(cols, ["線", "色", "從", "到", "用途"]):
    a(f'<text x="{x}" y="{ty+28}" class="th">{h}</text>')
a(f'<line x1="{tx}" y1="{ty+36}" x2="{W-20}" y2="{ty+36}" stroke="#d0d7de"/>')
for i, (no, cl, path, s0, s1, use, dash) in enumerate(WIRES):
    yy = ty + 58 + i * 25
    a(f'<text x="{cols[0]}" y="{yy}" class="tb">{no}</text>')
    da = ' stroke-dasharray="6 4"' if dash else ""
    a(f'<line x1="{cols[1]}" y1="{yy-5}" x2="{cols[1]+30}" y2="{yy-5}" stroke="{COL[cl]}" stroke-width="5"{da}/>')
    for x, v in zip(cols[2:], (s0, s1, use)):
        a(f'<text x="{x}" y="{yy}" class="tb">{v}</text>')
ny = ty + 58 + len(WIRES) * 25 + 30
a(f'<text x="{tx}" y="{ny}" class="h2" style="fill:#b42318">Demo：下面幾項是估的，量完再修</text>')
for i, t in enumerate(["卡座寬 40 mm：照片比例從 62 mm 推算",
                       "卡座腳：估在離卡座左緣 31–39 mm，間距 2.54",
                       "上排（插卡口側）C5–C8、下排 C1–C4：照老師紅字",
                       "偵測開關 SW1/SW2：估在下緣、離左緣約 26–28 mm",
                       "板子靠卡座右緣、上緣對齊插卡口，下方超出卡座約 21 mm",
                       "C1、C5 的腳估在板子左緣第 1–2 欄下面，可能要把腳彎進孔裡焊",
                       "nice!nano 腳先焊、背面剪平，再接 OK 線",
                       "K1、K2、K5 會跨過卡座正面；OK 線有絕緣，交叉沒關係",
                       "P0.08（UART_TX）、P1.06 老師圖沒接到東西，不焊"]):
    a(f'<text x="{tx}" y="{ny+28+i*25}" class="tb">● {t}</text>')
a("</svg>")
open(OUT, "w", encoding="utf-8").write("\n".join(o))
print(W, H)
