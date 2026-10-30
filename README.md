# 20261030_3D — 麵包板線路還原與 3D 模型

由同一塊麵包板的三張照片交叉判讀出接線位置，畫成原理圖，再做成 3D 模型。

- 左：Pro Micro nRF52840（nice!nano v2 相容）
- 右：WeAct BlackPill（STM32F401/F411）
- 中：U3 = **DMC2038LVT**（Diodes，互補 MOSFET：Q1 N 通道＋Q2 P 通道，TSOT26），裝在 SOT-23 轉 DIP 轉接板上；S1 接 GND、G2 接 BlackPill 5V、G1↔D2 相連，R1 跨在 D1 與 D2 之間（腳位對應依 1 號腳在欄27上推定）
- 其他：LiPo 電池（＋ 接 nRF RAW）、兩組 SWD 引出排針（nRF 側 J4⇄J1、BlackPill 側 J3⇄J2）

> 所有零件與跳線都依判讀出的麵包板座標（欄 1–63、列 a–j）擺放，判讀誤差約 ±1 欄。

## 分區說明圖

![分區說明圖](breadboard_annotated.png)

## 3D 圖

### 整體斜視
![整體斜視](3D/overview.png)

### U3（DMC2038LVT）特寫
![U3 特寫](3D/u3_closeup.png)

### 俯視
![俯視](3D/top.png)

### 正面低角度
![正面低角度](3D/front_low.png)

### 反向斜視
![反向斜視](3D/reverse.png)

## 檔案

| 檔案 | 內容 |
|---|---|
| `breadboard_annotated.png` / `.svg` | 分區說明圖（A–H 功能分區＋訊號與電源路徑） |
| `breadboard_restore.kicad_sch` | KiCad 原理圖 |
| `breadboard_restore_kicad.pdf` / `.svg` | KiCad 匯出的原理圖 |
| `breadboard_restore.svg` / `_preview.png` | 示意圖 |
| `3D/*.png` | 3D 算圖 |
| `3D/breadboard_3d.kicad_pcb` | 用 KiCad 開啟後按 **Alt+3** 可旋轉檢視 |
| `3D/breadboard_3d.wrl` | 3D 模型（要跟 kicad_pcb 放在同一個資料夾） |
| `scripts/` | 產生上述檔案的 Python 腳本 |
