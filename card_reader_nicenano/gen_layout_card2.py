"""Card-reader demo layout (v2): socket long side (62 mm) horizontal, card slot on top.
Perfboard 61 x 25.4 mm (24 x 10 holes) under the lower part of the socket; nice!nano on the front,
USB-C to the left; all wires on the FRONT (OK wire). Battery taped elsewhere (only its leads shown)."""
import sys

OUT = sys.argv[1]
S = 34
SOCK_H = 40.0                                   # socket short side (ESTIMATED from photo)
RTOP = 0.5 + SOCK_H / 2.54                      # socket top edge (card slot) in hole rows
c_of = lambda X: 0.5 + (X - 0.5) / 2.54         # socket X (mm, from its left edge) -> column
LX = {"C1": c_of(39.2), "C2": c_of(36.3), "C3": c_of(33.8), "C4": c_of(31.2)}   # bottom-edge legs
TX = {"C5": c_of(39.2), "C6": c_of(36.3), "C7": c_of(33.8), "C8": c_of(31.2)}   # top-edge legs (slot side)
SWX = {"SW1": 10.0, "SW2": 11.0}                # detect switch legs, bottom edge (ASSUMED)
C0, C1_, R0, R1_ = -3.5, 27.5, -2.6, RTOP + 7.5
PW = int((C1_ - C0) * S)
PH = int((R1_ - R0) * S)
W, H = max(PW + 60, 1560), PH + 120 + 420
COL = {"red": "#d62828", "blk": "#1b1b1b", "yel": "#e3b505", "blu": "#1f6fd1", "grn": "#2a9d4b", "pur": "#8e44ad", "brn": "#8a5a2b"}
o = []; a = o.append
a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
a("""<style>text{font-family:'Microsoft JhengHei','Noto Sans TC',sans-serif;fill:#1f2328}
.h1{font-size:26px;font-weight:700}.h2{font-size:19px;font-weight:700}.sub{font-size:14px;fill:#57606a}
.ax{font-size:11px;fill:#6e7781}.pl{font-size:12px;font-weight:700}.pt{font-size:15px;font-weight:700}
.tb{font-size:14px}.th{font-size:14px;font-weight:700}.wn{font-size:12px;font-weight:700}</style>""")
a(f'<rect width="{W}" height="{H}" fill="#fff"/>')
a('<text x="30" y="42" class="h1">讀卡機 Layout Demo v2 — 卡座＋nice!nano＋洞洞板（正面俯視，插卡口在上）</text>')
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

# card (sticks out above the slot)
rect(c_of(4), c_of(58), RTOP - 3.0, RTOP + 7.3, fill="rgba(31,111,209,0.06)", stroke="#1f6fd1", stroke_width="2", stroke_dasharray="10 6", rx="12")
label((c_of(4) + c_of(58)) / 2, RTOP + 5.0, "健保卡 85.6 × 54（從上往下插，約一半露在外面）", color="#1f6fd1", halo=False, cls="pt")
label((c_of(4) + c_of(58)) / 2, RTOP + 3.8, "▼ 插卡方向", color="#1f6fd1", halo=False, cls="pt")
# socket body (behind the board)
rect(c_of(0), c_of(62), 0.5, RTOP, fill="#2b2f36", stroke="#000", stroke_width="1.5", rx="5")
label(c_of(14), RTOP - 1.0, "J1 卡座（貼在板子背面）62 × 40（寬為照片估計）", color="#cfd6de", halo=False, cls="pt"); label(c_of(14), RTOP - 2.0, "上緣＝插卡口", color="#cfd6de", halo=False)
# perfboard
rect(0.5, 24.5, 0.5, 10.5, fill="#1f5a3a", stroke="#0f3b25", rx="5")
for c in range(1, 25):
    for r in range(1, 11):
        a(f'<circle cx="{X(c)}" cy="{Y(r)}" r="7" fill="#d9dde3"/><circle cx="{X(c)}" cy="{Y(r)}" r="3" fill="#1f5a3a"/>')
    a(f'<text x="{X(c)}" y="{Y(0.5)+18}" class="ax" text-anchor="middle">{c}</text>')
for r in range(1, 11):
    a(f'<text x="{X(24.5)+14}" y="{Y(r)+4}" class="ax" text-anchor="middle">{r}</text>')
label(12.5, 0.5 - 1.9, "洞洞板 61 × 25.4 mm（24 × 10 孔），貼在卡座下半部；卡座在背面", color="#1f2328", halo=False)

