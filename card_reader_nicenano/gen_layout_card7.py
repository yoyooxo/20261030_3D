"""Card-reader layout v7: recounted from the teacher photos (S__14311426 / 742949).
Perfboard 11 x 24 holes, socket legs in c8-c11 at rows 24 and 8, module (13 holes per side) bottom-left, USB-C down.
All wires on the FRONT (OK wire)."""
import sys

OUT = sys.argv[1]
S = 30
NC, NR = 11, 24
SOCK_W, SOCK_H = 62.0, 16.8 * 2.54                     # long side (measured); legs 16 holes apart on the teacher boards
BX = 4.4                                        # board left edge ~4 mm in from the socket left edge (teacher box photo)
RTOP = 24.5                                     # socket top edge (card slot) = board top edge
RBOT = RTOP - SOCK_H / 2.54                     # socket far edge
c_of = lambda Xmm: 0.5 + (Xmm - BX) / 2.54
TOPH = {"C5": (8, 24), "C6": (9, 24), "C7": (10, 24), "C8": (11, 24)}   # slot-edge legs (photo: 1st and 3rd wired)
BOTH = {"C1": (8, 8), "C2": (9, 8), "C3": (10, 8), "C4": (11, 8)}       # far-edge legs (photo: first three wired)
SWX = 12.3; SW1R, SW2R = 9.0, 8.2   # detect switch legs: just off the right board edge beside the lower leg row (photo)
C0, C1_, R0, R1_ = -3.0, 25.0, -3.2, RTOP + 8.0
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
a('<text x="30" y="42" class="h1">讀卡機 Layout v7 — 照老師實物照片重新數孔（正面俯視，插卡口在上）</text>')
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
label(c_of(47), RTOP - 2.0, "J1 卡座（在板子背面）", color="#cfd6de", halo=False, cls="pt")
label(c_of(47), RTOP - 3.0, "62 × 約 40（兩排腳相隔 16 孔）", color="#cfd6de", halo=False)
label(c_of(47), RTOP - 4.0, "上緣＝插卡口", color="#cfd6de", halo=False)
# perfboard (standing)
rect(0.5, NC + 0.5, 0.5, NR + 0.5, fill="#1f5a3a", stroke="#0f3b25", rx="5")
for c in range(1, NC + 1):
    for r in range(1, NR + 1):
        a(f'<circle cx="{X(c)}" cy="{Y(r)}" r="6.5" fill="#d9dde3"/><circle cx="{X(c)}" cy="{Y(r)}" r="2.8" fill="#1f5a3a"/>')
for c in range(1, NC + 1):
    a(f'<text x="{X(c)}" y="{Y(NR + 0.5)-6}" class="ax" text-anchor="middle">{c}</text>')
for r in range(1, NR + 1):
    a(f'<text x="{X(0.5)-12}" y="{Y(r)+4}" class="ax" text-anchor="middle" style="fill:{"#fff" if r > RBOT else "#6e7781"}">{r}</text>')
label((NC + 1) / 2, -2.7, f"洞洞板 {NC*2.54:.1f} × {NR*2.54:.1f} mm（{NC} × {NR} 孔）直放", color="#1f2328", halo=False)

# socket legs into holes (grey squares)
for name, (c, r) in TOPH.items():
    a(f'<rect x="{X(c)-7}" y="{Y(r)-7}" width="14" height="14" fill="#b8bec6" stroke="#333" stroke-width="1.5"/>')
    label(c, r + 1.25, name, color="#1f2328", halo=False)
for name, (c, r) in BOTH.items():
    a(f'<rect x="{X(c)-7}" y="{Y(r)-7}" width="14" height="14" fill="#b8bec6" stroke="#333" stroke-width="1.5"/>')
for name, (c, r), dc, dr in (("C1", (8, 8), 0, 0.62), ("C2", (9, 8), 0, 0.62), ("C3", (10, 8), 0, 0.62), ("C4", (11, 8), 0, 0.62)):
    label(c + dc, r + dr, name, color="#ffffff")
