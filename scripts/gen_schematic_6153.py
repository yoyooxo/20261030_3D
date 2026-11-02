"""KiCad schematic of the product circuit, symbols placed like the 61 x 53 perfboard layout (front view).
Placement unit = one perfboard hole (c, r) -> 5.08 mm; r grows upward like the layout."""
import sys, uuid

OUT = sys.argv[1]
H = 7.62
X0, Y0 = 53.34, 160.02
SX = lambda c: X0 + c * H
SY = lambda r: Y0 - r * H
U = lambda: str(uuid.uuid4())
ROOT = U()
f = lambda v: f"{round(v, 4):g}"
FT = "(effects (font (size 1.27 1.27)))"
HID = "(effects (font (size 1.27 1.27)) (hide yes))"

class Sym:
    def __init__(s, name, origin, body, pins, extra=(), ref="U", pin_names=True):
        s.name, (s.oc, s.orr), s.body, s.pins, s.extra, s.ref, s.pn = name, origin, body, pins, extra, ref, pin_names
    def lx(s, c): return (c - s.oc) * H
    def ly(s, r): return (r - s.orr) * H
    def lib(s):
        (c0, c1, r0, r1) = s.body
        o = [f'(symbol "ic:{s.name}" (pin_names (offset 0.508){"" if s.pn else " (hide yes)"}) (exclude_from_sim no) (in_bom yes) (on_board yes)',
             f'(property "Reference" "{s.ref}" (at 0 0 0) {HID})', f'(property "Value" "{s.name}" (at 0 0 0) {HID})',
             f'(property "Footprint" "" (at 0 0 0) {HID})', f'(property "Datasheet" "" (at 0 0 0) {HID})',
             f'(symbol "{s.name}_0_1" (rectangle (start {f(s.lx(c0))} {f(s.ly(r1))}) (end {f(s.lx(c1))} {f(s.ly(r0))}) '
             f'(stroke (width 0.254) (type default) (color 0 0 132 1)) (fill (type none)))'] + list(s.extra) + [")", f'(symbol "{s.name}_1_1"']
        for num, nm, c, r, ang, ln in s.pins:
            o.append(f'(pin passive line (at {f(s.lx(c))} {f(s.ly(r))} {ang}) (length {f(ln * H)}) (name "{nm}" {FT}) (number "{num}" {FT}))')
        o.append("))")
        return "\n".join(o)
    def at(s, num):
        for n, _, c, r, *_ in s.pins:
            if n == num:
                return (c, r)
        raise KeyError(num)

# ---- U2 BlackPill: block row 9 (bottom edge) and row 15 (top edge), USB-C on the left ----
H_ROW = ["3V3", "G", "5V", "B9", "B8", "B7", "B6", "B5", "B4", "B3", "A15", "A12", "A11", "A10", "A9", "A8", "B15", "B14", "B13", "B12"]
L_ROW = ["VB", "C13", "C14", "C15", "R", "A0", "A1", "A2", "A3", "A4", "A5", "A6", "A7", "B0", "B1", "B2", "B10", "3V3", "G", "5V"]
pre = lambda n: ("P" + n) if n[0] in "ABC" and n[1:].isdigit() else n
bp_pins = [(f"H{21-c}", pre(H_ROW[20 - c]), c, 10, 90, 0.5) for c in range(1, 21)] + \
          [(f"L{21-c}", pre(L_ROW[20 - c]), c, 16, 270, 0.5) for c in range(1, 21)]
usb = lambda c0, c1, r0, r1, sym: (f'(rectangle (start {f(sym.lx(c0))} {f(sym.ly(r1))}) (end {f(sym.lx(c1))} {f(sym.ly(r0))}) '
                                   f'(stroke (width 0.2) (type default)) (fill (type outline)))')