# legs
for name, c in TX.items():
    a(f'<rect x="{X(c)-3:.1f}" y="{Y(RTOP)-12:.1f}" width="6" height="16" fill="#c0c4c9" stroke="#555"/>')
    label(c, RTOP + 0.75, name, color="#1f2328", halo=False)
for name, c in LX.items():
    a(f'<rect x="{X(c)-3:.1f}" y="{Y(0.5)-4:.1f}" width="6" height="16" fill="#c0c4c9" stroke="#555"/>')
    label(c, -0.15, name, color="#1f2328", halo=False, dy=10)
for name, c in SWX.items():
    a(f'<rect x="{X(c)-3:.1f}" y="{Y(0.5)-4:.1f}" width="6" height="16" fill="#9fb3c8" stroke="#555"/>')
    label(c, -0.15, name, color="#1f2328", halo=False, dy=10)

# nice!nano: USB-C to the left; bottom row r3 = pins 1..12, top row r9 = pins 24..13
NB = ["P0.06", "P0.08", "GND", "GND", "P0.17", "P0.20", "P0.22", "P0.24", "P1.00", "P0.11", "P1.04", "P1.06"]
NT = ["RAW", "GND", "RST", "VCC", "P0.31", "P0.29", "P0.02", "P1.15", "P1.13", "P1.11", "P0.10", "P0.09"]
rect(-0.05, 13.05, 2.45, 9.55, fill="rgba(20,20,20,0.66)", stroke="#000", stroke_width="1.5", rx="3")
rect(-0.75, 1.3, 4.3, 7.7, fill="#e9ecef", stroke="#555"); label(0.3, 6.0, "USB-C", color="#333", halo=False)
rect(11.0, 13.05, 2.45, 9.55, fill="rgba(220,40,40,0.22)", stroke="#d62828", stroke_dasharray="4 3")
label(12.0, 6.0, "天線", color="#ffd0d0")
label(6.5, 6.5, "U1 nice!nano v2", cls="pt"); label(6.5, 5.5, "（朝上，USB-C 朝左凸出）", color="#ddd")
for c in range(1, 13):
    for r in (3, 9):
        a(f'<rect x="{X(c)-5}" y="{Y(r)-5}" width="10" height="10" fill="#e8b84a" stroke="#7a5a10"/>')
    label(c, 3, NB[c - 1], color="#ffe9a8", dy=-11, cls="ax")
    label(c, 9, NT[c - 1], color="#ffe9a8", dy=20, cls="ax")
# C10 0.1uF across top-row GND (c2) and VCC (c4), leads in holes (2,10) & (4,10)
rect(1.7, 4.3, 9.75, 10.25, fill="#d9b34a", stroke="#6b4d1e", rx="5"); label(3.0, 10.0, "C10 0.1µF", color="#3d2a00", halo=False, cls="ax")

