"""2-D perfboard layout (21 x 16 holes) of the flat PCB version: front (parts) + back (wires, mirrored) + wiring table."""
import sys, re

OUT = sys.argv[1]
NC, NR, S = 21, 16, 30          # component block (unchanged layout)
GC, GR, DR = 24, 24, 4           # 62 x 62 mm board = 24 x 24 holes; block sits 4 rows up, flush left
EDGE = (62.0 / 2.54 - 24) / 2    # board edge beyond the outer hole centres (in hole units)
PW, PH = GC * S + 100, GR * S + 170
W, H = 2 * PW + 60, PH + 520
COL = {"red": "#d62828", "blk": "#1b1b1b", "yel": "#e3b505", "org": "#f07d14"}
o = []
a = o.append
a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
a("""<style>text{font-family:'Microsoft JhengHei','Noto Sans TC',sans-serif;fill:#1f2328}
.h1{font-size:26px;font-weight:700}.h2{font-size:19px;font-weight:700}.sub{font-size:14px;fill:#57606a}
.ax{font-size:11px;fill:#6e7781}.pl{font-size:11px;font-weight:700}.pt{font-size:14px;font-weight:700}
.tb{font-size:13px}.th{font-size:13px;font-weight:700}</style>""")
a(f'<rect width="{W}" height="{H}" fill="#fff"/>')
a('<text x="30" y="42" class="h1">洞洞板 Layout — 平面版・USB 同側（62 × 62 mm，24 × 24 孔）</text>')
a('<text x="30" y="66" class="sub">零件全部在正面、線全部走背面。孔位 (c, r)：c＝欄 1–24、r＝列 1–24，一律以「正面俯視」為準；背面圖是翻過來看（左右相反），欄號照樣標出方便對照。</text>')


class Panel:
    def __init__(s, ox, oy, mirror): s.ox, s.oy, s.m = ox, oy, mirror
    def x(s, c): return s.ox + 40 + ((GC - c) if s.m else (c - 1)) * S
    def y(s, r): return s.oy + 90 + (GR - (r + DR)) * S
    def rect(s, c0, c1, r0, r1, **kw):
        xa, xb = sorted((s.x(c0), s.x(c1))); ya, yb = sorted((s.y(r0), s.y(r1)))
        at = " ".join(f'{k.replace("_", "-")}="{v}"' for k, v in kw.items())
        a(f'<rect x="{xa:.1f}" y="{ya:.1f}" width="{xb-xa:.1f}" height="{yb-ya:.1f}" {at}/>')
    def label(s, c, r, t, cls="pl", color="#fff", dy=4, anchor="middle"):
        a(f'<text x="{s.x(c):.1f}" y="{s.y(r)+dy:.1f}" class="{cls}" text-anchor="{anchor}" style="fill:{color}">{t}</text>')
    def wire(s, pts, color, dash=False):
        d = "M" + " L".join(f"{s.x(c):.1f},{s.y(r):.1f}" for c, r in pts)
        da = ' stroke-dasharray="8 5"' if dash else ""
        a(f'<path d="{d}" stroke="#fff" stroke-width="7" fill="none" stroke-linecap="round" stroke-linejoin="round"/>')
        a(f'<path d="{d}" stroke="{color}" stroke-width="4" fill="none" stroke-linecap="round" stroke-linejoin="round"{da}/>')
        for c, r in (pts[0], pts[-1]):
            a(f'<circle cx="{s.x(c):.1f}" cy="{s.y(r):.1f}" r="5" fill="{color}" stroke="#fff" stroke-width="1.5"/>')
    def grid(s, title, sub):
        a(f'<text x="{s.ox}" y="{s.oy+18}" class="h2">{title}</text><text x="{s.ox}" y="{s.oy+40}" class="sub">{sub}</text>')
        s.rect(0.5 - EDGE, GC + 0.5 + EDGE, 0.5 - EDGE - DR, GR + 0.5 + EDGE - DR, fill="#1f5a3a", rx="6")
        for c in range(1, GC + 1):
            for r in range(1 - DR, GR - DR + 1):
                a(f'<circle cx="{s.x(c)}" cy="{s.y(r)}" r="6.5" fill="#d9dde3"/><circle cx="{s.x(c)}" cy="{s.y(r)}" r="2.8" fill="#1f5a3a"/>')
            a(f'<text x="{s.x(c)}" y="{s.y(GR - DR + 0.5)-8}" class="ax" text-anchor="middle">{c}</text>')
        for r in range(1 - DR, GR - DR + 1):
            side = s.x(GC + 0.5) + 16 if s.m else s.x(0.5) - 16
            a(f'<text x="{side}" y="{s.y(r)+4}" class="ax" text-anchor="middle">{r + DR}</text>')
    def pins(s, cells, color="#e8b84a"):
        for c, r in cells:
            a(f'<rect x="{s.x(c)-5}" y="{s.y(r)-5}" width="10" height="10" fill="{color}" stroke="#7a5a10"/>')