U2 = Sym("WeAct_BlackPill", (10.5, 13), (0.5, 20.5, 10.5, 15.5), bp_pins)
U2.extra = [f'(rectangle (start {f(U2.lx(-0.3))} {f(U2.ly(14.0))}) (end {f(U2.lx(0.5))} {f(U2.ly(12.0))}) (stroke (width 0.2) (type default) (color 0 0 132 1)) (fill (type none)))',
            f'(text "USB-C" (at {f(U2.lx(0.1))} {f(U2.ly(13.0))} 0) (effects (font (size 0.9 0.9) (color 0 0 132 1))))']

# ---- U1 nice!nano: bottom row = pins 1..12, top row = pins 24..13 ----
N_BOT = ["P0.06", "P0.08", "GND", "GND", "P0.17", "P0.20", "P0.22", "P0.24", "P1.00", "P0.11", "P1.04", "P1.06"]
N_TOP = ["RAW", "GND", "RST", "VCC", "P0.31", "P0.29", "P0.02", "P1.15", "P1.13", "P1.11", "P0.10", "P0.09"]
nano_pins = [(str(c), N_BOT[c - 1], c, 0, 90, 0.5) for c in range(1, 13)] + \
            [(str(25 - c), N_TOP[c - 1], c, 6, 270, 0.5) for c in range(1, 13)]
U1 = Sym("nice!nano_v2", (6.5, 3), (0.5, 12.5, 0.5, 5.5), nano_pins)
U1.extra = [f'(rectangle (start {f(U1.lx(-0.7))} {f(U1.ly(4.0))}) (end {f(U1.lx(0.5))} {f(U1.ly(2.0))}) (stroke (width 0.2) (type default) (color 0 0 132 1)) (fill (type none)))',
            f'(text "USB-C" (at {f(U1.lx(-0.1))} {f(U1.ly(3.0))} 0) (effects (font (size 0.9 0.9) (color 0 0 132 1))))']

# ---- U3 DMC2038LVT (TSOT26): top G1 S2 G2 = 1 2 3, bottom D1 S1 D2 = 6 5 4 ----
U3 = Sym("DMC2038LVT", (18, 4.5), (16.5, 19.5, 3.5, 5.5),
         [("3", "G2", 17, 6, 270, 0.5), ("2", "S2", 18, 6, 270, 0.5), ("1", "G1", 19, 6, 270, 0.5),
          ("4", "D2", 17, 3, 90, 0.5), ("5", "S1", 18, 3, 90, 0.5), ("6", "D1", 19, 3, 90, 0.5)])

# ---- R1 ----
R1 = Sym("R", (18.5, 1), (17.9, 19.1, 0.8, 1.2), [("1", "~", 17, 1, 0, 0.9), ("2", "~", 20, 1, 180, 0.9)], ref="R", pin_names=False)

# ---- BT1 LiPo: - on the left, + on the right ----
BT = Sym("Battery_Cell", (14.5, 18.5), (14.5, 14.5, 18.5, 18.5), [("1", "+", 12.5, 18.5, 0, 1.0), ("2", "-", 16.5, 18.5, 180, 1.0)], ref="BT", pin_names=False)
BT.extra = ['(polyline (pts (xy -1.27 3.81) (xy -1.27 -3.81)) (stroke (width 0.3) (type default) (color 0 0 132 1)) (fill (type none)))',
            '(polyline (pts (xy 1.27 1.905) (xy 1.27 -1.905)) (stroke (width 1.0) (type default) (color 0 0 132 1)) (fill (type none)))',
            '(polyline (pts (xy -7.62 0) (xy -1.27 0)) (stroke (width 0) (type default)) (fill (type none)))',
            '(polyline (pts (xy 1.27 0) (xy 7.62 0)) (stroke (width 0) (type default)) (fill (type none)))',
            '(text "+" (at -3.2 2.6 0) (effects (font (size 2 2) (bold yes) (color 0 0 132 1)))) ', '(text "−" (at 3.2 2.6 0) (effects (font (size 2 2) (bold yes) (color 0 0 132 1))))']
