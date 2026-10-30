"""Annotated overview: KiCad SVG export + coloured function zones + legend + path chips."""
import sys, base64

KSVG, OUT = sys.argv[1], sys.argv[2]
W, H = 2200, 1250
# crop window of the KiCad page (mm)
CX, CY, CW, CH = 8, 20, 279, 138
PX, PY, PW = 40, 132, 1640
K = PW / CW
PH = CH * K

def d2mm(x, y):
    """coords measured on the 8 px/mm preview crop (display scale 1.1) -> page mm"""
    return ((x * 1.1 + 80) / 8, (y * 1.1 + 180) / 8)

ZONES = [  # letter, colour, (x1,y1,x2,y2) in preview-display px
    ("A", "#2b6cd9", (395, -2, 575, 95)),
    ("B", "#7c4a2d", (45, 170, 302, 572)),
    ("C", "#4f46e5", (312, 518, 1555, 556)),
    ("D", "#222222", (765, 155, 1110, 400)),
    ("E", "#e08600", (135, 612, 425, 778)),
    ("F", "#0e9488", (1280, 598, 1528, 790)),
    ("G", "#2f9e44", (1540, 5, 1885, 882)),
    ("H", "#dc2626", (590, 32, 662, 334)),
    ("H", "#dc2626", (305, 338, 752, 368)),
]
LEGEND = [
    ("A", "#2b6cd9", "電池 BT1", "LiPo 經熱縮 2pin 排針插在欄22(+)/23(−)；不在電源軌；正極接 RAW"),
    ("B", "#7c4a2d", "nice!nano U1（nRF52840）", "欄1–12；腳位已對照官方 pinout 與板上絲印 009/010/104/106"),
    ("C", "#4f46e5", "UART 連線", "PA9(TX) → P0.08(RX) 方向正確；J2 第6腳可監看；反向未接"),
    ("D", "#222222", "U3 3.3V LDO（推斷）+ R1", "依接法推斷為 AP2112K-3.3 同腳位系列；5V → 3.3V → R1 負載"),
    ("E", "#e08600", "nRF SWD 引出 J4 ⇄ J1", "紫線束→板底 [UNVERIFIED]；欄15/17/18 跨溝，欄16 未接"),
    ("F", "#0e9488", "BlackPill SWD 引出 J3 ⇄ J2", "紫線束→SWD 排孔 [UNVERIFIED]；欄36/38/39 跨溝，欄37 未接"),
    ("G", "#2f9e44", "BlackPill U2（STM32F401/F411）", "欄44–63；排針順序已對照 WeAct 官方；晶片可見 ST 商標（F401/F411 腳位相同）"),
    ("H", "#dc2626", "⚠ 問題點", "電池負極接到 P0.06（不是 GND）；P1.06 可能與 GND 同欄 [UNVERIFIED]"),
]
FLOWS = [
    ("資料（UART）", "#1e64d2", ["BlackPill PA9（欄58）", "綠線 → 欄41", "黃線 → 欄19", "橘線 → 欄2", "nRF P0.08（RX）"]),
    ("電源", "#c81e1e", ["LiPo ＋（欄22）", "紅線 → 欄1", "nRF RAW", "BlackPill 5V（欄46）", "U3 VIN", "3.3V → R1 負載"]),
    ("⚠ 問題", "#dc2626", ["LiPo −（欄23）", "黃線 → 欄1", "nRF P0.06（TX）", "應改接 GND（欄3/4/20）"]),
]

