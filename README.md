# 20261030_3D — 麵包板組裝 3D 模型

由同一塊麵包板的三張照片交叉判讀出接線位置，再做成 3D 模型。

- 左：Pro Micro nRF52840（nice!nano v2 相容）
- 右：WeAct BlackPill（STM32F401/F411）
- 中：U3 = **3.3V LDO 穩壓 IC**（SOT-23-5，AP2112K-3.3 同腳位系列），裝在 SOT-23 轉 DIP 轉接板上；吃 BlackPill 的 5V，輸出 3.3V 接負載電阻 R1
- 其他：LiPo 電池（＋ 接 nRF RAW）、兩組 SWD 引出排針（nRF 側 J4⇄J1、BlackPill 側 J3⇄J2）

> 所有零件與跳線都依判讀出的麵包板座標（欄 1–63、列 a–j）擺放，判讀誤差約 ±1 欄。
> 開發板為簡化外形；紫色線束鑽進板底的那一段為示意。

## 3D 圖

### 整體
![整體斜視](3D/overview.png)

### U3（3.3V LDO）特寫
![U3 特寫](3D/u3_closeup.png)

## 檔案

| 檔案 | 內容 |
|---|---|
| `3D/overview.png` | 整體斜視，底板前緣標有元件名稱 |
| `3D/u3_closeup.png` | 中間轉接板（U3）、R1、電池接頭的近拍 |
| `3D/breadboard_3d.kicad_pcb` | KiCad 承載板，開啟後按 **Alt+3** 進 3D 檢視器旋轉檢視 |
| `3D/breadboard_3d.wrl` | 麵包板組裝的 VRML 模型（kicad_pcb 會引用它，兩者要放在同一個資料夾） |