BT.body = None
def bt_lib(s=BT):
    o = [f'(symbol "ic:{s.name}" (pin_names (offset 0) (hide yes)) (exclude_from_sim no) (in_bom yes) (on_board yes)',
         f'(property "Reference" "BT" (at 0 0 0) {HID})', f'(property "Value" "{s.name}" (at 0 0 0) {HID})',
         f'(property "Footprint" "" (at 0 0 0) {HID})', f'(property "Datasheet" "" (at 0 0 0) {HID})',
         f'(symbol "{s.name}_0_1"'] + s.extra + [")", f'(symbol "{s.name}_1_1"']
    for num, nm, c, r, ang, ln in s.pins:
        o.append(f'(pin passive line (at {f(s.lx(c))} {f(s.ly(r))} {ang}) (length {f(ln * H)}) (name "{nm}" {FT}) (number "{num}" {FT}))')
    o.append("))")
    return "\n".join(o)
BT.lib = bt_lib

GND_LIB = """(symbol "power:GND" (power) (pin_names (offset 0)) (exclude_from_sim no) (in_bom yes) (on_board yes)
(property "Reference" "#PWR" (at 0 -6.35 0) (effects (font (size 1.27 1.27)) (hide yes)))
(property "Value" "GND" (at 0 -3.81 0) (effects (font (size 1.27 1.27))))
(property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
(property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
(symbol "GND_0_1" (polyline (pts (xy 0 0) (xy 0 -1.27)) (stroke (width 0) (type default) (color 132 0 132 1)) (fill (type none))) (polyline (pts (xy -2.032 -1.27) (xy 2.032 -1.27)) (stroke (width 0.254) (type default) (color 132 0 132 1)) (fill (type none))) (polyline (pts (xy -1.27 -1.905) (xy 1.27 -1.905)) (stroke (width 0.254) (type default) (color 132 0 132 1)) (fill (type none))) (polyline (pts (xy -0.508 -2.54) (xy 0.508 -2.54)) (stroke (width 0.254) (type default) (color 132 0 132 1)) (fill (type none))))
(symbol "GND_1_1" (pin power_in line (at 0 0 270) (length 0) hide (name "GND" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))))"""

place = [  # sym, ref, value, ref text pos (c, r), value text pos
    (U2, "U2", "WeAct BlackPill（STM32F401/F411）", (10.5, 13.6), (10.5, 12.6)),
    (U1, "U1", "nice!nano v2（nRF52840）", (6.5, 3.6), (6.5, 2.6)),
    (U3, "U3", "DMC2038LVT", (19.8, 5.0), (19.8, 4.3)),
    (R1, "R1", "阻值待定", (18.5, 0.6), (18.5, 0.2)),
    (BT, "BT1", "LiPo 電池 30×25×5 mm（估）— 實體用膠帶疊在 U2 右段上", (18.0, 18.85), (18.0, 18.15)),
]

items = []
def wire(pts, color=None, width=0):
    st = f"(stroke (width {width}) (type default))" if not color else f"(stroke (width {width}) (type default) (color {color} 1))"
    for (c1, r1), (c2, r2) in zip(pts, pts[1:]):
        items.append(f'(wire (pts (xy {f(SX(c1))} {f(SY(r1))}) (xy {f(SX(c2))} {f(SY(r2))})) {st} (uuid "{U()}"))')
def junction(c, r):
    items.append(f'(junction (at {f(SX(c))} {f(SY(r))}) (diameter 0) (color 132 0 132 1) (uuid "{U()}"))')
def label(name, c, r, ang=0):
    items.append(f'(label "{name}" (at {f(SX(c))} {f(SY(r))} {ang}) (fields_autoplaced yes) (effects (font (size 1.27 1.27) (bold yes) (color 200 100 0 1)) (justify left bottom)) (uuid "{U()}"))')
