"""Card-reader layout v5 (follows the teacher's boxed build): narrow perfboard 27.9 x 53.3 mm (11 x 21 holes),
socket legs into 8 holes on the board's right part, nice!nano bottom-left with USB-C down (opposite the slot).
All wires on the FRONT (OK wire)."""
import sys

OUT = sys.argv[1]
S = 30
NC, NR = 11, 21
SOCK_W, SOCK_H = 62.0, 34.0                     # long side (measured), short side (from teacher photo, ~13 holes)
BX = 31.2 - 7.5 * 2.54                          # board placed so the legs (socket X 31-39 mm) land in columns 8-11
RTOP = 21.5                                     # socket top edge (card slot) = board top edge
RBOT = RTOP - SOCK_H / 2.54                     # socket far edge
c_of = lambda Xmm: 0.5 + (Xmm - BX) / 2.54
TOPH = {"C8": (8, 21), "C7": (9, 21), "C6": (10, 21), "C5": (11, 21)}   # slot-edge legs -> holes
BOTH = {"C4": (8, 8), "C3": (9, 8), "C2": (10, 8), "C1": (11, 8)}       # far-edge legs -> holes
SWL = {"SW1": 12.6, "SW2": 13.6}                # detect switch legs (POSITION UNKNOWN), off-board right
C0, C1_, R0, R1_ = -8.0, 22.0, -2.2, RTOP + 8.0
PW = int((C1_ - C0) * S)
PH = int((R1_ - R0) * S)
W, H = PW + 720, max(PH + 150, 1150)
COL = {"red": "#d62828", "blk": "#1b1b1b", "yel": "#e3b505", "blu": "#1f6fd1", "grn": "#2a9d4b", "pur": "#8e44ad", "brn": "#8a5a2b"}
o = []; a = o.append
a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
a("""<style>text{font-family:'Microsoft JhengHei','Noto Sans TC',sans-serif;fill:#1f2328}
.h1{font-size:26px;font-weight:700}.h2{font-size:19px;font-weight:700}.sub{font-size:14px;fill:#57606a}
.ax{font-size:11px;fill:#6e7781}.pl{font-size:12px;font-weight:700}.pt{font-size:15px;font-weight:700}
.tb{font-size:13px}.th{font-size:13px;font-weight:700}.wn{font-size:12px;font-weight:700}</style>""")
a(f'<rect width="{W}" height="{H}" fill="#fff"/>')
a('<text x="30" y="42" class="h1">讀卡機 Layout v5 — 照老師盒裝版排法：卡座在右、nice!nano 在左下、USB-C 朝下（正面俯視）</text>')
a('<text x="30" y="66" class="sub">依老師 261103_nrf_card 線路圖＋紅字腳位（插卡口那排 C5–C8、對面那排 C1–C4）。線全部在正面，OK 線手焊；電池另外用雙面膠黏，只畫出它的兩條線。</text>')
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
rect(c_of(0), c_of(SOCK_W), RBOT, RTOP, fill="#2b2f36", stroke="#000", stroke_width="1.5", rx="5")
label(c_of(50), RTOP - 2.0, "J1 卡座（在板子背面）", color="#cfd6de", halo=False, cls="pt")
label(c_of(50), RTOP - 3.0, "62 × 34（寬為照片估計）", color="#cfd6de", halo=False)
label(c_of(50), RTOP - 4.0, "上緣＝插卡口", color="#cfd6de", halo=False)
# perfboard (standing)
rect(0.5, NC + 0.5, 0.5, NR + 0.5, fill="#1f5a3a", stroke="#0f3b25", rx="5")
for c in range(1, NC + 1):
    for r in range(1, NR + 1):
        a(f'<circle cx="{X(c)}" cy="{Y(r)}" r="6.5" fill="#d9dde3"/><circle cx="{X(c)}" cy="{Y(r)}" r="2.8" fill="#1f5a3a"/>')
for c in range(1, NC + 1):
    a(f'<text x="{X(c)}" y="{Y(0.5)+16}" class="ax" text-anchor="middle">{c}</text>')
for r in range(1, NR + 1):
    a(f'<text x="{X(NC + 0.5)+14}" y="{Y(r)+4}" class="ax" text-anchor="middle">{r}</text>')
label((NC + 1) / 2, -1.7, f"洞洞板 {NC*2.54:.1f} × {NR*2.54:.1f}（{NC} × {NR} 孔）直放", color="#1f2328", halo=False)

