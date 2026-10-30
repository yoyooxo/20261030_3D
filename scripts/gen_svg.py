"""Hand-laid SVG schematic of the photo-derived breadboard circuit."""
import sys

OUT = sys.argv[1]
W, H = 1700, 1180
S = []
add = S.append

STY = {
    "power": 'stroke="#c81e1e" stroke-width="4" fill="none"',
    "gnd":   'stroke="#111" stroke-width="3" fill="none"',
    "gnd?":  'stroke="#111" stroke-width="2.5" stroke-dasharray="10 6" fill="none"',
    "sig":   'stroke="#1e64d2" stroke-width="3" fill="none"',
    "swd":   'stroke="#8e44ad" stroke-width="3" fill="none"',
    "bundle": 'stroke="#8e44ad" stroke-width="4" stroke-dasharray="4 6" fill="none"',
    "warn":  'stroke="#e66e00" stroke-width="4.5" stroke-dasharray="14 7" fill="none"',
    "unv":   'stroke="#888" stroke-width="2.5" stroke-dasharray="6 6" fill="none"',
    "misc":  'stroke="#444" stroke-width="2" fill="none"',
}

def path(pts, st):
    d = "M" + " L".join(f"{x},{y}" for x, y in pts)
    add(f'<path d="{d}" {STY[st]}/>')

def dot(x, y, c="#111"):
    add(f'<circle cx="{x}" cy="{y}" r="5" fill="{c}"/>')

def openpin(x, y, note="未見接線", anchor="start"):
    add(f'<circle cx="{x}" cy="{y}" r="5" fill="#fff" stroke="#999" stroke-width="1.5"/>')
    dx = 10 if anchor == "start" else -10
    add(f'<text x="{x+dx}" y="{y+4}" class="na" text-anchor="{anchor}">{note}</text>')

def text(x, y, s, cls="t", anchor="start"):
    for i, line in enumerate(s.split("\n")):
        add(f'<text x="{x}" y="{y + i*19}" class="{cls}" text-anchor="{anchor}">{line}</text>')

def box(x1, y1, x2, y2, title, sub="", fill="#fbfbf6", dashed=False):
    da = ' stroke-dasharray="8 5"' if dashed else ""
    add(f'<rect x="{x1}" y="{y1}" width="{x2-x1}" height="{y2-y1}" rx="6" fill="{fill}" stroke="#333" stroke-width="2"{da}/>')
    text((x1+x2)/2, y1 - 26 if sub else y1 - 10, title, "bt", "middle")
    if sub:
        text((x1+x2)/2, y1 - 8, sub, "bs", "middle")

def pin_r(xb, y, name, stub=30):
    """pin on right edge of a box at xb; returns stub end"""
    add(f'<line x1="{xb}" y1="{y}" x2="{xb+stub}" y2="{y}" stroke="#333" stroke-width="2"/>')
    text(xb - 8, y + 5, name, "pn", "end")
    return xb + stub

def pin_l(xb, y, name, stub=30):
    add(f'<line x1="{xb-stub}" y1="{y}" x2="{xb}" y2="{y}" stroke="#333" stroke-width="2"/>')
    text(xb + 8, y + 5, name, "pn", "start")
    return xb - stub

def tag(x, y, s, color, anchor="start"):
    w = sum(15 if ord(c) > 0x2E80 else 8 for c in s) + 14
    x0 = x if anchor == "start" else x - w
    add(f'<rect x="{x0}" y="{y-12}" width="{w}" height="22" rx="4" fill="#fff" stroke="{color}" stroke-width="1.5"/>')
    add(f'<text x="{x0+7}" y="{y+4}" class="tag" fill="{color}">{s}</text>')

def unv(x, y, anchor="start"):
    add(f'<text x="{x}" y="{y}" class="unv" text-anchor="{anchor}">[UNVERIFIED]</text>')

