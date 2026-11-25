"""Build the hand-off package (teacher + PCB vendor) and zip it.
usage: python make_package.py   (after gen_breakout / gen_scene / gen_drawings / gen_viewer)"""
import os, shutil, subprocess, sys, zipfile, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
KCLI = os.environ.get("KICAD_CLI", "kicad-cli")   # set KICAD_CLI to your kicad-cli path (KiCad 9+)
NAME = "card609_breakout"
VER = "v1"
TAG = f"ICA609_breadboard_breakout_{VER}"
OUT = os.path.join(HERE, "交付", TAG)
PCB = os.path.join(HERE, NAME + ".kicad_pcb")
SCH = os.path.join(HERE, NAME + ".kicad_sch")

if os.path.isdir(OUT):
    shutil.rmtree(OUT)
D = {k: os.path.join(OUT, v) for k, v in {
    "gbr": "01_Gerber_給廠商", "bom": "02_BOM", "doc": "03_圖面", "3d": "04_3D", "src": "05_KiCad原始檔", "chk": "06_檢查報告"}.items()}
for d in D.values():
    os.makedirs(d)


def run(*a):
    r = subprocess.run([KCLI, *a], capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode:
        sys.exit(f"kicad-cli failed: {a}\n{r.stdout}\n{r.stderr}")
    return r.stdout


# ---- 01 Gerber + drill (single-sided: copper on top only) ----
gdir = os.path.join(D["gbr"], "gerber")
os.makedirs(gdir)
run("pcb", "export", "gerbers", "--layers", "F.Cu,F.Mask,F.SilkS,B.Mask,Edge.Cuts", "--subtract-soldermask", "-o", gdir + os.sep, PCB)
run("pcb", "export", "drill", "--format", "excellon", "--excellon-units", "mm", "--generate-map", "--map-format", "pdf",
    "-o", gdir + os.sep, PCB)
for f in os.listdir(gdir):
    if f.endswith(".gbrjob"):
        os.remove(os.path.join(gdir, f))
gzip = os.path.join(D["gbr"], f"{TAG}_gerber.zip")
with zipfile.ZipFile(gzip, "w", zipfile.ZIP_DEFLATED) as z:
    for f in sorted(os.listdir(gdir)):
        if not f.endswith((".pdf", ".gbrjob")):    # job file says 2 copper layers (KiCad minimum) -> leave it out, board is 1-layer
            z.write(os.path.join(gdir, f), f)

# ---- 02 BOM ----
open(os.path.join(D["bom"], "BOM.csv"), "w", encoding="utf-8-sig").write(
    "位號,數量,品名,規格,裝配面,備註\n"
    "J1,1,IC 卡座,Hamburg ICA-609 Type2 NO（8 觸點 + 常開偵測開關，插件腳 Ø1.0）,背面（無銅面）,腳從背面穿上來、在正面（銅面）焊\n"
    "J2,1,排針,1×5 直排公針 2.54 mm（標準 11.5 mm：下 6 / 塑膠 2.5 / 上 3）,塑膠座在背面,長腳朝下插麵包板 d1–d5，短腳在正面焊\n"
    "J3,1,排針,1×5 直排公針 2.54 mm（同 J2）,塑膠座在背面,長腳朝下插麵包板 g1–g5，短腳在正面焊\n")

# ---- 03 drawings ----
run("sch", "export", "pdf", "-o", os.path.join(D["doc"], "線路圖.pdf"), SCH)
run("pcb", "export", "pdf", "--layers", "F.Cu,F.SilkS,Edge.Cuts", "--mode-single", "-o", os.path.join(D["doc"], "PCB_正面銅箔與絲印.pdf"), PCB)
run("pcb", "export", "pdf", "--layers", "B.Fab,Edge.Cuts", "--mode-single", "--mirror", "-o", os.path.join(D["doc"], "PCB_背面裝配_卡座外框.pdf"), PCB)
for f in ("尺寸圖.png", "配置圖_麵包板.png", "預覽_PCB.png"):
    shutil.copy(os.path.join(HERE, f), D["doc"])
shutil.copy(os.path.join(D["gbr"], "gerber", [f for f in os.listdir(gdir) if f.endswith(".pdf")][0]), os.path.join(D["doc"], "鑽孔圖.pdf"))

# ---- 04 3D ----
for f in os.listdir(HERE):
    if f.startswith("立體") and (f.endswith(".png") or f.endswith(".html")):
        shutil.copy(os.path.join(HERE, f), D["3d"])

# ---- 05 KiCad sources (+ generator scripts) ----
for f in (NAME + ".kicad_pro", NAME + ".kicad_sch", NAME + ".kicad_pcb"):
    shutil.copy(os.path.join(HERE, f), D["src"])
os.makedirs(os.path.join(D["src"], "3d"))
for f in ("ICA-609_socket.wrl", "header_1x05.wrl"):
    shutil.copy(os.path.join(HERE, "3d", f), os.path.join(D["src"], "3d"))
os.makedirs(os.path.join(D["src"], "產生腳本"))
for f in ("gen_breakout.py", "models3d.py", "gen_scene.py", "gen_drawings.py", "gen_viewer.py", "check_dims.py", "make_package.py"):
    shutil.copy(os.path.join(HERE, f), os.path.join(D["src"], "產生腳本"))

# ---- 06 checks ----
run("pcb", "drc", "--schematic-parity", "-o", os.path.join(D["chk"], "DRC.rpt"), PCB)
run("sch", "erc", "-o", os.path.join(D["chk"], "ERC.rpt"), SCH)
r = subprocess.run([sys.executable, "-I", os.path.join(HERE, "check_dims.py"), PCB], capture_output=True, text=True, encoding="utf-8")
open(os.path.join(D["chk"], "尺寸檢查.txt"), "w", encoding="utf-8").write(r.stdout)
if "ALL SPEC CHECKS PASS" not in r.stdout:
    sys.exit("dimension check failed")

# ---- README ----
shutil.copy(os.path.join(HERE, "README_交付.md"), os.path.join(OUT, "README.md"))

# ---- zip ----
stamp = datetime.date.today().strftime("%Y%m%d")
zpath = os.path.join(HERE, "交付", f"{TAG}_{stamp}.zip")
with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
    for root, _, files in os.walk(OUT):
        for f in files:
            p = os.path.join(root, f)
            z.write(p, os.path.join(TAG, os.path.relpath(p, OUT)))
print(zpath)
for root, _, files in os.walk(OUT):
    for f in sorted(files):
        print("  ", os.path.relpath(os.path.join(root, f), OUT))