# socket legs into holes (grey squares) + leg stubs from the socket edge
for name, (c, r) in TOPH.items():
    a(f'<rect x="{X(c)-7}" y="{Y(r)-7}" width="14" height="14" fill="#b8bec6" stroke="#333" stroke-width="1.5"/>')
    label(c, r + 0.95, name, color="#1f2328", halo=False)
for name, (c, r) in BOTH.items():
    a(f'<rect x="{X(c)-7}" y="{Y(r)-7}" width="14" height="14" fill="#b8bec6" stroke="#333" stroke-width="1.5"/>')
    label(c, r - 0.62, name, color="#ffffff", dy=8)
for name, c in SWL.items():
    a(f'<rect x="{X(c)-3:.1f}" y="{Y(RBOT)-4:.1f}" width="6" height="16" fill="#9fb3c8" stroke="#555"/>')
    pass
label(SWL["SW2"] + 0.5, RBOT - 0.65, "SW1/SW2 偵測開關（位置待量）", color="#1f2328", halo=False, anchor="start")

# nice!nano rotated 180 deg (USB-C down): right column c13 = pins 1..12, left column c7 = pins 24..13
L, R_ = 1, 7
NR_ = ["P0.06", "P0.08", "GND", "GND", "P0.17", "P0.20", "P0.22", "P0.24", "P1.00", "P0.11", "P1.04", "P1.06"]
NL_ = ["RAW", "GND", "RST", "VCC", "P0.31", "P0.29", "P0.02", "P1.15", "P1.13", "P1.11", "P0.10", "P0.09"]
rect(L - 0.55, R_ + 0.55, -0.05, 12.95, fill="rgba(20,20,20,0.66)", stroke="#000", stroke_width="1.5", rx="3")
rect(2.4, 5.6, -0.8, 1.25, fill="#e9ecef", stroke="#555"); label(4.0, -0.1, "USB-C ↓", color="#333", halo=False)
rect(2.3, 5.7, 11.0, 12.95, fill="rgba(220,40,40,0.22)", stroke="#d62828", stroke_dasharray="4 3"); label(4.0, 12.0, "天線", color="#ffd0d0")
label(4.0, 2.55, "U1 nice!nano（轉 180°）", cls="pl")
for i in range(12):
    for c in (L, R_):
        a(f'<rect x="{X(c)-5}" y="{Y(i+1)-5}" width="10" height="10" fill="#e8b84a" stroke="#7a5a10"/>')
    label(R_ - 0.45, i + 1, NR_[i], color="#ffe9a8", anchor="end", cls="ax")
    label(L + 0.45, i + 1, NL_[i], color="#ffe9a8", anchor="start", cls="ax")
# C10 0.1uF between (5,2) GND and (5,4) VCC
rect(9.8, 11.2, 4.3, 4.75, fill="#d9b34a", stroke="#6b4d1e", rx="3"); label(10.5, 5.0, "C10", color="#1f2328", halo=False, cls="ax")
a(f'<rect x="{X(10)-5}" y="{Y(4)-5}" width="10" height="10" fill="#f2d16b" stroke="#7a5a10"/><rect x="{X(11)-5}" y="{Y(4)-5}" width="10" height="10" fill="#f2d16b" stroke="#7a5a10"/>')
rect(12.0, 17.6, 0.5, 7.4, fill="rgba(240,170,60,0.18)", stroke="#f0a030", stroke_width="2.5", stroke_dasharray="9 5", rx="4")
label(14.8, 5.0, "BT1 電池", color="#b45309", halo=False, cls="pt"); label(14.8, 4.2, "雙面膠另黏", color="#b45309", halo=False)

