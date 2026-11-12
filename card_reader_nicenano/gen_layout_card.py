"""Card-reader perfboard layout: 10 x 24 holes (25.4 x 61 mm), nice!nano at the bottom (USB down),
card socket J1 behind the board, all wires on the FRONT (hand-soldered OK wire)."""
import sys

OUT = sys.argv[1]
S = 30
NC, NR = 10, 24
HW = 40.0 / 2.54                     # socket width (ASSUMED 40 mm -> holes)
XMAX = 0.5 + HW + 1.5
PW = int((XMAX + 1.5) * S) + 60
PH = NR * S + 200
W, H = 2 * PW + 40 + 640, PH + 140
COL = {"red": "#d62828", "blk": "#1b1b1b", "yel": "#e3b505", "org": "#f07d14", "blu": "#1f6fd1", "grn": "#2a9d4b", "pur": "#8e44ad"}
o = []; a = o.append
a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
a("""<style>text{font-family:'Microsoft JhengHei','Noto Sans TC',sans-serif;fill:#1f2328}
.h1{font-size:26px;font-weight:700}.h2{font-size:19px;font-weight:700}.sub{font-size:14px;fill:#57606a}
.ax{font-size:11px;fill:#6e7781}.pl{font-size:11px;font-weight:700}.pt{font-size:14px;font-weight:700}
.tb{font-size:13px}.th{font-size:13px;font-weight:700}.wn{font-size:12px;font-weight:700}</style>""")
a(f'<rect width="{W}" height="{H}" fill="#fff"/>')
a('<text x="30" y="42" class="h1">讀卡機洞洞板 Layout — nice!nano＋ISO 7816 卡座（板子 25.4 × 61 mm，10 × 24 孔）</text>')
a('<text x="30" y="66" class="sub">依老師 261103_nrf_card 線路圖。零件與線全部在正面（OK 線手焊），卡座貼在背面。孔位 (c, r)：c＝欄 1–10（左→右）、r＝列 1–24（下→上），正面俯視。</text>')


class Panel:
    def __init__(s, ox, oy, mirror): s.ox, s.oy, s.m = ox, oy, mirror
    def x(s, c): return s.ox + 50 + ((XMAX - c) if s.m else (c + 1.0)) * S
    def y(s, r): return s.oy + 100 + (NR + 1 - r) * S
    def rect(s, c0, c1, r0, r1, **kw):
        xa, xb = sorted((s.x(c0), s.x(c1))); ya, yb = sorted((s.y(r0), s.y(r1)))
        at = " ".join(f'{k.replace("_", "-")}="{v}"' for k, v in kw.items())
        a(f'<rect x="{xa:.1f}" y="{ya:.1f}" width="{xb-xa:.1f}" height="{yb-ya:.1f}" {at}/>')
    def label(s, c, r, t, cls="pl", color="#fff", dy=4, anchor="middle"):
        a(f'<text x="{s.x(c):.1f}" y="{s.y(r)+dy:.1f}" class="{cls}" text-anchor="{anchor}" style="fill:{color};paint-order:stroke;stroke:rgba(0,0,0,0.35);stroke-width:2px">{t}</text>')
    def wire(s, pts, color, dash=False, w=4):
        d = "M" + " L".join(f"{s.x(c):.1f},{s.y(r):.1f}" for c, r in pts)
        da = ' stroke-dasharray="8 5"' if dash else ""
        a(f'<path d="{d}" stroke="#fff" stroke-width="{w+3}" fill="none" stroke-linecap="round" stroke-linejoin="round"/>')
        a(f'<path d="{d}" stroke="{color}" stroke-width="{w}" fill="none" stroke-linecap="round" stroke-linejoin="round"{da}/>')
        for c, r in (pts[0], pts[-1]):
            a(f'<circle cx="{s.x(c):.1f}" cy="{s.y(r):.1f}" r="5" fill="{color}" stroke="#fff" stroke-width="1.5"/>')
    def grid(s, title, sub):
        a(f'<text x="{s.ox}" y="{s.oy+18}" class="h2">{title}</text><text x="{s.ox}" y="{s.oy+40}" class="sub">{sub}</text>')
        # card socket (behind the board) - assumed 40 mm wide, 62 mm long
        s.rect(0.5, 0.5 + HW, 0.3, 24.7, fill="#2b2f36", stroke="#000", stroke_width="1.5", rx="4")
        s.label(0.5 + HW - 0.3, 23.0, "J1 卡座", color="#cfd6de", anchor="end" if not s.m else "start", cls="pt"); s.label(0.5 + HW - 0.3, 22.2, "（背面，寬先估 40）", color="#cfd6de", anchor="end" if not s.m else "start")
        s.rect(0.5, NC + 0.5, 0.5, NR + 0.5, fill="#1f5a3a", stroke="#0f3b25", rx="5")
        for c in range(1, NC + 1):
            for r in range(1, NR + 1):
                a(f'<circle cx="{s.x(c)}" cy="{s.y(r)}" r="6.5" fill="#d9dde3"/><circle cx="{s.x(c)}" cy="{s.y(r)}" r="2.8" fill="#1f5a3a"/>')
            a(f'<text x="{s.x(c)}" y="{s.y(NR + 0.5) - 8}" class="ax" text-anchor="middle">{c}</text>')
        for r in range(1, NR + 1):
            side = s.x(NC + 0.5) + 14 if s.m else s.x(0.5) - 14
            a(f'<text x="{side}" y="{s.y(r)+4}" class="ax" text-anchor="middle">{r}</text>')
        # socket contact legs (left & right edge of the socket), C-numbers ASSUMED until measured
        for side, cx in (("L", 0.1), ("R", 0.5 + HW + 0.4)):
            for i, r in enumerate((16, 15, 14, 13)):
                a(f'<rect x="{s.x(cx)-9:.1f}" y="{s.y(r)-3:.1f}" width="18" height="6" fill="#c0c4c9" stroke="#555"/>')
    def pins(s, cells, color="#e8b84a"):
        for c, r in cells:
            a(f'<rect x="{s.x(c)-5}" y="{s.y(r)-5}" width="10" height="10" fill="{color}" stroke="#7a5a10"/>')

