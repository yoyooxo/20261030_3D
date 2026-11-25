"""One short PDF for the teacher to approve the design (white background everywhere).
usage: python gen_review_pdf.py <scene_render.png> <low_angle_render.png>   (transparent-background kicad renders)"""
import os, runpy, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Rectangle

HERE = os.path.dirname(os.path.abspath(__file__))
G = runpy.run_path(os.path.join(HERE, "gen_drawings.py"))      # also refreshes 尺寸圖.png / 配置圖_麵包板.png (white)
plt.rcParams["font.family"] = ["Microsoft JhengHei", "DejaVu Sans"]
r_scene, r_low = sys.argv[1], sys.argv[2]
OUTD = os.path.join(HERE, "給老師確認")
os.makedirs(OUTD, exist_ok=True)
OUT = os.path.join(OUTD, "讀卡座轉接板_請老師確認.pdf")
A4 = (11.69, 8.27)


def page_title(fig, t, sub=None):
    fig.text(0.04, 0.95, t, fontsize=18, weight="bold", va="top")
    if sub:
        fig.text(0.04, 0.905, sub, fontsize=11, color="#444", va="top")


def img(fig, path, rect):
    ax = fig.add_axes(rect)
    ax.imshow(plt.imread(path))
    ax.axis("off")


with PdfPages(OUT) as pdf:
    # ---- page 1: overview ----
    fig = plt.figure(figsize=A4, facecolor="white")
    page_title(fig, "ICA-609 IC 卡座　麵包板轉接板（請老師確認）", "卡座的 8 個觸點和插卡偵測開關，轉成兩排 1×5 排針，直接插在麵包板上用")
    img(fig, r_scene, [0.0, 0.08, 0.58, 0.78])
    txt = ("板子\n"
           "  • 單面板，銅箔在正面；FR-4 1.6 mm\n"
           "  • T 字形，外框 58.76 × 43.50 mm\n"
           "  • 只有轉接，沒有其他零件\n\n"
           "卡座 J1（Hamburg ICA-609 Type2 NO）\n"
           "  • 裝在 PCB 背面、吊在麵包板旁邊\n"
           "  • 腳穿上來在正面焊\n"
           "  • IC 卡從下方插入，晶片朝上\n\n"
           "排針 J2、J3（1×5，2.54 mm）\n"
           "  • 塑膠座在 PCB 和麵包板中間\n"
           "  • 上排插 d1–d5，下排插 g1–g5\n")
    fig.text(0.60, 0.84, txt, fontsize=11.5, va="top", linespacing=1.55)
    ax = fig.add_axes([0.60, 0.10, 0.37, 0.22]); ax.axis("off")
    rows = [["麵包板孔", "1", "2", "3", "4", "5"],
            ["上排 d", "C1", "C2", "C3", "C4", "SW1"],
            ["下排 g", "C5", "C6", "C7", "C8", "SW2"]]
    t = ax.table(cellText=rows, loc="center", cellLoc="center")
    t.auto_set_font_size(False); t.set_fontsize(11); t.scale(1, 1.8)
    for (r, c), cell in t.get_celld().items():
        if r == 0 or c == 0:
            cell.set_facecolor("#eeeeee")
    fig.text(0.60, 0.085, "第 1 欄靠卡座。C1–C8 為 ISO 7816 觸點，SW1/SW2 為常開偵測開關（插卡導通）", fontsize=9, color="#444")
    pdf.savefig(fig); plt.close(fig)

    # ---- page 2: KiCad PCB preview ----
    fig = plt.figure(figsize=A4, facecolor="white")
    page_title(fig, "PCB 正面（KiCad）", "紅色：銅箔走線與焊盤（只在正面）；黃色：絲印；虛線／灰框：吊在背面的卡座外框；J2 插麵包板 d1–d5、J3 插 g1–g5")
    img(fig, os.path.join(HERE, "預覽_PCB.png"), [0.04, 0.02, 0.92, 0.86])
    pdf.savefig(fig); plt.close(fig)

    # ---- page 3: dimensions ----
    fig = plt.figure(figsize=A4, facecolor="white")
    page_title(fig, "尺寸（mm）", "卡座腳位照規格書「Reference dimension for PCB layout」；因卡座裝背面，正面看是左右鏡像")
    img(fig, os.path.join(HERE, "尺寸圖.png"), [0.02, 0.0, 0.96, 0.89])
    pdf.savefig(fig); plt.close(fig)

    # ---- page 4: on the breadboard ----
    fig = plt.figure(figsize=A4, facecolor="white")
    page_title(fig, "插在麵包板上的樣子", "俯視圖＋側視圖")
    img(fig, os.path.join(HERE, "配置圖_麵包板.png"), [0.10, 0.0, 0.80, 0.89])
    pdf.savefig(fig); plt.close(fig)

print(OUT)