WIRES = [  # no, colour, path, from, to, use, dashed
    ("K1", "red", [(1, 4), (1.6, 3.5), (11, 3.5), (11, 8)], "VCC 腳21 (c1,r4)", "J1 C1 VCC (c11,r8)", "+3V3_CARD（經 C10 右腳，跨過 nice!nano）", False),
    ("K2", "blk", [(7, 4), (6.3, 4.5), (3.7, 4.5), (3.7, 13.9), (11, 13.9), (11, 21)], "GND 腳4 (c7,r4)", "J1 C5 GND (c11,r21)", "卡片 GND（跨過 nice!nano）", False),
    ("K3", "blu", [(7, 8), (7.6, 8.6), (10, 8.6), (10, 8)], "P0.24 腳8 (c7,r8)", "J1 C2 RST (c10,r8)", "RST", False),
    ("K4", "grn", [(7, 5), (9, 5), (9, 8)], "P0.17 腳5 (c7,r5)", "J1 C3 CLK (c9,r8)", "CLK", False),
    ("K5", "yel", [(7, 6), (6.3, 6.5), (4.3, 6.5), (4.3, 13.3), (9, 13.3), (9, 21)], "P0.20 腳6 (c7,r6)", "J1 C7 I/O (c9,r21)", "I/O（跨過 nice!nano）", False),
    ("K6", "yel", [(7, 6), (7.4, 6.5), (7, 7)], "P0.20 腳6 (c7,r6)", "P0.22 腳7 (c7,r7)", "I/O 兩腳併接", False),
    ("K7", "blk", [(7, 3), (7.4, 3.5), (7, 4)], "GND 腳3 (c7,r3)", "GND 腳4 (c7,r4)", "GND 兩腳併接", False),
    ("K10", "blk", [(7, 4), (10, 4)], "GND 腳4 (c7,r4)", "C10 左腳 (c10,r4)", "C10 接地", False),
    ("K8", "pur", [(7, 9), (7.6, 9.6), (SWL["SW1"], 9.6), (SWL["SW1"], RBOT)], "P1.00 腳9 (c7,r9)", "J1 SW1 DET", "插卡偵測（選配）", True),
    ("K9", "blk", [(SWL["SW2"], RBOT), (SWL["SW2"], 2.9), (10, 2.9), (10, 4)], "J1 SW2 DET_G", "C10 左腳 GND (c10,r4)", "偵測開關接地（選配，位置待量）", True),
    ("K11", "red", [(12.0, 0.9), (1.6, 0.9), (1, 1)], "電池 ＋", "RAW 腳24 (c1,r1)", "VBAT（跨過 nice!nano 下緣）", False),
    ("K12", "blk", [(12.0, 1.5), (1.6, 1.5), (1, 2)], "電池 －", "GND 腳23 (c1,r2)", "電池負極", False),
]
for no, cl, path, s0, s1, use, dash in WIRES:
    wire(path, COL[cl], dash)
for c, r, t in ((4.0, 3.75, "K1"), (7.5, 14.15, "K2"), (8.8, 8.85, "K3"), (8.2, 5.25, "K4"), (6.5, 13.55, "K5"),
                (7.7, 6.9, "K6"), (7.7, 3.0, "K7"), (8.6, 4.25, "K10"), (10.2, 9.85, "K8"), (14.1, 6.5, "K9")):
    label(c, r, t, cls="wn")
label(12.3, 0.1, "K11/K12", color="#1f2328", halo=False, cls="wn", anchor="start")

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
ny = ty + 58 + len(WIRES) * 25 + 24
a(f'<text x="{tx}" y="{ny}" class="h2">卡座 8 個洞</text>')
for i, t in enumerate(["插卡口那排（第 21 列）：C8 c8、C7 c9、C6 c10、C5 c11",
                       "對面那排（第 8 列）：C4 c8、C3 c9、C2 c10、C1 c11",
                       "兩排相隔 13 列（33 mm），照老師板子上的焊點估",
                       "只接 C1、C2、C3、C5、C7；C4、C6、C8 焊住固定"]):
    a(f'<text x="{tx}" y="{ny+26+i*24}" class="tb">● {t}</text>')
ny2 = ny + 26 + 4 * 24 + 22
a(f'<text x="{tx}" y="{ny2}" class="h2" style="fill:#b42318">照片推估、要再量的</text>')
for i, t in enumerate(["卡座寬 34 mm、腳在離卡座左緣 31–39 mm",
                       "偵測開關 SW1/SW2 的實際位置（先畫在板子右外側）",
                       "電池約 12 × 20 mm（照片估），雙面膠黏在 nice!nano 右邊",
                       "盒子內部尺寸還不知道，先沒畫盒子",
                       "老師盒裡那顆 3 pin 彎排針還不知道用途，先沒畫",
                       "K2、K5 跨過 nice!nano；K1 跨 K4；OK 線有絕緣沒關係"]):
    a(f'<text x="{tx}" y="{ny2+26+i*24}" class="tb">● {t}</text>')
a("</svg>")
open(OUT, "w", encoding="utf-8").write("\n".join(o))
print(W, H)
