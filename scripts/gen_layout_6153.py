"""2-D perfboard layout (21 x 16 holes) of the flat PCB version: front (parts) + back (wires, mirrored) + wiring table."""
import sys, re

OUT = sys.argv[1]
NC, NR, S = 21, 16, 30          # component block (unchanged layout)
GC, GR, DR, DC = 24, 20, 2, 0           # 61 (long) x 53 (wide, USB side) mm board = 24 x 20 holes; block 2 rows up, flush left
EX = (61.0 / 2.54 - GC) / 2      # board edge beyond the outer hole centres (in hole units)
EY = (53.0 / 2.54 - GR) / 2
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
a('<text x="30" y="42" class="h1">洞洞板 Layout — 平面版・USB 同側（長 61 × 寬 53 mm，24 × 20 孔，高約 12–13 mm 含電池）</text>')
a('<text x="30" y="66" class="sub">零件和線全部在正面（線用 OK 線），背面只有焊點。孔位 (c, r)：c＝欄 1–24、r＝列 1–20，一律以「正面俯視」為準；背面圖是翻過來看（左右相反），欄號照樣標出方便對照。</text>')


class Panel:
    def __init__(s, ox, oy, mirror): s.ox, s.oy, s.m = ox, oy, mirror
    def x(s, c): return s.ox + 40 + ((GC - (c + DC)) if s.m else (c + DC - 1)) * S
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
        s.rect(0.5 - EX - DC, GC + 0.5 + EX - DC, 0.5 - EY - DR, GR + 0.5 + EY - DR, fill="#1f5a3a", rx="6")
        for c in range(1 - DC, GC - DC + 1):
            for r in range(1 - DR, GR - DR + 1):
                a(f'<circle cx="{s.x(c)}" cy="{s.y(r)}" r="6.5" fill="#d9dde3"/><circle cx="{s.x(c)}" cy="{s.y(r)}" r="2.8" fill="#1f5a3a"/>')
            a(f'<text x="{s.x(c)}" y="{s.y(GR - DR + 0.5)-8}" class="ax" text-anchor="middle">{c + DC}</text>')
        for r in range(1 - DR, GR - DR + 1):
            side = s.x(GC - DC + 0.5) + 16 if s.m else s.x(0.5 - DC) - 16
            a(f'<text x="{side}" y="{s.y(r)+4}" class="ax" text-anchor="middle">{r + DR}</text>')
    def pins(s, cells, color="#e8b84a"):
        for c, r in cells:
            a(f'<rect x="{s.x(c)-5}" y="{s.y(r)-5}" width="10" height="10" fill="{color}" stroke="#7a5a10"/>')

nano = [(c, r) for c in range(1, 13) for r in (-1, 5)]
bp = [(c, r) for c in range(1, 21) for r in (11, 17)]
u3 = [(c, r) for c in (17, 18, 19) for r in (2, 5)]
U3N = {(17, 5): "G2", (18, 5): "S2", (19, 5): "G1", (17, 2): "D2", (18, 2): "S1", (19, 2): "D1"}  # real top view: pins 3-2-1 on top, 4-5-6 below
NANO_L = {(2, -1): "P0.08", (12, -1): "P1.06", (1, 5): "RAW", (2, 5): "GND"}
BP_L = {(1, 11): "B12", (6, 11): "PA9", (18, 11): "5V", (19, 11): "G", (20, 11): "3.3", (1, 17): "5V", (2, 17): "G", (3, 17): "3.3", (20, 17): "VB"}