WIRES = [  # no, colour, path, from, to, use, dashed
    ("K1", "red", [(4, 9), (4.4, 9.75), (17.0, 9.75), (17.0, 1.2), (LX["C1"], 0.5)], "VCC 腳21 (c4,r9)", "J1 C1 VCC（下排）", "+3V3_CARD（P0.13 控制）", False),
    ("K2", "blk", [(2, 9), (2.3, 10.2), (TX["C5"], 10.2), (TX["C5"], RTOP)], "GND 腳23 (c2,r9)", "J1 C5 GND（上排）", "卡片 GND", False),
    ("K3", "blu", [(8, 3), (8.5, 2.15), (LX["C2"], 2.15), (LX["C2"], 0.5)], "P0.24 腳8 (c8,r3)", "J1 C2 RST（下排）", "RST", False),
    ("K4", "grn", [(5, 3), (5.5, 1.55), (LX["C3"], 1.55), (LX["C3"], 0.5)], "P0.17 腳5 (c5,r3)", "J1 C3 CLK（下排）", "CLK", False),
    ("K5", "yel", [(6, 3), (6.4, 2.75), (13.6, 2.75), (13.6, 9.0), (TX["C7"] + 0.0, 9.0), (TX["C7"], RTOP)], "P0.20 腳6 (c6,r3)", "J1 C7 I/O（上排）", "I/O", False),
    ("K6", "yel", [(6, 3), (6.5, 3.6), (7, 3)], "P0.20 腳6 (c6,r3)", "P0.22 腳7 (c7,r3)", "I/O 兩腳併接", False),
    ("K7", "blk", [(3, 3), (3.5, 3.6), (4, 3)], "GND 腳3 (c3,r3)", "GND 腳4 (c4,r3)", "GND 兩腳併接", False),
    ("K8", "pur", [(9, 3), (9.4, 2.45), (9.6, 1.0), (SWX["SW1"], 0.5)], "P1.00 腳9 (c9,r3)", "J1 SW1 DET", "插卡偵測（選配）", True),
    ("K9", "blk", [(4, 3), (4.4, 0.95), (SWX["SW2"], 0.95), (SWX["SW2"], 0.5)], "GND 腳4 (c4,r3)", "J1 SW2 DET_G", "偵測開關接地（選配）", True),
    ("K10", "brn", [(2, 9), (2, 10)], "GND 腳23 (c2,r9)", "C10 左腳 (c2,r10)", "C10 接地", False),
    ("K11", "red", [(4, 9), (4, 10)], "VCC 腳21 (c4,r9)", "C10 右腳 (c4,r10)", "C10 接 VCC", False),
    ("K12", "red", [(-2.6, 9.9), (0.2, 9.9), (1, 9)], "電池 ＋（另外黏）", "RAW 腳24 (c1,r9)", "VBAT", False),
    ("K13", "blk", [(-2.6, 10.5), (1.4, 10.5), (2, 9)], "電池 －", "GND 腳23 (c2,r9)", "電池負極", False),
]
for no, cl, path, s0, s1, use, dash in WIRES:
    wire(path, COL[cl], dash)
for c, r, t in ((10.5, 9.45, "K1"), (9.0, 10.55, "K2"), (11.0, 2.45, "K3"), (11.0, 1.25, "K4"), (13.95, 6.0, "K5"),
                (6.5, 3.9, "K6"), (3.5, 3.9, "K7"), (9.9, 1.6, "K8"), (7.0, 0.68, "K9"), (17.4, 5.0, "K1"),
                (TX["C5"] + 0.45, 13.0, "K2"), (TX["C7"] - 0.45, 13.0, "K5")):
    label(c, r, t, cls="wn")
label(-1.9, 11.25, "電池線 K12/K13", color="#1f2328", halo=False)

# ---------- table ----------
ty = PH + 130
a(f'<text x="30" y="{ty}" class="h2">接線表（全部在正面，OK 線）</text>')
cols = [30, 82, 130, 380, 640]
for x, h in zip(cols, ["線", "色", "從", "到", "用途"]):
    a(f'<text x="{x}" y="{ty+28}" class="th">{h}</text>')
a(f'<line x1="30" y1="{ty+36}" x2="{W-30}" y2="{ty+36}" stroke="#d0d7de"/>')
for i, (no, cl, path, s0, s1, use, dash) in enumerate(WIRES):
    yy = ty + 58 + i * 26
    a(f'<text x="{cols[0]}" y="{yy}" class="tb">{no}</text>')
    da = ' stroke-dasharray="6 4"' if dash else ""
    a(f'<line x1="{cols[1]}" y1="{yy-5}" x2="{cols[1]+34}" y2="{yy-5}" stroke="{COL[cl]}" stroke-width="5"{da}/>')
    for x, v in zip(cols[2:], (s0, s1, use)):
        a(f'<text x="{x}" y="{yy}" class="tb">{v}</text>')
nx = 900
a(f'<text x="{nx}" y="{ty}" class="h2" style="fill:#b42318">這是 Demo：下面幾項是估的，量完再修</text>')
for i, t in enumerate(["卡座寬 40 mm：用照片比例從 62 mm 推算",
                       "卡座腳位置：照片估在離左緣 31–39 mm，間距 2.54",
                       "上排（插卡口那側）C5–C8、下排 C1–C4：照老師紅字",
                       "偵測開關 SW1/SW2：估在下緣第 10、11 欄",
                       "nice!nano 腳先焊、背面剪平，再接 OK 線",
                       "K2、K5 會跨過卡座上方到插卡口那一排腳",
                       "OK 線有絕緣，K5 跨過 K1、K2 沒關係",
                       "P0.08（UART_TX）、P1.06 老師圖沒接到東西，不焊"]):
    a(f'<text x="{nx}" y="{ty+30+i*26}" class="tb">● {t}</text>')
a("</svg>")
open(OUT, "w", encoding="utf-8").write("\n".join(o))
print(W, H)