def text(s, c, r, size=1.27, bold=False, color=None):
    b = " (bold yes)" if bold else ""
    col = f" (color {color} 1)" if color else ""
    items.append(f'(text "{s}" (exclude_from_sim no) (at {f(SX(c))} {f(SY(r))} 0) (effects (font (size {size} {size}){b}{col}) (justify left)) (uuid "{U()}"))')
gnds = []
def gnd(c, r): gnds.append((c, r))

RED = BLK = YEL = ORG = "132 0 132"
# W1 battery + -> RAW ; W2 battery - -> nano GND ; W4 common ground to BlackPill G (top row)
wire([(12.5, 18.5), (-3, 18.5), (-3, 7), (1, 7), (1, 6)], RED, 0)
label("VBAT", 6, 18.5)
wire([(16.5, 18.5), (16.5, 19), (-4, 19), (-4, 6.5), (2, 6.5), (2, 6)], BLK, 0)
wire([(-4, 6.5), (-4, 6)], BLK, 0); gnd(-4, 6); junction(-4, 6.5)
wire([(-1.5, 6.5), (-1.5, 17), (2, 17), (2, 16)], BLK, 0); junction(-1.5, 6.5)
# W3 UART PA9 -> P0.08
wire([(6, 10), (6, 9.5), (14, 9.5), (14, -1), (2, -1), (2, 0)], YEL, 0); label("UART_TX", 8, 9.5)
# W5 5V -> G2 ; W6 G -> S2
wire([(18, 10), (18, 7.5), (17, 7.5), (17, 6)], RED, 0); label("+5V", 18, 8.5, 90)
wire([(19, 10), (19, 7), (18, 7), (18, 6)], BLK, 0)
wire([(19, 8.5), (20, 8.5), (20, 8)], BLK, 0); gnd(20, 8); junction(19, 8.5)
# W7 S1 -> GND (S2 is GND through W6)
wire([(18, 3), (18, 2.5)], BLK, 0); gnd(18, 2.5)
# W8 G1 <-> D2 ; W9 D2 -> R1.2 ; W10 D1 -> R1.1 ; W11 R1.1 -> P1.06
wire([(19, 6), (19, 6.5), (21, 6.5), (21, 1.5), (17, 1.5)], RED, 0); junction(17, 1.5)
wire([(17, 3), (17, 1)], RED, 0)
wire([(19, 3), (19, 2), (20, 2), (20, 1)], ORG, 0)
wire([(20, 1), (20, -0.5), (12, -0.5), (12, 0)], ORG, 0); junction(20, 1)

# wire numbers (same as the perfboard layout)
for s, c, r in [("W1 電池＋", -2.8, 7.25), ("W2 電池−", -3.8, 6.25), ("W4 共地", -1.3, 16.0), ("W3", 10.5, 9.75), ("W5", 16.3, 7.75),
                ("W6", 19.2, 7.25), ("W7", 18.25, 2.1), ("W8", 21.2, 2.6), ("W9", 16.3, 2.25),
                ("W10", 20.2, 2.25), ("W11", 14.3, -0.75)]:
    text(s, c, r, 1.0, False, "110 110 110")

# notes
nx = 22.2
items.append(f'(rectangle (start {f(SX(nx - 0.3))} {f(SY(15.6))}) (end {f(SX(nx + 8.0))} {f(SY(3.9))}) (stroke (width 0.2) (type default) (color 0 0 0 1)) (fill (type none)) (uuid "{U()}"))')
text("注意事項", nx, 15.15, 1.5, True, "0 0 132")
for i, s in enumerate(["U3 DMC2038LVT（TSOT26）互補 MOSFET：", "  Q1 N 通道 G1(1)/S1(5)/D1(6)", "  Q2 P 通道 G2(3)/S2(2)/D2(4)",
                       "", "網路：", "  GND：電池−、U1 GND、U2 G×2、U3 S1/S2", "  +5V：U2 5V → U3 G2",
                       "  UART_TX：U2 PA9 → U1 P0.08", "  U3 G1 ＝ D2 ＝ R1.1", "  U3 D1 ＝ R1.2 ＝ U1 P1.06",
                       "  W7：U3 S1 接 GND（Layout 上直接焊到 S2）",
                       "  VBAT：電池＋ → U1 RAW",
                       "電池疊在 U2 右段（實體），線從左緣繞進來",
                       "", "U1 與 U2 之間對應 Layout 中間空 4 排", "電池尺寸為照片估計；R1 阻值待定",
                       "兩個 USB-C 都在左邊、凸出板邊；X ＝ 不接"]):
    text(s, nx, 14.5 - i * 0.62, 1.27, False, "0 0 132")