ks = base64.b64encode(open(KSVG, "rb").read()).decode()
S = []
a = S.append
a(f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
a("""<style>
text{font-family:'Microsoft JhengHei','Noto Sans TC','PingFang TC',sans-serif;fill:#1f2328}
.h1{font-size:40px;font-weight:700}.sub{font-size:19px;fill:#57606a}
.h2{font-size:23px;font-weight:700}.lt{font-size:19px;font-weight:700}.ld{font-size:15px;fill:#57606a}
.chip{font-size:17px;font-weight:600}.row{font-size:17px;font-weight:700}.foot{font-size:15px;fill:#6e7781}
.badge{font-size:15px;font-weight:700;fill:#fff}
</style>""")
a(f'<rect width="{W}" height="{H}" fill="#ffffff"/>')
a('<text x="40" y="60" class="h1">麵包板線路還原（由三張照片判讀）</text>')
a('<text x="40" y="96" class="sub">nice!nano（nRF52840）＋ WeAct BlackPill（STM32F401/F411）｜欄號為麵包板座標，誤差約 ±1 欄｜[UNVERIFIED] = 照片無法證實</text>')
a('<rect x="40" y="110" width="1640" height="4" rx="2" fill="#d0d7de"/>')

# schematic panel
a(f'<rect x="{PX-6}" y="{PY-6}" width="{PW+12}" height="{PH+12}" rx="6" fill="#fffef7" stroke="#d0d7de"/>')
a(f'<svg x="{PX}" y="{PY}" width="{PW}" height="{PH}" viewBox="{CX} {CY} {CW} {CH}">')
a(f'<image x="0" y="0" width="297.0022" height="210.0072" preserveAspectRatio="none" href="data:image/svg+xml;base64,{ks}" xlink:href="data:image/svg+xml;base64,{ks}"/>')
for letter, col, (x1, y1, x2, y2) in ZONES:
    (mx1, my1), (mx2, my2) = d2mm(x1, y1), d2mm(x2, y2)
    a(f'<rect x="{mx1:.2f}" y="{my1:.2f}" width="{mx2-mx1:.2f}" height="{my2-my1:.2f}" rx="0.8" fill="none" stroke="{col}" stroke-width="0.7" stroke-dasharray="2.2 1.2"/>')
    a(f'<rect x="{mx1-0.4:.2f}" y="{my1-0.4:.2f}" width="5" height="5" rx="0.8" fill="{col}"/>')
    a(f'<text x="{mx1+2.1:.2f}" y="{my1+3.5:.2f}" text-anchor="middle" style="font-size:3.6px;font-weight:700;fill:#fff">{letter}</text>')
a("</svg>")

# legend
LX = 1720
a(f'<text x="{LX}" y="150" class="h2">功能分區</text>')
for i, (letter, col, title, desc) in enumerate(LEGEND):
    y = 200 + i * 82
    a(f'<rect x="{LX}" y="{y-17}" width="26" height="26" rx="4" fill="{col}"/>')
    a(f'<text x="{LX+12}" y="{y+1}" text-anchor="middle" class="badge">{letter}</text>')
    a(f'<text x="{LX+36}" y="{y+1}" class="lt">{title}</text>')
    # wrap description at ~26 CJK chars
    line, lines = "", []
    for ch in desc:
        line += ch
        if sum(2 if ord(c) > 0x2E80 else 1 for c in line) >= 44 and ch in "；，、 ）":
            lines.append(line); line = ""
    if line: lines.append(line)
    for j, ln in enumerate(lines):
        a(f'<text x="{LX+36}" y="{y+25+j*19}" class="ld">{ln}</text>')
a(f'<text x="{LX}" y="{200+8*82}" class="ld">黑虛線 N36：兩組 SWD 排針第1腳＋下方 − 軌，</text>')
a(f'<text x="{LX}" y="{200+8*82+19}" class="ld">推論為 GND（未經證實）。</text>')

# path chips
FY = PY + PH + 50
a(f'<text x="40" y="{FY}" class="h2">訊號與電源路徑</text>')
def cw(s):
    return sum(18 if ord(c) > 0x2E80 else 10 for c in s) + 32
for r, (name, col, chips) in enumerate(FLOWS):
    y = FY + 30 + r * 62
    a(f'<text x="40" y="{y+27}" class="row" fill="{col}" style="fill:{col}">{name}</text>')
    x = 190
    for k, c in enumerate(chips):
        if name == "電源" and k == 3:  # second, independent power path
            a(f'<text x="{x+4}" y="{y+27}" class="ld">｜</text>'); x += 26
        w = cw(c)
        warn = name.startswith("⚠")
        fill = "#fff1f0" if warn else "#f6f8fa"
        a(f'<rect x="{x}" y="{y}" width="{w}" height="44" rx="10" fill="{fill}" stroke="{col if warn else "#c9d1d9"}" stroke-width="1.5"/>')
        a(f'<text x="{x+w/2}" y="{y+28}" text-anchor="middle" class="chip">{c}</text>')
        x += w
        nxt = k + 1 < len(chips) and not (name == "電源" and k == 2)
        if nxt:
            a(f'<path d="M{x+8},{y+20} h18 m-7,-7 l7,7 l-7,7" stroke="#57606a" stroke-width="2.2" fill="none"/>')
            x += 36
        else:
            x += 10
a(f'<text x="40" y="{H-22}" class="foot">來源：麵包板照片 740779 / 740780 / 740781.jpg 交叉判讀；以 KiCad 10.0.7 繪製。nRF 腳位依 nice!nano 官方 pinout，BlackPill SWD 依 WeAct / Zephyr 文件。</text>')
a("</svg>")
open(OUT, "w", encoding="utf-8").write("\n".join(S))
print("wrote")