add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
add("""<style>
text{font-family:'Microsoft JhengHei','Noto Sans TC','PingFang TC',sans-serif;fill:#222}
.title{font-size:26px;font-weight:700}.subt{font-size:15px;fill:#555}
.bt{font-size:17px;font-weight:700}.bs{font-size:13px;fill:#555}
.pn{font-size:14px}.t{font-size:14px}.na{font-size:12px;fill:#999}
.tag{font-size:13px;font-weight:700}.unv{font-size:12px;font-weight:700;fill:#c0392b}
.warn{font-size:15px;font-weight:700;fill:#b34700}.lg{font-size:14px}
</style>""")
add(f'<rect width="{W}" height="{H}" fill="#ffffff"/>')
text(40, 42, "麵包板線路還原 — 由三張照片判讀", "title")
text(40, 68, "欄號為麵包板座標（欄 1–63、列 a–j），判讀誤差約 ±1 欄；[UNVERIFIED] = 照片無法證實；交叉處無黑點 = 不相連", "subt")

# ---------- U1 nice!nano ----------
box(60, 190, 310, 780, "U1  nice!nano 相容板", "nRF52840｜欄 1–12，上排 h 列／下排 d 列")
u1 = {}
for key, y, name in [("RAW", 240, "RAW / B+〔上排·欄1〕"), ("VCC", 300, "VCC 3.3V〔上排·欄4〕"),
                     ("P006", 360, "P0.06 (TX)〔下排·欄1〕"), ("GND1", 430, "GND〔上排·欄2〕"),
                     ("GND2", 470, "GND〔下排·欄3〕"), ("P106", 540, "P1.06?〔下排·欄12±1〕"),
                     ("P008", 620, "P0.08 (RX)〔下排·欄2〕"), ("SWD", 720, "SWD 焊盤（板底）")]:
    u1[key] = (pin_r(310, y, name), y)
openpin(*u1["VCC"])
unv(320, 712)

# ---------- U2 BlackPill ----------
box(1390, 190, 1640, 800, "U2  WeAct BlackPill", "STM32F401/F411｜欄 44–63，上排 h 列")
u2 = {}
for key, y, name in [("5V", 320, "5V〔欄46〕"), ("3V3", 370, "3V3〔欄44〕"), ("G", 420, "G〔欄45〕"),
                     ("PA9", 620, "PA9 USART1_TX〔欄58〕"), ("PA10", 670, "PA10 USART1_RX〔欄57〕"),
                     ("SWD", 740, "SWD 排孔 3V3/DIO/SCK/GND")]:
    u2[key] = (pin_l(1390, y, name), y)
openpin(*u2["3V3"], anchor="end"); openpin(*u2["G"], anchor="end"); openpin(*u2["PA10"], anchor="end")
text(1400, 775, "板上紫色飛線：NRST ↔ USB-C 旁", "na"); unv(1400, 792)

# ---------- BT1 ----------
box(620, 125, 820, 175, "BT1  LiPo 電池", "熱縮套 2pin 排針插在 g 列（不在電源軌）")
text(660, 157, "＋ 欄22", "pn"); text(735, 157, "− 欄23", "pn")
path([u1["RAW"], (680, 240), (680, 175)], "power")
tag(400, 222, "RAW（欄1 → 紅線 → 欄22）", "#c81e1e")
path([u1["P006"], (770, 360), (770, 175)], "warn")
tag(400, 342, "P0.06（欄1 → 黃線 → 欄23）", "#b34700")
# X1 unknown object (no connections drawn)
add('<rect x="690" y="190" width="62" height="34" rx="4" fill="#fff" stroke="#888" stroke-width="2" stroke-dasharray="5 4"/>')
text(721, 212, "X1 ?", "pn", "middle")
text(830, 145, "X1：欄22–23 j 列的白色半透明物體（LED？熱熔膠？）", "t"); unv(830, 163)
add('<rect x="830" y="180" width="470" height="62" rx="6" fill="#fff4e8" stroke="#e66e00" stroke-width="2"/>')
text(845, 205, "⚠ 電池負極接到 P0.06（欄23），不是 GND", "warn")
text(845, 228, "回流會經過 P0.06 腳位的保護二極體 → 可能燒腳／燒晶片", "t")