# nice!nano rotated 180 deg: USB at the bottom edge; right column = pins 1..12 (bottom->top), left column = pins 24..13
NR_ = ["P0.06", "P0.08", "GND", "GND", "P0.17", "P0.20", "P0.22", "P0.24", "P1.00", "P0.11", "P1.04", "P1.06"]
NL_ = ["RAW", "GND", "RST", "VCC", "P0.31", "P0.29", "P0.02", "P1.15", "P1.13", "P1.11", "P0.10", "P0.09"]
nano = [(3, r) for r in range(1, 13)] + [(9, r) for r in range(1, 13)]
LEGL = {16: "C1", 15: "C2", 14: "C3", 13: "C4"}
LEGR = {16: "C5", 15: "C6", 14: "C7", 13: "C8"}
RX = 0.5 + HW + 0.4                  # right-leg x

F = Panel(30, 90, False)
F.grid("① 正面（俯視）— 線全部在這面", "插卡口在上方；nice!nano 在最下面、USB-C 朝下凸出")
a(f'<text x="{F.x(5.5)}" y="{F.y(25.6)}" class="pt" text-anchor="middle" style="fill:#b45309">▼ 插卡口（卡片從上方插入）</text>')
F.rect(2.45, 9.55, 0.0, 12.95, fill="rgba(20,20,20,0.62)", stroke="#000", stroke_width="1.5", rx="3")
F.rect(4.6, 7.4, -0.55, 1.4, fill="#e9ecef", stroke="#555"); F.label(6.0, 0.2, "USB-C", color="#333")
F.label(6.0, 9.2, "nice!nano", cls="pt"); F.label(6.0, 8.4, "（朝上，轉 180°）", color="#ddd")
F.rect(4.6, 7.4, 10.6, 12.8, fill="rgba(220,40,40,0.22)", stroke="#d62828", stroke_dasharray="4 3"); F.label(6.0, 11.0, "天線端", color="#ffd0d0")
# battery on top half
F.rect(0.6, 10.4, 13.2, 24.4, fill="rgba(240,170,60,0.20)", stroke="#f0a030", stroke_width="2.5", stroke_dasharray="9 5")
F.label(5.5, 21.5, "BT1 電池 30×25×5（估）", color="#ffc56b"); F.label(5.5, 20.7, "最後才貼，蓋在線上面", color="#ffc56b")
# C10 0.1uF between (1,2) GND and (1,4) VCC
F.rect(0.7, 1.3, 2.2, 3.8, fill="#c9a26b", stroke="#6b4d1e", rx="3"); F.label(1.0, 3.0, "C10", color="#fff", cls="pl")
F.pins(nano); F.pins([(1, 2), (1, 4)], "#f2d16b")
for i, n in enumerate(NR_):
    F.label(8.6, i + 1, n, color="#ffe9a8", anchor="end", dy=4)