for rr in (SW1R, SW2R):
    a(f'<rect x="{X(SWX)-8:.1f}" y="{Y(rr)-4:.1f}" width="16" height="8" fill="#9fb3c8" stroke="#555"/>')
label(SWX + 0.5, SW1R, "SW1", color="#cfd6de", halo=False, anchor="start")
label(SWX + 0.5, SW2R, "SW2　偵測開關（位置照照片估）", color="#cfd6de", halo=False, anchor="start")

# module rotated 180 deg (USB-C down). 13 holes per side: row 0 = B+ / B- hangs below the board edge.
L, R_ = 1, 7
NR_ = ["B-", "P0.06", "P0.08", "GND", "GND", "P0.17", "P0.20", "P0.22", "P0.24", "P1.00", "P0.11", "P1.04", "P1.06"]
NL_ = ["B+", "RAW", "GND", "RST", "VCC", "P0.31", "P0.29", "P0.02", "P1.15", "P1.13", "P1.11", "P0.10", "P0.09"]
rect(L - 0.55, R_ + 0.55, -0.75, 12.95, fill="rgba(20,20,20,0.66)", stroke="#000", stroke_width="1.5", rx="3")
rect(2.5, 5.5, -1.6, 0.35, fill="#e9ecef", stroke="#555"); label(4.0, -0.75, "USB-C ↓", color="#333", halo=False)
rect(2.3, 5.7, 11.9, 12.75, fill="rgba(220,40,40,0.22)", stroke="#d62828", stroke_dasharray="4 3"); label(4.0, 12.3, "天線", color="#ffd0d0")
label(4.0, 10.3, "U1 nRF52840", cls="pl")
label(4.0, 9.6, "轉 180°", cls="ax")
for i in range(13):
    for c in (L, R_):
        a(f'<rect x="{X(c)-5}" y="{Y(i)-5}" width="10" height="10" fill="#e8b84a" stroke="#7a5a10"/>')
    label(R_ - 0.45, i, NR_[i], color="#ffe9a8", anchor="end", cls="ax")
    label(L + 0.45, i, NL_[i], color="#ffe9a8", anchor="start", cls="ax")
# C10 0.1uF: legs (8,6)=VCC on K1, (9,6)=GND
rect(7.9, 9.1, 5.78, 6.22, fill="#d9b34a", stroke="#6b4d1e", rx="3")
a(f'<rect x="{X(8)-5}" y="{Y(6)-5}" width="10" height="10" fill="#f2d16b" stroke="#7a5a10"/><rect x="{X(9)-5}" y="{Y(6)-5}" width="10" height="10" fill="#f2d16b" stroke="#7a5a10"/>')

WIRES = [  # no, colour, path, from, to, use, dashed
    ("K1", "red", [(1, 4), (1.6, 4.5), (8, 4.5), (8, 8)], "VCC (c1,r4)", "J1 C1 VCC (c8,r8)", "+3V3_CARD（跨過模組，途中接 C10）", False),
    ("K2", "blk", [(7, 3), (7.6, 2.5), (9.5, 2.5), (9.5, 23.3), (8.4, 23.3), (8, 24)], "GND (c7,r3)", "J1 C5 GND (c8,r24)", "卡片 GND", False),
    ("K3", "blu", [(7, 8), (7.6, 7.55), (9, 7.55), (9, 8)], "P0.24 (c7,r8)", "J1 C2 RST (c9,r8)", "RST", False),
    ("K4", "grn", [(7, 5), (7.6, 5.3), (10, 5.3), (10, 8)], "P0.17 (c7,r5)", "J1 C3 CLK (c10,r8)", "CLK", False),
    ("K5", "yel", [(7, 7), (7.6, 6.8), (10.5, 6.8), (10.5, 23.3), (10, 24)], "P0.22 (c7,r7)", "J1 C7 I/O (c10,r24)", "I/O", False),
    ("K6", "yel", [(7, 6), (6.6, 6.5), (7, 7)], "P0.20 (c7,r6)", "P0.22 (c7,r7)", "I/O 兩腳併接", False),
    ("K7", "blk", [(7, 3), (6.6, 3.5), (7, 4)], "GND (c7,r3)", "GND (c7,r4)", "GND 兩腳併接", False),
    ("K10", "blk", [(7, 4), (7.6, 3.6), (9, 3.6), (9, 6)], "GND (c7,r4)", "C10 GND 腳 (c9,r6)", "C10 接地", False),
    ("K8", "pur", [(7, 9), (7.6, 9.5), (SWX, 9.5), (SWX, SW1R)], "P1.00 (c7,r9)", "J1 SW1 DET", "插卡偵測（選配）", True),
    ("K9", "blk", [(SWX, SW2R), (SWX, 6.35), (9.3, 6.35), (9, 6)], "J1 SW2 DET_G", "C10 GND 腳 (c9,r6)", "偵測開關接地（選配）", True),
    ("K11", "red", [(8.3, 0.75), (1.6, 0.75), (1, 1)], "電池 ＋", "RAW (c1,r1)", "VBAT（照老師：接 RAW，B+ 空著）", False),
    ("K12", "blk", [(8.3, 1.6), (1.6, 1.6), (1, 2)], "電池 －", "GND (c1,r2)", "電池負極", False),
]
for no, cl, path, s0, s1, use, dash in WIRES:
    wire(path, COL[cl], dash)