# ---------- GND_A ----------
path([u1["GND1"], (380, 430), (380, 520)], "gnd")
path([u1["GND2"], (380, 470)], "gnd"); dot(380, 470)
path([(380, 520), (1170, 520)], "gnd")
tag(400, 502, "GND_A（nice!nano GND）", "#111")

# P1.06 (uncertain) to GND_A
path([u1["P106"], (860, 540), (860, 520)], "unv"); dot(860, 520, "#888")
text(400, 562, "紅線：欄12 → 欄27（與 GND 同欄；若成立 = P1.06 接地，輸出高電位會短路）", "na")
unv(400, 578)

# ---------- U3 ----------
box(960, 300, 1100, 440, "U3  3.3V LDO（推斷）", "SOT-23-5｜AP2112K-3.3 同腳位系列")
u3 = {}
for key, y, name in [("27u", 320, "EN?"), ("27d", 370, "NC"), ("28d", 420, "（空）")]:
    u3[key] = (pin_l(960, y, name), y)
for key, y, name in [("29u", 320, "VIN"), ("28u", 370, "GND"), ("29d", 420, "VOUT")]:
    u3[key] = (pin_r(1100, y, name), y)
openpin(*u3["27u"], anchor="end"); openpin(*u3["28d"], anchor="end")
text(1030, 458, "VIN 欄29上｜GND 欄28上｜VOUT 欄29下", "na", "middle")
text(1030, 475, "EN 欄27上｜NC 欄27下（依接法推斷）", "na", "middle")
path([u3["27d"], (900, 370), (900, 520)], "gnd"); dot(900, 520)
text(890, 470, "綠線（欄2 GND）", "na", "end")
# 5V
path([u3["29u"], u2["5V"]], "power")
tag(1150, 302, "+5V（黃線 欄29 ↔ 欄46）", "#c81e1e")
# R1 between 29下 and GND_A
path([u3["29d"], (1170, 420), (1170, 445)], "misc")
add('<path d="M1170,445 l10,5 l-20,8 l20,8 l-20,8 l20,8 l-20,8 l10,5" stroke="#444" stroke-width="2" fill="none"/>')
path([(1170, 495), (1170, 520)], "gnd")
text(1188, 470, "R1 負載  欄27–29 c 列", "t"); text(1188, 488, "阻值", "t"); unv(1222, 488)
# N36 from U3 28上
path([u3["28u"], (1150, 370)], "gnd?")
tag(1155, 370, "N36", "#111")

# ---------- UART ----------
path([u1["P008"], u2["PA9"]], "sig")
tag(400, 602, "UART：P0.08 ← 橘 → 欄19 → 黃 → 欄41 → 綠（板下）→ PA9", "#1e64d2")
dot(1200, 620, "#1e64d2")

# ---------- J2 / J3 (BlackPill side) ----------
box(1240, 680, 1300, 900, "J2", "")
text(1270, 918, "6pin 黑排針 j 列", "bs", "middle")
j2 = {}
for i, y in zip([6, 5, 4, 3, 2, 1], [700, 740, 780, 820, 860, 880 + 0]):
    pass
j2y = {6: 700, 5: 740, 4: 780, 3: 820, 2: 850, 1: 880}
for n, y in j2y.items():
    j2[n] = (pin_l(1240, y, f"{n}", 30), y)
