"""Compact (A4, 2.54 mm pitch) routed schematic of the photo-derived breadboard circuit.
Coordinates in grid units (1 = 2.54 mm); schematic y grows downward."""
import sys, uuid

OUT = sys.argv[1]
G = 2.54
ROOT = str(uuid.uuid4())
U = lambda: str(uuid.uuid4())
mm = lambda v: f"{round(v * G, 4):g}"
F = "(effects (font (size 1.27 1.27)))"
FS = "(effects (font (size 1.27 1.27)))"

class Sym:
    """left/right: lists of (num, name, dy); dy in grid units, down positive"""
    def __init__(self, name, left, right, w, ref, pad=1):
        self.name, self.left, self.right, self.w, self.ref = name, left, right, w, ref
        dys = [p[2] for p in left + right]
        self.top, self.bot = min(dys) - pad, max(dys) + pad

    def pins(self):
        hx = self.w / 2 + 1
        for num, nm, dy in self.left:
            yield num, nm, -hx, dy, 0
        for num, nm, dy in self.right:
            yield num, nm, hx, dy, 180

    def lib(self):
        s = [f'(symbol "restore:{self.name}" (pin_names (offset 0.508)) (exclude_from_sim no) (in_bom yes) (on_board yes)',
             f'(property "Reference" "{self.ref}" (at 0 {mm(-self.top + 2)} 0) {F})',
             f'(property "Value" "{self.name}" (at 0 {mm(-self.bot - 2)} 0) {F})',
             '(property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))',
             '(property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))',
             f'(symbol "{self.name}_0_1" (rectangle (start {mm(-self.w/2)} {mm(-self.top)}) (end {mm(self.w/2)} {mm(-self.bot)}) (stroke (width 0.254) (type default)) (fill (type background))))',
             f'(symbol "{self.name}_1_1"']
        for num, nm, x, dy, a in self.pins():
            s.append(f'(pin passive line (at {mm(x)} {mm(-dy)} {a}) (length 2.54) (name "{nm}" {FS}) (number "{num}" {FS}))')
        s.append("))")
        return "\n".join(s)

# U1 nice!nano — wired pins on the right (facing the circuit), unwired pins on the left
u1_right = [("24", "RAW [欄1上]", -6), ("21", "VCC [欄4上]", -5), ("1", "P0.06 TX [欄1下]", -4),
            ("12", "P1.06? [欄12下]", -2), ("23", "GND [欄2上]", 0), ("3", "GND [欄3下]", 1),
            ("2", "P0.08 RX [欄2下]", 8)]
u1_left = [("4", "GND"), ("5", "P0.17"), ("6", "P0.20"), ("7", "P0.22"), ("8", "P0.24"), ("9", "P1.00"),
           ("10", "P0.11"), ("11", "P1.04"), ("13", "P0.09"), ("14", "P0.10"), ("15", "P1.11"), ("16", "P1.13"),
           ("17", "P1.15"), ("18", "P0.02"), ("19", "P0.29"), ("20", "P0.31"), ("22", "RST")]
u1 = Sym("NiceNano_nRF52840", [(n, nm, -8 + i) for i, (n, nm) in enumerate(u1_left)], u1_right, 12, "U")

# U2 BlackPill — wired pins on the left
top_row = ["3V3", "G", "5V", "B9", "B8", "B7", "B6", "B5", "B4", "B3", "A15", "A12", "A11", "A10", "A9", "A8", "B15", "B14", "B13", "B12"]
bot_row = ["VB", "C13", "C14", "C15", "R", "A0", "A1", "A2", "A3", "A4", "A5", "A6", "A7", "B0", "B1", "B2", "B10", "3V3", "G", "5V"]
u2_left = [("H3", "5V [欄46]", -9), ("H1", "3V3 [欄44]", -8), ("H2", "G [欄45]", -7),
           ("H15", "PA9 USART1_TX [欄58]", 8), ("H14", "PA10 USART1_RX [欄57]", 9)]
used = {"H3", "H1", "H2", "H15", "H14"}
pre = lambda n: ("P" + n) if n[0] in "ABC" and n[1:].isdigit() else n
rest = [(f"H{i+1}", f"{pre(n)} [{44+i}h]") for i, n in enumerate(top_row) if f"H{i+1}" not in used]
rest += [(f"L{i+1}", f"{pre(n)} [{44+i}d]") for i, n in enumerate(bot_row)]
u2 = Sym("BlackPill_STM32F411", u2_left, [(n, nm, -17 + i) for i, (n, nm) in enumerate(rest)], 16, "U")
u4 = Sym("BlackPill_SWD_header", [("1", "3V3", -2), ("2", "DIO PA13", -1), ("3", "SCK PA14", 0), ("4", "GND", 1)], [], 8, "U")
u3 = Sym("U3_DMC2038LVT", [("3", "G1", -1), ("4", "D1", 0), ("6", "S1", 1)],
         [("1", "G2", -1), ("2", "S2", 0), ("5", "D2", 1)], 6, "U")
