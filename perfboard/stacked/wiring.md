# 洞洞板第一版（最小化）

洞洞板 22×10 孔（55.9×25.4 mm）；含兩端 USB-C 整體約 **56.3 × 25.4 × 17.2 mm**。
孔位 (c, r)：c 為欄 1–22（左→右）、r 為列 1–10（下→上），一律以**正面俯視**標示。

## 零件位置

| 零件 | 面 | 孔位 | 備註 |
|---|---|---|---|
| U2 BlackPill | 正面，朝上 | c2–c21 × r2（B12…A9(c7)…5V c19/G c20/3.3 c21）、r8（5V c2/G c3/3.3 c4…VB c21） | USB-C 朝左緣 |
| U1 nice!nano | 反面，朝下 | c10–c21 × r9（RAW c21/GND c20/RST/VCC…P0.09 c10）、r3（P0.06 c21/P0.08 c20/GND c19/GND c18…P1.06 c10） | USB-C 朝右緣 |
| U3 DMC2038LVT（SOT-23-6 轉接板） | 反面，朝下 | r7：G2 c3、S2 c4、G1 c5；r4：D2 c3、S1 c4、D1 c5 | |
| R1 | 反面 | c3 r1 ↔ c6 r1 | |
| 電池 | 反面，貼在 nice!nano 下方（Kapton 絕緣） | 避開 nice!nano 的 USB-C | 假設 30×25×5 mm |

## 接線

| 線號 | 顏色 | 面 | 起點 | 終點 | 用途 |
|---|---|---|---|---|---|
| W1 | 紅 | 反面 | 電池 + | U1 RAW (c21,r9) | 電池正極 → RAW |
| W2 | 黑 | 反面 | 電池 − | U1 GND (c20,r9) | 電池負極 → GND（產品改接） |
| W3 | 黃 | 反面 | U2 PA9 (c7,r2) | U1 P0.08 (c20,r3) | UART：BlackPill TX → nRF RX |
| W4 | 黑 | 反面 | U1 GND (c19,r3) | U2 G (c20,r2) | nRF GND ↔ BlackPill GND |
| W5 | 紅 | 正面 | U2 5V (c2,r8) | U3 G2 (c3,r7) | BlackPill 5V → G2 |
| W6 | 黑 | 正面 | U2 G (c3,r8) | U3 S2 (c4,r7) | S2 → GND |
| W7 | 黑 | 正面 | U3 S2 (c4,r7) | U3 S1 (c4,r4) | S1 → GND |
| W8 | 紅 | U3 轉接板上 | U3 G1 (c5,r7) | U3 D2 (c3,r4) | G1 ↔ D2 相連 |
| W9 | 紅 | 正面 | U3 D2 (c3,r4) | R1 (c3,r1) | D2 → R1 |
| W10 | 橘 | 正面 | U3 D1 (c5,r4) | R1 (c6,r1) | D1 → R1 |
| W11 | 橘 | 正面 | R1 (c6,r1) | U1 P1.06 (c10,r3) | D1 → nRF P1.06 |

正面的線在 BlackPill 底下、反面的線在 nice!nano 底下，所以要**先焊線、再裝模組**。