label(8.5, 6.0, "C10", color="#1f2328", halo=False, cls="ax")
# battery: only the lower part is outlined so the wires stay readable
rect(7.85, 13.0, -0.6, 2.2, fill="rgba(240,170,60,0.10)", stroke="#f0a030", stroke_width="2.5", stroke_dasharray="9 5", rx="4")
label(13.3, 1.2, "← BT1 電池（實際約 13 × 23，會往上蓋到第 8 列；", color="#b45309", halo=False, cls="pl", anchor="start")
label(13.3, 0.4, "　 這裡只畫下半免得擋線。最後用雙面膠黏）", color="#b45309", halo=False, cls="pl", anchor="start")
for c, r, t in ((4.0, 4.78, "K1"), (9.0, 15.0, "K2"), (8.5, 7.25, "K3"), (10.45, 5.0, "K4"), (11.0, 15.0, "K5"),
                (6.1, 6.5, "K6"), (6.1, 3.5, "K7"), (8.3, 3.3, "K10"), (11.3, 9.8, "K8"), (11.3, 6.05, "K9"), (4.0, 1.05, "K11"), (4.0, 1.9, "K12")):
    label(c, r, t, cls="wn")

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
a(f'<text x="{tx}" y="{ny}" class="h2">照片上確定的</text>')
for i, t in enumerate(["洞洞板 11 × 24 孔（從 S__14311426 數的；v6 的 12 × 22 不對）",
                       "卡座兩排腳在最右 4 欄 c8–c11，相隔 16 孔：第 24 列、第 8 列",
                       "下排腳跟 P0.24 同一列（第 8 列）",
                       "插卡口那排接線的是第 1、3 支 → 左到右 C5 C6 C7 C8",
                       "對面那排前 3 支有接線 → 左到右 C1 C2 C3 C4（v6 左右相反）",
                       "模組每邊 13 孔，最靠 USB 那對是 B+ / B-，凸出板子下緣",
                       "老師電池＋焊在 RAW，B+ 那孔空著",
                       "偵測開關兩支腳在板子右緣外、下排腳旁邊"]):
    a(f'<text x="{tx}" y="{ny+26+i*24}" class="tb">● {t}</text>')
ny2 = ny + 26 + 8 * 24 + 22
a(f'<text x="{tx}" y="{ny2}" class="h2" style="fill:#b42318">照片看不出來、要你確認的</text>')
for i, t in enumerate(["C1–C8 左右順序是從照片接線判斷的，焊之前用電表量一次",
                       "哪一排是插卡口那側（目前照你說的：上面）",
                       "老師的模組是平貼黏上去；這版把腳插進 c1 / c7 的洞",
                       "線有交叉（K1 跨過模組）；OK 線有絕緣沒關係"]):
    a(f'<text x="{tx}" y="{ny2+26+i*24}" class="tb">● {t}</text>')
a("</svg>")
open(OUT, "w", encoding="utf-8").write("\n".join(o))
print(W, H)