# ---------- front ----------
F = Panel(30, 90, False)
F.grid("① 正面（零件面，俯視）— 線全部在這面", "零件都插在這面；所有線用 OK 線焊在零件腳上方；電池（橘虛框）用膠帶疊在 BlackPill 上")
F.rect(0.55, 20.45, 9.9, 18.1, fill="rgba(20,20,20,0.6)", stroke="#000", stroke_width="1.5", rx="3")
F.rect(-0.3, 2.8, 12.3, 15.7, fill="#e9ecef", stroke="#555"); F.label(1.25, 14, "USB-C", color="#333")
F.label(5.0, 15.1, "BlackPill", cls="pt"); F.label(5.0, 14.1, "（朝上，USB-C 朝左）", color="#ddd")
F.rect(0.0, 13.0, -1.45, 5.45, fill="rgba(20,20,20,0.6)", stroke="#000", stroke_width="1.5", rx="3")
F.rect(-0.7, 2.2, 0.3, 3.7, fill="#e9ecef", stroke="#555"); F.label(0.75, 2, "USB-C", color="#333")
F.label(6.5, 2.6, "nice!nano", cls="pt"); F.label(6.5, 1.6, "（朝上，USB-C 朝左）", color="#ddd")
F.rect(11.6, 15.3, -0.8, 4.8, fill="rgba(220,40,40,0.25)", stroke="#d62828", stroke_dasharray="4 3"); F.label(13.5, 2, "天線", color="#fff")
F.rect(16.0, 20.0, 1.25, 5.75, fill="rgba(40,160,70,0.85)", stroke="#0b5d1e", rx="3")
F.label(15.9, 5.4, "U3 DMC2038LVT", color="#e8fbe8", anchor="end")
F.rect(17.6, 19.4, -0.25, 0.25, fill="#e8d6a8", stroke="#7a5a10"); F.label(18.5, 0, "R1", color="#5a3d00")
F.rect(8.6, 20.4, 8.95, 18.8, fill="rgba(240,170,60,0.22)", stroke="#f0a030", stroke_width="2.5", stroke_dasharray="9 5")
F.label(14.5, 13.6, "電池 30×25×5（疊在 BlackPill 右段）", color="#ffc56b")
F.label(14.0, 7.9, "兩板中間空 5 排（第 8–12 排）", color="#9fd3b0")
F.pins(nano); F.pins(bp); F.pins(u3, "#f2d16b")
for (c, r), t in U3N.items():
    F.label(c, r, t, dy=-9 if r == 5 else 19)
for (c, r), t in NANO_L.items():
    F.label(c, r, t, color="#ffe9a8", dy=19 if r == -1 else -9)
for (c, r), t in BP_L.items():
    F.label(c, r, t, color="#ffe9a8", dy=-9 if r == 17 else 19)

WIRES = [  # no, colour, path, from, to, use   (all on the FRONT, OK wire)
    ("W1", "red", [(8.6, 9.7), (1, 9.7), (1, 5)], "電池 ＋（電池左端）", "nice!nano RAW (c1,r5)", "電池正極（RAW 即 B+）"),
    ("W2", "blk", [(8.6, 9.2), (2, 9.2), (2, 5)], "電池 －（電池左端）", "nice!nano GND (c2,r5)", "電池負極 → GND"),
    ("W3", "yel", [(6, 11), (6, 10.3), (4.5, 10.3), (4.5, -0.5), (2.5, -0.5), (2, -1)], "BlackPill PA9 (c6,r11)", "nice!nano P0.08 (c2,r-1)", "UART：BlackPill TX → nRF RX（跨過 nice!nano 上方）"),
    ("W4", "blk", [(2, 5), (2.6, 5.7), (3.3, 5.7), (3.3, 16.4), (2.4, 16.4), (2, 17)], "nice!nano GND (c2,r5)", "BlackPill G (c2,r17)", "兩板共地（跨過 BlackPill 上方）"),
    ("W5", "red", [(18, 11), (17.5, 10.4), (17, 9.2), (17, 5)], "BlackPill 5V (c18,r11)", "DMC2038LVT G2 腳3 (c17,r5)", "5V → G2"),
    ("W6", "blk", [(19, 11), (18.5, 10.4), (18, 9.2), (18, 5)], "BlackPill G (c19,r11)", "DMC2038LVT S2 腳2 (c18,r5)", "S2 → GND"),
    ("W7", "blk", [(18, 5), (18, 2)], "DMC2038LVT S2 腳2 (c18,r5)", "DMC2038LVT S1 腳5 (c18,r2)", "S1 → GND"),
    ("W8", "red", [(19, 5), (19.6, 4.4), (19.6, 3.3), (16.5, 3.3), (16.5, 2.5), (17, 2)], "DMC2038LVT G1 腳1 (c19,r5)", "DMC2038LVT D2 腳4 (c17,r2)", "G1 ↔ D2"),
    ("W9", "red", [(17, 2), (17, 0)], "DMC2038LVT D2 腳4 (c17,r2)", "R1 (c17,r0)", "D2 → R1"),
    ("W10", "org", [(19, 2), (20, 1), (20, 0)], "DMC2038LVT D1 腳6 (c19,r2)", "R1 (c20,r0)", "D1 → R1"),
    ("W11", "org", [(20, 0), (19.5, -0.5), (12.5, -0.5), (12, -1)], "R1 (c20,r0)", "nice!nano P1.06 (c12,r-1)", "D1 → nRF P1.06"),
]
for no, cl, path, *_ in WIRES:
    F.wire(path, COL[cl])