for i, n in enumerate(NL_):
    F.label(3.4, i + 1, n, color="#ffe9a8", anchor="start", dy=4)
for r, t in LEGL.items():
    F.label(-0.35, r, t, color="#1f2328", anchor="end")
for r, t in LEGR.items():
    F.label(RX + 0.55, r, t, color="#1f2328", anchor="start")
# detect switch (right side, ASSUMED position)
SW = [(RX, 18), (RX, 19)]
for c, r in SW:
    a(f'<rect x="{F.x(c)-9:.1f}" y="{F.y(r)-3:.1f}" width="18" height="6" fill="#9fb3c8" stroke="#555"/>')
F.label(RX + 0.5, 18, "SW1", color="#1f2328", anchor="start", dy=-6); F.label(RX + 0.5, 19, "SW2", color="#1f2328", anchor="start", dy=-6)

WIRES = [  # no, colour, path, from, to, use
    ("K1", "red", [(3, 4), (1, 4), (1, 16), (0.1, 16)], "nice!nano VCC 腳21 (c3,r4)", "J1 C1 VCC（經 C10 腳）", "+3V3_CARD（P0.13 可開關）"),
    ("K2", "blk", [(3, 2), (1, 2)], "nice!nano GND 腳23 (c3,r2)", "C10 另一腳 (c1,r2)", "C10 接地"),
    ("K3", "blu", [(9, 8), (9.9, 8.6), (9.9, 15), (0.1, 15)], "nice!nano P0.24 腳8 (c9,r8)", "J1 C2 RST", "RST"),
    ("K4", "grn", [(9, 5), (10.3, 5.6), (10.3, 14), (0.1, 14)], "nice!nano P0.17 腳5 (c9,r5)", "J1 C3 CLK", "CLK"),
    ("K5", "blk", [(9, 4), (12.9, 4), (12.9, 16), (RX, 16)], "nice!nano GND 腳4 (c9,r4)", "J1 C5 GND", "卡片 GND"),
    ("K6", "blk", [(9, 3), (9.75, 3.5), (9, 4)], "nice!nano GND 腳3 (c9,r3)", "nice!nano GND 腳4 (c9,r4)", "腳3、4 併接（老師圖）"),
    ("K7", "yel", [(9, 6), (12.1, 6), (12.1, 14), (RX, 14)], "nice!nano P0.20 腳6 (c9,r6)", "J1 C7 I/O", "I/O"),
    ("K8", "yel", [(9, 6), (9.75, 6.5), (9, 7)], "nice!nano P0.20 腳6 (c9,r6)", "nice!nano P0.22 腳7 (c9,r7)", "I/O 兩腳併接（老師圖）"),
    ("K9", "pur", [(9, 9), (11.3, 9), (11.3, 18), (RX, 18)], "nice!nano P1.00 腳9 (c9,r9)", "J1 SW1 DET", "插卡偵測（選配）"),
    ("K10", "blk", [(RX, 19), (RX + 1.4, 19), (RX + 1.4, 16), (RX, 16)], "J1 SW2 DET_G", "J1 C5 GND 腳", "偵測開關接地（選配）"),
    ("K11", "red", [(0.9, 13.2), (2.05, 12.6), (2.05, 1.6), (3, 1)], "電池 ＋", "nice!nano RAW 腳24 (c3,r1)", "VBAT"),
    ("K12", "blk", [(1.5, 13.2), (1.6, 12.4), (1.6, 2.6), (3, 2)], "電池 －", "nice!nano GND 腳23 (c3,r2)", "電池負極"),
]
for no, cl, path, *_ in WIRES:
    F.wire(path, COL[cl], dash=no in ("K9", "K10"))