r1 = Sym("R1", [("1", "", 0)], [("2", "", 0)], 2, "R", pad=0.5)
bt = Sym("BT1_LiPo", [("+", "+", 0)], [("-", "−", 0)], 4, "BT", pad=1)
def hdr(name, n, side, start, dy0):
    pins = [(str(k), f"欄{start + k - 1}", dy0 + (n - k)) for k in range(1, n + 1)]  # pin 1 at bottom
    return Sym(name, pins if side == "L" else [], pins if side == "R" else [], 3, "J")
j4 = hdr("J4_4pin", 4, "R", 15, -2)
j1 = hdr("J1_4pin", 4, "L", 15, -2)
j3 = hdr("J3_4pin", 4, "R", 36, -1)
j2 = hdr("J2_6pin", 6, "L", 36, -3)

place = {  # ref: (sym, X, Y, value)
    "U1": (u1, 14, 30, "nice!nano 相容 nRF52840"),
    "U2": (u2, 96, 30, "WeAct BlackPill STM32F401/F411"),
    "U4": (u4, 101, 54, "BlackPill SWD 排孔"),
    "U3": (u3, 52, 22, " "),
    "R1": (r1, 60, 29, "阻值[UNVERIFIED]"),
    "BT1": (bt, 32, 12, "LiPo 欄22(+)/23(−)"),
    "J4": (j4, 15.5, 48, "黃 c列"),
    "J1": (j1, 24.5, 48, "黑 j列"),
    "J3": (j3, 75.5, 48, "黃 d列"),
    "J2": (j2, 84.5, 48, "黑 j列"),
}

def P(ref, num):
    sym, X, Y, _ = place[ref]
    for n, _, x, dy, _ in sym.pins():
        if n == num:
            return (X + x, Y + dy)
    raise KeyError((ref, num))

STY = {
    "power": "(stroke (width 0.5) (type solid) (color 200 30 30 1))",
    "gnd":   "(stroke (width 0.5) (type solid) (color 0 0 0 1))",
    "gnd?":  "(stroke (width 0.4) (type dash) (color 0 0 0 1))",
    "sig":   "(stroke (width 0.4) (type solid) (color 30 100 210 1))",
    "swd":   "(stroke (width 0.4) (type solid) (color 142 68 173 1))",
    "warn":  "(stroke (width 0.6) (type dash) (color 230 110 0 1))",
    "unv":   "(stroke (width 0.35) (type dash) (color 120 120 120 1))",
    "misc":  "(stroke (width 0.3) (type solid) (color 60 60 60 1))",
}
items = []
def wire(pts, st):
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        items.append(f'(wire (pts (xy {mm(x1)} {mm(y1)}) (xy {mm(x2)} {mm(y2)})) {STY[st]} (uuid "{U()}"))')
def junction(x, y):
    items.append(f'(junction (at {mm(x)} {mm(y)}) (diameter 0) (color 0 0 0 0) (uuid "{U()}"))')
def label(name, x, y):
    items.append(f'(label "{name}" (at {mm(x)} {mm(y)} 0) (fields_autoplaced yes) (effects (font (size 1.27 1.27)) (justify left bottom)) (uuid "{U()}"))')
def text(s, x, y, size=1.27):
    s = s.replace('"', "'").replace("\n", "\\n")
    items.append(f'(text "{s}" (exclude_from_sim no) (at {mm(x)} {mm(y)} 0) (effects (font (size {size} {size})) (justify left top)) (uuid "{U()}"))')
def poly(pts, color="142 68 173"):
    p = " ".join(f"(xy {mm(x)} {mm(y)})" for x, y in pts)
    items.append(f'(polyline (pts {p}) (stroke (width 0.5) (type dot) (color {color} 1)) (uuid "{U()}"))')

BUS, UART = 36, 38
# RAW and the battery-negative problem wire
x, y = P("U1", "24"); bx, by = P("BT1", "+"); wire([(x, y), (26, y), (26, by), (bx, by)], "power"); label("RAW", 21, y)
x, y = P("U1", "1"); bx, by = P("BT1", "-"); wire([(x, y), (38, y), (38, by), (bx, by)], "warn")
# GND_A bus
(g1x, g1y), (g2x, g2y) = P("U1", "23"), P("U1", "3")
wire([(g1x, g1y), (22, g1y), (22, g2y)], "gnd"); wire([(g2x, g2y), (22, g2y)], "gnd"); junction(22, g2y)
x3, y3 = P("U3", "6")
taps = [46]
wire([(22, g2y), (22, BUS), (taps[0], BUS)], "gnd")
for a, b in zip(taps, taps[1:] + [79]):
    wire([(a, BUS), (b, BUS)], "gnd"); junction(a, BUS)
