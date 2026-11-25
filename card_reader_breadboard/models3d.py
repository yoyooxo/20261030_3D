"""Simple box-based VRML models for the ICA-609 breakout (KiCad: 1 VRML unit = 2.54 mm, y up, z up from board top).
All inputs are in mm, footprint-local, PCB y-down convention."""
import os

P = 2.54
BLACK, GOLD, PLAST = (0.06, 0.06, 0.07), (0.85, 0.68, 0.25), (0.13, 0.13, 0.15)
CARD, CHIPC = (0.55, 0.75, 0.95), (0.85, 0.68, 0.25)
BB, BBHOLE, RED, BLUE = (0.93, 0.92, 0.88), (0.25, 0.25, 0.25), (0.85, 0.15, 0.15), (0.15, 0.25, 0.85)

PCB_T = 1.6
BODY_H = 6.25 - 2.80          # socket height above the PCB (datasheet 6.25 overall, 2.80 pin length below)
CARD_Z0 = 1.9                 # card underside above the PCB (springs press it up), card 0.76 thick


def write(path, boxes):
    """boxes: (x0, x1, y0, y1, z0, z1, rgb[, transparency])"""
    out = ["#VRML V2.0 utf8"]
    for b in boxes:
        x0, x1, y0, y1, z0, z1, rgb = b[:7]
        tr = b[7] if len(b) > 7 else 0.0
        X0, X1 = sorted((x0 / P, x1 / P)); Y0, Y1 = sorted((-y0 / P, -y1 / P)); Z0, Z1 = sorted((z0 / P, z1 / P))
        v = [(X0, Y0, Z0), (X1, Y0, Z0), (X1, Y1, Z0), (X0, Y1, Z0), (X0, Y0, Z1), (X1, Y0, Z1), (X1, Y1, Z1), (X0, Y1, Z1)]
        pts = ", ".join(f"{a:.4f} {b_:.4f} {c:.4f}" for a, b_, c in v)
        out.append("Shape { appearance Appearance { material Material { diffuseColor %.3f %.3f %.3f "
                   "specularColor 0.2 0.2 0.2 shininess 0.3 transparency %.2f } }" % (rgb + (tr,)))
        out.append("  geometry IndexedFaceSet { coord Coordinate { point [ %s ] }" % pts)
        out.append("    coordIndex [ 0 3 2 1 -1 4 5 6 7 -1 0 1 5 4 -1 1 2 6 5 -1 2 3 7 6 -1 3 0 4 7 -1 ] } }")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w", encoding="utf-8").write("\n".join(out))


def socket(path, cpin, frame):
    """open frame + springs + pins. origin = J1 footprint origin."""
    fx0, fy0, fx1, fy1 = frame
    H = BODY_H
    b = [(fx0, fx0 + 5, fy0, fy1, 0, H, BLACK), (fx1 - 5, fx1, fy0, fy1, 0, H, BLACK),          # side rails (card guides)
         (fx0, fx1, fy0, fy0 + 3.2, 0, 1.6, BLACK), (fx0, fx1, fy1 - 3.2, fy1, 0, 1.6, BLACK),  # top / bottom bars
         (19.5, 21.0, fy0, fy1, 0, 1.5, BLACK), (31.0, 32.5, fy0, fy1, 0, 1.5, BLACK),          # contact carrier walls
         (fx0, fx1, 17.8, 20.3, 0, 1.2, BLACK),                                                 # centre cross bar
         (fx0 + 5, fx1 - 5, fy0, fy0 + 1.0, 0, H, BLACK)]                                        # card stop at the far end
    for n, (x, y) in cpin.items():
        b.append((x - 0.3, x + 0.3, y - 0.3, y + 0.3, -2.8, 0.6, GOLD))                          # leg
        if n.startswith("C"):
            tip = 15.24 if y < 19 else 22.86
            y0, y1 = sorted((y, tip))
            b.append((x - 0.4, x + 0.4, y0, y1, 1.2, 1.9, GOLD))                                 # spring
    b.append((33.1, 34.0, 0, 6.0, 0.6, 1.8, GOLD))                                               # detect blade
    write(path, b)


HDR_PLASTIC = 2.5


def header(path, sign=-1, below=False):
    """1x05 2.54 header, origin = pin 1, pins at x = sign*2.54*k.
    below=True: standard mounting, plastic under the PCB, 6 mm legs into the breadboard, 3 mm stubs out the top."""
    x0, x1 = -sign * 1.27, sign * (4 * P + 1.27)
    if below:
        zb = -PCB_T - HDR_PLASTIC
        b = [(x0, x1, -1.25, 1.25, zb, -PCB_T, BLACK)]
        pin = (zb - 6.0, zb + 3.0 + HDR_PLASTIC + 0.0)          # 11.5 mm pin: 6 below plastic, 2.5 in plastic, 3 above
    else:
        b = [(x0, x1, -1.25, 1.25, 0, HDR_PLASTIC, BLACK)]
        pin = (-PCB_T - 4.4, HDR_PLASTIC + 3.0)
    for k in range(5):
        x = sign * P * k
        b.append((x - 0.32, x + 0.32, -0.32, 0.32, pin[0], pin[1], GOLD))
    write(path, b)


def card(path, x0, x1, y0, y1):
    z0 = CARD_Z0
    write(path, [(x0, x1, y0, y1, z0, z0 + 0.76, CARD, 0.35),
                 (20.0, 31.8, 13.0, 25.1, z0 - 0.02, z0, CHIPC)])                                 # chip contacts face down


def breadboard(path, ncol=30, edge_margin=5.0, length=83.5, width=54.5, height=8.5, top_z=-PCB_T - HDR_PLASTIC):
    """origin = hole d1 (J2 pin 1), breadboard extends to the right (+x). edge_margin = d1 hole centre -> breadboard end.
    top_z = breadboard top surface (header plastic sits on it)."""
    zt = top_z
    rows = {"a": -7.62, "b": -5.08, "c": -2.54, "d": 0, "e": 2.54, "f": 10.16, "g": 12.7, "h": 15.24, "i": 17.78, "j": 20.32}
    cy = 6.35
    xl = -edge_margin
    xr = xl + length
    b = [(xl, xr, cy - width / 2, cy + width / 2, zt - height, zt - 0.01, BB),
         (xl + 2, xr - 2, cy - 1.2, cy + 1.2, zt - 0.02, zt - 0.005, (0.8, 0.79, 0.75))]          # centre channel
    for r, y in rows.items():
        for c in range(1, ncol + 1):
            x = (c - 1) * P
            b.append((x - 0.5, x + 0.5, y - 0.5, y + 0.5, zt - 0.005, zt, BBHOLE))
    for ry, col in ((-13.97, RED), (-16.51, BLUE), (26.67, RED), (29.21, BLUE)):   # power rails
        for c in range(1, ncol):
            if c % 6 == 0:
                continue
            x = c * P
            b.append((x - 0.5, x + 0.5, ry - 0.5, ry + 0.5, zt - 0.005, zt, BBHOLE))
        yl = ry - 1.6 if (col == RED) == (ry < 0) else ry + 1.6
        b.append((xl + 3, xr - 3, yl - 0.15, yl + 0.15, zt - 0.004, zt, col))
    write(path, b)