nano = [(c, r) for c in range(2, 14) for r in (1, 7)]
bp = [(c, r) for c in range(1, 21) for r in (9, 15)]
u3 = [(c, r) for c in (17, 18, 19) for r in (3, 6)]
U3N = {(17, 6): "G1", (18, 6): "S2", (19, 6): "G2", (17, 3): "D1", (18, 3): "S1", (19, 3): "D2"}
NANO_L = {(3, 1): "P0.08", (13, 1): "P1.06", (2, 7): "RAW", (3, 7): "GND"}
BP_L = {(1, 9): "B12", (6, 9): "PA9", (18, 9): "5V", (19, 9): "G", (20, 9): "3.3", (1, 15): "5V", (2, 15): "G", (3, 15): "3.3", (20, 15): "VB"}

# ---------- front ----------
F = Panel(30, 90, False)
F.grid("① 正面（零件面，俯視）", "nice!nano、BlackPill、DMC2038LVT、R1 都插在這面；電池（橘虛框）用膠帶疊在 BlackPill 上")
F.rect(0.55, 20.45, 7.9, 16.1, fill="rgba(20,20,20,0.6)", stroke="#000", stroke_width="1.5", rx="3")
F.rect(-0.3, 2.8, 10.3, 13.7, fill="#e9ecef", stroke="#555"); F.label(1.25, 12, "USB-C", color="#333")
F.label(9.5, 13.1, "BlackPill", cls="pt"); F.label(9.5, 12.1, "（朝上，USB-C 朝左）", color="#ddd")
F.rect(1.0, 14.0, 0.55, 7.45, fill="rgba(20,20,20,0.6)", stroke="#000", stroke_width="1.5", rx="3")
F.rect(0.3, 3.2, 2.3, 5.7, fill="#e9ecef", stroke="#555"); F.label(1.75, 4, "USB-C", color="#333")
F.label(7.5, 4.6, "nice!nano", cls="pt"); F.label(7.5, 3.6, "（朝上，USB-C 朝左）", color="#ddd")
F.rect(12.6, 15.3, 1.2, 6.8, fill="rgba(220,40,40,0.25)", stroke="#d62828", stroke_dasharray="4 3"); F.label(14.0, 4, "天線", color="#fff")
F.rect(16.0, 20.0, 2.25, 6.75, fill="rgba(40,160,70,0.85)", stroke="#0b5d1e", rx="3")
F.label(18, 4.6, "DMC2038LVT", color="#e8fbe8")
F.rect(17.6, 19.4, 0.75, 1.25, fill="#e8d6a8", stroke="#7a5a10"); F.label(18.5, 1, "R1", color="#5a3d00")
F.rect(5.2, 17.0, 8.6, 16.45, fill="rgba(240,170,60,0.22)", stroke="#f0a030", stroke_width="2.5", stroke_dasharray="9 5")
F.label(11.1, 10.6, "電池 30×25（疊在上面，往上凸出 3 mm）", color="#ffc56b")
F.pins(nano); F.pins(bp); F.pins(u3, "#f2d16b")
for (c, r), t in U3N.items():
    F.label(c, r, t, dy=-9 if r == 6 else 19)
for (c, r), t in NANO_L.items():
    F.label(c, r, t, color="#ffe9a8", dy=19 if r == 1 else -9)
for (c, r), t in BP_L.items():
    F.label(c, r, t, color="#ffe9a8", dy=-9 if r == 15 else 19)
F.wire([(17, 6), (16.5, 6.5), (16.5, 2.6), (19.5, 2.6), (19, 3)], COL["red"], dash=True)
F.label(15.9, 4.6, "W8", color="#fff", anchor="end")

