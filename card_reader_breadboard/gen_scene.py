"""Render-only scene: the real board + an inserted card + a 400-point breadboard, then 3D PNGs via kicad-cli.
usage: python gen_scene.py   (run after gen_breakout.py, in this folder)"""
import os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import models3d

KCLI = os.environ.get("KICAD_CLI", "kicad-cli")   # set KICAD_CLI to your kicad-cli path (KiCad 9+)
src = open(os.path.join(HERE, "card609_breakout.kicad_pcb"), encoding="utf-8").read()

models3d.card(os.path.join(HERE, "3d", "card.wrl"), 2.0, 56.0, 15.24 - 11.0, 15.24 - 11.0 + 85.6)
models3d.breadboard(os.path.join(HERE, "3d", "breadboard_400.wrl"))

sock = '(model "${KIPRJMOD}/3d/ICA-609_socket.wrl"'
hdr = '(model "${KIPRJMOD}/3d/header_1x05.wrl"'
assert src.count(sock) == 1 and src.count(hdr) == 2
src = src.replace(sock, '(model "${KIPRJMOD}/3d/card.wrl" (offset (xyz 0 0 0)) (scale (xyz 1 1 1)) (rotate (xyz 0 0 180)))\n  ' + sock, 1)
src = src.replace(hdr, '(model "${KIPRJMOD}/3d/breadboard_400.wrl" (offset (xyz 0 0 0)) (scale (xyz 1 1 1)) (rotate (xyz 0 0 0)))\n  ' + hdr, 1)
scene = os.path.join(HERE, "_scene_render_only.kicad_pcb")
open(scene, "w", encoding="utf-8").write(src)

views = {
    "立體_斜視.png": ["--rotate", "-55,0,20", "--zoom", "0.5", "--perspective"],
    "立體_正面.png": ["--side", "top", "--zoom", "0.55"],
    "立體_側視.png": ["--side", "front", "--zoom", "0.8"],
    "立體_低角度.png": ["--rotate", "-80,0,-25", "--zoom", "0.6", "--perspective"],
}
board_only = {"立體_PCB單板.png": ["--rotate", "-45,0,30", "--zoom", "1.0", "--perspective"]}
for name, args in views.items():
    subprocess.run([KCLI, "pcb", "render", "-o", os.path.join(HERE, name), "-w", "1800", "-h", "1200",
                    "--quality", "high", "--background", "opaque", *args, scene], check=True)
for name, args in board_only.items():
    subprocess.run([KCLI, "pcb", "render", "-o", os.path.join(HERE, name), "-w", "1800", "-h", "1200",
                    "--quality", "high", "--background", "opaque", *args,
                    os.path.join(HERE, "card609_breakout.kicad_pcb")], check=True)