label("GND_A", 28, BUS)
# col 27 lower half: U3 27下 + R1 (col 27 end) + red wire from U1 col 12
x, y = P("U1", "12"); n27x, n27y = P("U3", "4")
wire([(x, y), (42, y)], "unv"); wire([(42, y), (42, n27y), (n27x, n27y)], "misc"); label("N27", 43, n27y)
wire([(x3, y3), (46, y3), (46, BUS)], "gnd")
x, y = P("U3", "5"); (rx, ry), (rx2, ry2) = P("R1", "1"), P("R1", "2")
wire([(x, y), (57, y), (57, ry), (rx, ry)], "misc")
wire([(rx2, ry2), (63, ry2), (63, 32), (42, 32), (42, P("U1", "12")[1])], "misc")
# 27上 <-> 29下 link (red marking in the corrected photo)
lx, ly = P("U3", "3"); wire([(lx, ly), (47, ly), (47, 19), (57, 19), (57, y)], "misc"); junction(57, y)
jx, jy = P("J2", "5"); wire([(79, BUS), (79, jy), (jx, jy)], "gnd")
# UART with J2.6 tap
x, y = P("U1", "2"); px, py = P("U2", "H15")
wire([(x, y), (81, y)], "sig"); wire([(81, y), (px, py)], "sig"); junction(81, y)
jx, jy = P("J2", "6"); wire([(81, y), (81, jy), (jx, jy)], "sig")
label("UART", 28, y)
# +5V
x, y = P("U3", "1"); px, py = P("U2", "H3"); wire([(x, y), (px, py)], "power"); label("+5V", 64, y)
# cross-channel jumpers
for a, b in [(("J4", "4"), ("J1", "4")), (("J4", "3"), ("J1", "3")), (("J3", "4"), ("J2", "4")), (("J3", "3"), ("J2", "3"))]:
    wire([P(*a), P(*b)], "swd")
(ax, ay), (bx, by) = P("J4", "1"), P("J1", "1"); wire([(ax, ay), (20, ay)], "gnd?"); wire([(20, ay), (bx, by)], "gnd?"); junction(20, ay)
(cx, cy), (dx, dy) = P("J3", "1"), P("J2", "1"); wire([(cx, cy), (80, cy)], "gnd?"); wire([(80, cy), (dx, dy)], "gnd?"); junction(80, cy)
# N36: U3 GND (28上) -> J3/J2 pin1 ; red wire S6 from J4/J1 pin1
x, y = P("U3", "2")
wire([(x, y), (66, y), (66, 53), (80, 53)], "gnd?"); wire([(80, cy), (80, 53)], "gnd?")
wire([(20, ay), (20, 56), (80, 56), (80, 53)], "gnd?"); junction(80, 53)
label("N36（推論GND）", 40, 56)

# purple bundles: graphic only (endpoints under the boards, pin mapping unknown)
poly([(14, 48), (12, 48), (12, 39.5)])
poly([(74, 49), (72, 49), (72, 58.5), (99, 58.5), (99, 56)])

text("[!] 電池負極與 P0.06 同欄（欄23），不是 GND", 40, 10.2, 1.4)
text("X1 [UNVERIFIED]：欄22–23 白色物體，未接入", 40, 13)
text("紫點線＝紫線束（焊點在板底）[UNVERIFIED]", 6, 61)
text("下方 − 軌只接欄36", 82, 56.4)
text("U3：DMC2038LVT 互補 MOSFET（TSOT26；Q1 N 通道 G1/S1/D1、Q2 P 通道 G2/S2/D2）。\n腳↔欄位（依 1 號腳在欄27上推定）：G1=27上 S2=28上 G2=29上 / D1=27下 S1=28下 D2=29下", 40, 15.6)

out = [f'(kicad_sch (version 20231120) (generator "eeschema") (generator_version "8.0")',
       f'(uuid "{ROOT}") (paper "A4")',
       '(title_block (title "麵包板線路還原（由三張照片判讀）") (comment 1 "欄號誤差 ±1；[UNVERIFIED] = 照片無法證實"))',
       "(lib_symbols"] + [s.lib() for s in [u1, u2, u4, u3, r1, bt, j4, j1, j3, j2]] + [")"]
for ref, (sym, X, Y, val) in place.items():
    out.append(f'(symbol (lib_id "restore:{sym.name}") (at {mm(X)} {mm(Y)} 0) (unit 1) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no) (uuid "{U()}")')
    out.append(f'(property "Reference" "{ref}" (at {mm(X)} {mm(Y + sym.top - 1.9)} 0) {F})')
    out.append(f'(property "Value" "{val}" (at {mm(X)} {mm(Y + sym.top - 0.8)} 0) {FS})')
    out.append(f'(property "Footprint" "" (at {mm(X)} {mm(Y)} 0) (effects (font (size 1.27 1.27)) (hide yes)))')
    out.append(f'(property "Datasheet" "" (at {mm(X)} {mm(Y)} 0) (effects (font (size 1.27 1.27)) (hide yes)))')
    for n, *_ in sym.pins():
        out.append(f'(pin "{n}" (uuid "{U()}"))')
    out.append(f'(instances (project "breadboard_restore" (path "/{ROOT}" (reference "{ref}") (unit 1)))))')
out += items
out.append('(sheet_instances (path "/" (page "1")))')
out.append(")")
open(OUT, "w", encoding="utf-8").write("\n".join(out))
print("wrote")