text(1310, 705, "欄41", "na"); text(1310, 745, "欄40", "na"); text(1310, 785, "欄39", "na")
text(1310, 825, "欄38", "na"); text(1310, 855, "欄37", "na"); text(1310, 885, "欄36", "na")
path([j2[6], (1200, 700), (1200, 620)], "sig")
path([j2[5], (1180, 740)], "gnd"); tag(1176, 740, "GND_A", "#111", "end")
text(1176, 722, "欄20 → 紅線 → 欄40", "na", "end")
box(1080, 770, 1140, 900, "", "")
text(1030, 800, "J3  4pin 黃排針 d 列", "bt", "end")
text(1030, 822, "跨溝短跳線：欄36 綠、欄38/39 紅", "na", "end")
text(1030, 840, "欄37 兩半邊未接通", "na", "end")
j3y = {4: 780, 3: 820, 2: 850, 1: 880}
j3 = {n: (pin_r(1140, y, f"{n}", 30), y) for n, y in j3y.items()}
path([j3[4], j2[4]], "swd"); path([j3[3], j2[3]], "swd"); path([j3[1], j2[1]], "gnd?")
openpin(1172, 850, "", "start"); openpin(1208, 850, "", "end")
# purple bundle J3 -> BlackPill SWD
path([(1080, 860), (1045, 860), (1045, 1000), (1360, 1000), u2["SWD"]], "bundle")
text(1205, 1022, "紫線 ×4 → BlackPill 板底 SWD 排孔", "t"); unv(1205, 1039)
text(1205, 1056, "（判斷：1=GND、3/4=SWDIO/SWCLK、2=3V3，順序未證實）", "na")

# ---------- J4 / J1 (nice!nano side) ----------
box(430, 840, 490, 990, "J4", "4pin 黃 c 列")
j4y = {4: 860, 3: 900, 2: 940, 1: 980}
j4 = {n: (pin_r(490, y, f"{n}", 30), y) for n, y in j4y.items()}
box(600, 840, 660, 990, "J1", "4pin 黑 j 列")
j1 = {n: (pin_l(600, y, f"{n}", 30), y) for n, y in j4y.items()}
path([j4[1], j1[1]], "gnd?"); path([j4[3], j1[3]], "swd"); path([j4[4], j1[4]], "swd")
openpin(522, 940, "", "start"); openpin(568, 940, "", "end")
for n, y in j4y.items():
    text(670, y + 5, f"欄{14+n}", "na")
text(560, 1045, "跨溝短跳線：欄15 黃、欄17/18 紅；欄16 兩半邊未接通", "na")
# bundle J4 -> nice!nano SWD pads
path([(430, 920), (360, 920), (360, 720), u1["SWD"]], "bundle")
text(175, 945, "紫線 ×4 → nice!nano 板底", "t"); unv(175, 962)

# ---------- N36: S6 red wire col15 <-> col36 (shared pin-1 net) ----------
path([(545, 980), (545, 1090), (1190, 1090), (1190, 880)], "gnd?")
dot(545, 980); dot(1190, 880)
add('<rect x="1182" y="993" width="16" height="14" fill="#fff"/>')
add('<path d="M1190,1007 a7,7 0 0,1 0,-14" stroke="#111" stroke-width="2.5" fill="none"/>')
tag(620, 1090, "N36（紅線 S6：欄15 ↔ 欄36）推論為 GND", "#111")
path([(1190, 1090), (1190, 1130)], "gnd?")
text(1200, 1130, "下方 − 軌（只接了欄36）", "t")
text(1150, 395, "（紫跳線 欄28 ↔ 欄36）", "na")

# ---------- legend ----------
lx, ly = 60, 1080
add(f'<rect x="{lx-15}" y="{ly-30}" width="440" height="125" rx="6" fill="#fafafa" stroke="#ccc"/>')
text(lx, ly - 8, "圖例", "bt")
items = [("power", "電源（RAW / 5V）"), ("gnd", "GND"), ("gnd?", "推論為 GND（N36）"), ("sig", "UART 訊號"),
         ("swd", "SWD 跳線"), ("bundle", "紫線束（端點在板底）"), ("warn", "⚠ 問題連線"), ("unv", "[UNVERIFIED] 連線")]
for i, (st, lab) in enumerate(items):
    x = lx + (i % 2) * 215
    y = ly + 15 + (i // 2) * 22
    path([(x, y), (x + 45, y)], st)
    text(x + 55, y + 5, lab, "lg")

add("</svg>")
open(OUT, "w", encoding="utf-8").write("\n".join(S))
print("wrote", OUT)