USED = {"U2": {"H15", "H3", "H2", "L19"}, "U1": {"2", "23", "24", "12"}}
for sym, ref in ((U2, "U2"), (U1, "U1")):
    for num, nm, c, r, *_ in sym.pins:
        if num not in USED[ref]:
            items.append(f'(no_connect (at {f(SX(c))} {f(SY(r))}) (uuid "{U()}"))')

out = ['(kicad_sch (version 20231120) (generator "eeschema") (generator_version "8.0")',
       f'(uuid "{ROOT}") (paper "A4")',
       '(title_block (title "IC卡產品 BlackPill + nice!nano + DMC2038LVT") (date "2026-11-02") (rev "V1") (comment 1 "零件依 61x53 mm 洞洞板 Layout 排列，線號 W1–W11 與 Layout 相同") (comment 2 "電池尺寸為估計；R1 阻值待定"))',
       "(lib_symbols"] + [s.lib() for s in (U2, U1, U3, R1, BT)] + [GND_LIB, ")"]
for sym, ref, val, (rc, rr), (vc, vr) in place:
    X, Y = SX(sym.oc), SY(sym.orr)
    out.append(f'(symbol (lib_id "ic:{sym.name}") (at {f(X)} {f(Y)} 0) (unit 1) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no) (uuid "{U()}")')
    j = " (justify left)" if ref in ("U3", "BT1") else ""
    out.append(f'(property "Reference" "{ref}" (at {f(SX(rc))} {f(SY(rr))} 0) (effects (font (size 1.524 1.524) (bold yes) (color 0 0 132 1)){j}))')
    out.append(f'(property "Value" "{val}" (at {f(SX(vc))} {f(SY(vr))} 0) (effects (font (size 1.27 1.27) (color 0 0 132 1)){j}))')
    out.append(f'(property "Footprint" "" (at {f(X)} {f(Y)} 0) {HID})')
    out.append(f'(property "Datasheet" "" (at {f(X)} {f(Y)} 0) {HID})')
    for p in sym.pins:
        out.append(f'(pin "{p[0]}" (uuid "{U()}"))')
    out.append(f'(instances (project "product_6153" (path "/{ROOT}" (reference "{ref}") (unit 1)))))')
for i, (c, r) in enumerate(gnds, 1):
    X, Y = SX(c), SY(r)
    out.append(f'(symbol (lib_id "power:GND") (at {f(X)} {f(Y)} 0) (unit 1) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no) (uuid "{U()}")')
    out.append(f'(property "Reference" "#PWR0{i}" (at {f(X)} {f(Y + 6.35)} 0) {HID})')
    out.append(f'(property "Value" "GND" (at {f(X)} {f(Y + 4.0)} 0) (effects (font (size 1.0 1.0) (bold yes) (color 200 100 0 1))))')
    out.append(f'(property "Footprint" "" (at {f(X)} {f(Y)} 0) {HID})')
    out.append(f'(property "Datasheet" "" (at {f(X)} {f(Y)} 0) {HID})')
    out.append(f'(pin "1" (uuid "{U()}"))')
    out.append(f'(instances (project "product_6153" (path "/{ROOT}" (reference "#PWR0{i}") (unit 1)))))')
out += items
out.append('(sheet_instances (path "/" (page "1")))')
out.append(")")
open(OUT, "w", encoding="utf-8").write("\n".join(out))
print("ok")