# ---------- back ----------
B = Panel(30 + PW + 30, 90, True)
B.grid("② 背面（翻過來看，左右相反）", "所有接線都在這面焊；黃色方塊＝要焊的腳")
B.pins(nano, "#c9a24a"); B.pins(bp, "#c9a24a"); B.pins(u3, "#c9a24a"); B.pins([(17, 1), (20, 1)], "#c9a24a")
WIRES = [  # no, colour, path, from, to, use
    ("W1", "red", [(-0.4, 7.6), (1.4, 7.6), (2, 7)], "電池 ＋", "nice!nano RAW (c2,r7)", "電池正極（RAW 即 B+）"),
    ("W2", "blk", [(-0.4, 8.2), (2.6, 8.2), (3, 7)], "電池 －", "nice!nano GND (c3,r7)", "電池負極 → GND"),
    ("W3", "yel", [(6, 9), (5.5, 8.5), (3.5, 8.5), (3.5, 1.5), (3, 1)], "BlackPill PA9 (c6,r9)", "nice!nano P0.08 (c3,r1)", "UART：BlackPill TX → nRF RX"),
    ("W4", "blk", [(3, 7), (2.5, 7.5), (2.5, 14.5), (2, 15)], "nice!nano GND (c3,r7)", "BlackPill G (c2,r15)", "兩板共地"),
    ("W5", "red", [(18, 9), (18.5, 8.4), (19, 7.2), (19, 6)], "BlackPill 5V (c18,r9)", "DMC2038LVT G2 (c19,r6)", "5V → G2"),
    ("W6", "blk", [(19, 9), (19.5, 8.5), (20.5, 8.0), (20.5, 5.6), (18.6, 5.6), (18, 6)], "BlackPill G (c19,r9)", "DMC2038LVT S2 (c18,r6)", "S2 → GND"),
    ("W7", "blk", [(18, 6), (18, 3)], "DMC2038LVT S2 (c18,r6)", "DMC2038LVT S1 (c18,r3)", "S1 → GND"),
    ("W8", "red", None, "DMC2038LVT G1 (c17,r6)", "DMC2038LVT D2 (c19,r3)", "G1 ↔ D2（焊在轉接板正面，虛線）"),
    ("W9", "red", [(19, 3), (20, 2), (20, 1)], "DMC2038LVT D2 (c19,r3)", "R1 (c20,r1)", "D2 → R1"),
    ("W10", "org", [(17, 3), (17, 1)], "DMC2038LVT D1 (c17,r3)", "R1 (c17,r1)", "D1 → R1"),
    ("W11", "org", [(17, 1), (16, 1.5), (14, 1.5), (13, 1)], "R1 (c17,r1)", "nice!nano P1.06 (c13,r1)", "D1 → nRF P1.06"),
]
for no, cl, path, *_ in WIRES:
    if path:
        B.wire(path, COL[cl])
for c, r, t in ((4.6, 8.95, "W3 UART"), (2.0, 11.0, "W4"), (18.3, 7.6, "W5"), (20.0, 7.0, "W6"), (18.5, 4.5, "W7"),
                (20.5, 2.0, "W9"), (17.5, 2.0, "W10"), (15.0, 2.0, "W11"), (1.2, 8.75, "W1/W2")):
    B.label(c, r, t, color="#fff")
for (c, r), t in {(6, 9): "PA9", (2, 15): "G", (18, 9): "5V", (19, 9): "G", (2, 7): "RAW", (3, 7): "GND", (3, 1): "P0.08", (13, 1): "P1.06"}.items():
    B.label(c, r, t, color="#ffe9a8", dy=-9 if r in (15, 7) else 19)
for (c, r), t in U3N.items():
    B.label(c, r, t, color="#cfd6de", dy=-9 if r == 6 else 19)
B.label(12.5, 17.5, "這面整面保留給 IC 卡連接器（型號待定）", color="#9fd3b0")

# ---------- table ----------
ty = PH + 110
a(f'<text x="30" y="{ty}" class="h2">接線表（線全部走背面）</text>')
cols = [30, 95, 160, 380, 610]
for x, h in zip(cols, ["線號", "顏色", "起點", "終點", "用途"]):
    a(f'<text x="{x}" y="{ty+30}" class="th">{h}</text>')
a(f'<line x1="30" y1="{ty+38}" x2="{W-30}" y2="{ty+38}" stroke="#d0d7de"/>')
for i, (no, cl, path, s0, s1, use) in enumerate(WIRES):
    yy = ty + 60 + i * 25
    a(f'<text x="{cols[0]}" y="{yy}" class="tb">{no}</text>')
    a(f'<line x1="{cols[1]}" y1="{yy-5}" x2="{cols[1]+40}" y2="{yy-5}" stroke="{COL[cl]}" stroke-width="5" stroke-linecap="round"/>')
    s0, s1 = (re.sub(r'r(\d+)\)', lambda m: f'r{int(m.group(1)) + DR})', t) for t in (s0, s1))
    for x, v in zip(cols[2:], (s0, s1, use)):
        a(f'<text x="{x}" y="{yy}" class="tb">{v}</text>')
nx = 980
notes = ["組裝順序：先焊背面的線 → 再插正面零件焊接 → 最後貼電池",
         "洞洞板 62 × 62 mm：零件靠左（USB-C 貼左緣），上下各留空間",
         "DMC2038LVT 腳位依 datasheet，方向依 1 號腳推定",
         "nice!nano 天線端（紅虛框）右邊保持空著",
         "兩個 USB-C 都在左邊（同一側）",
         "電池會蓋住 BlackPill 的按鍵，燒錄時要先掀開",
         "電池 30×25×5 mm 為照片估計值"]
a(f'<text x="{nx}" y="{ty}" class="h2">注意</text>')
for i, t in enumerate(notes):
    a(f'<text x="{nx}" y="{ty+32+i*26}" class="tb">● {t}</text>')
a("</svg>")
open(OUT, "w", encoding="utf-8").write("\n".join(o))
print(W, H)