for c, r, t in ((0.55, 10.0, "K1"), (2.0, 1.75, "K2"), (8.2, 15.35, "K3"), (8.2, 14.35, "K4"), (13.4, 11.0, "K5"),
                (10.25, 3.0, "K6"), (12.6, 8.0, "K7"), (10.25, 7.1, "K8"), (11.8, 12.5, "K9"), (RX + 2.1, 17.5, "K10 "),
                (2.55, 9.0, "K11"), (1.05, 7.0, "K12")):
    F.label(c, r, t.strip(), color="#fff" if t == t.strip() else "#1f2328", cls="wn")

# ---------- back ----------
B = Panel(30 + PW + 20, 90, True)
B.grid("② 背面（翻過來看，左右相反）", "背面不走線；卡座 J1 貼在這面，接點朝外對著卡片")
B.pins(nano, "#c9a24a"); B.pins([(1, 2), (1, 4)], "#c9a24a")
B.label(5.5, 20.5, "卡座貼在板子背面（左半邊）", color="#e6edf3")
B.label(5.5, 19.6, "nice!nano 腳焊好後剪平", color="#e6edf3")

# ---------- table ----------
tx = 2 * PW + 70
ty = 120
a(f'<text x="{tx}" y="{ty}" class="h2">接線表（全部在正面，OK 線）</text>')
cols = [tx, tx + 46, tx + 92, tx + 300, tx + 470]
for x, h in zip(cols, ["線", "色", "起點", "終點", "用途"]):
    a(f'<text x="{x}" y="{ty+28}" class="th">{h}</text>')
a(f'<line x1="{tx}" y1="{ty+36}" x2="{W-20}" y2="{ty+36}" stroke="#d0d7de"/>')
for i, (no, cl, path, s0, s1, use) in enumerate(WIRES):
    yy = ty + 58 + i * 25
    a(f'<text x="{cols[0]}" y="{yy}" class="tb">{no}</text>')
    da = ' stroke-dasharray="6 4"' if no in ("K9", "K10") else ""
    a(f'<line x1="{cols[1]}" y1="{yy-5}" x2="{cols[1]+32}" y2="{yy-5}" stroke="{COL[cl]}" stroke-width="5"{da}/>')
    for x, v in zip(cols[2:], (s0, s1, use)):
        a(f'<text x="{x}" y="{yy}" class="tb" style="font-size:12px">{v}</text>')
ny = ty + 58 + len(WIRES) * 25 + 30
a(f'<text x="{tx}" y="{ny}" class="h2">零件</text>')
for i, t in enumerate(["U1 nice!nano v2：c3 / c9 兩排，列 1–12；USB-C 朝下凸出板邊",
                       "J1 ISO 7816 卡座：貼在背面，長邊 62 mm 與板子 61 mm 對齊",
                       "C10 0.1 µF：c1 r2（GND）↔ c1 r4（VCC）",
                       "BT1 LiPo：疊在正面上半部（列 13–24）"]):
    a(f'<text x="{tx}" y="{ny+28+i*24}" class="tb">● {t}</text>')
ny2 = ny + 28 + 4 * 24 + 26
a(f'<text x="{tx}" y="{ny2}" class="h2" style="fill:#b42318">待量測（目前是假設）</text>')
for i, t in enumerate(["卡座寬度：先估 40 mm",
                       "卡座左右兩排腳：假設左邊 C1–C4、右邊 C5–C8，上→下依序",
                       "腳的高度：照片估在離上緣約 20–32 mm（列 13–16）",
                       "偵測開關 SW1/SW2：假設在右側列 18、19",
                       "量完若左右相反，K3/K4 和 K5/K7 對調一邊即可",
                       "P0.08（UART_TX）、P1.06（U3_D1）老師圖上沒接任何東西，不焊"]):
    a(f'<text x="{tx}" y="{ny2+28+i*24}" class="tb">● {t}</text>')
a("</svg>")
open(OUT, "w", encoding="utf-8").write("\n".join(o))
print(W, H)