for c, r, t in ((6.6, 9.95, "W1 電池＋"), (6.6, 8.75, "W2 電池－"), (5.2, 7.0, "W3"), (3.8, 12.6, "W4"), (16.4, 8.0, "W5"),
                (18.6, 8.0, "W6"), (18.55, 4.2, "W7"), (15.9, 3.6, "W8"), (16.4, 1.0, "W9"), (20.7, 1.2, "W10"), (15.5, -0.05, "W11")):
    F.label(c, r, t, color="#fff")

# ---------- back ----------
B = Panel(30 + PW + 30, 90, True)
B.grid("② 背面（翻過來看，左右相反）", "背面不走線：只有零件腳的焊點（黃色方塊）")
B.pins(nano, "#c9a24a"); B.pins(bp, "#c9a24a"); B.pins(u3, "#c9a24a"); B.pins([(17, 0), (20, 0)], "#c9a24a")
B.label(11.5, 8.6, "背面不走任何線，整面保留給 IC 卡連接器（型號待定）", color="#9fd3b0")
B.label(11.5, 7.6, "零件腳焊好後剪平", color="#9fd3b0")

# ---------- table ----------
ty = PH + 110
a(f'<text x="30" y="{ty}" class="h2">接線表（全部走正面，用 OK 線）</text>')
cols = [30, 95, 160, 380, 610]
for x, h in zip(cols, ["線號", "顏色", "起點", "終點", "用途"]):
    a(f'<text x="{x}" y="{ty+30}" class="th">{h}</text>')
a(f'<line x1="30" y1="{ty+38}" x2="{W-30}" y2="{ty+38}" stroke="#d0d7de"/>')
for i, (no, cl, path, s0, s1, use) in enumerate(WIRES):
    yy = ty + 60 + i * 25
    a(f'<text x="{cols[0]}" y="{yy}" class="tb">{no}</text>')
    a(f'<line x1="{cols[1]}" y1="{yy-5}" x2="{cols[1]+40}" y2="{yy-5}" stroke="{COL[cl]}" stroke-width="5" stroke-linecap="round"/>')
    s0, s1 = (re.sub(r'\(c(\d+),r(-?\d+)\)', lambda m: f'(c{int(m.group(1)) + DC},r{int(m.group(2)) + DR})', t) for t in (s0, s1))
    for x, v in zip(cols[2:], (s0, s1, use)):
        a(f'<text x="{x}" y="{yy}" class="tb">{v}</text>')
nx = 980
notes = ["組裝順序：先插零件、從背面焊好腳並剪平 → 正面用 OK 線接線 → 最後貼電池",
         "洞洞板 長 61 × 寬 53 mm：USB-C 凸出左板邊約 2–3 mm；兩板中間空 5 排、上方空 1 排、右邊空 3 欄",
         "高約 12–13 mm（含電池；不含電池約 8 mm）",
         "電池疊在 BlackPill 右段，不擋 USB-C，也不超出板子",
         "電池紅黑線（W1/W2）從電池左端直接拉到 nice!nano 的 RAW / GND",
         "OK 線有絕緣，W3/W4 跨過電池線、W8 跨過 W7 都沒關係",
         "DMC2038LVT 俯視：上排 腳3 G2、腳2 S2、腳1 G1；下排 腳4 D2、腳5 S1、腳6 D1（1 號腳在右上）",
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
