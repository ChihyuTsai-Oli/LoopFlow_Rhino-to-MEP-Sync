# LoopFlow｜Rhino to MEP Sync

[English](./README.md)

Rhino 發布建築殼 IFC 給 Revit／Archicad／Blender Bonsai；BIM 端把 MEP 幾何 IFC 送回 Rhino，當 Worksession 外參。**設計判斷只在 Rhino。** 交換只使用 IFC。BIM 端沒有 LoopFlow 外掛。

[▶ 使用說明](./docs/README.md) · [▶ GitHub](https://github.com/ChihyuTsai-Oli/LoopFlow_Rhino-to-MEP-Sync)

指令名已凍結：`RMOpen`、`RMStorey`、`RMModels`、`RMInbound`。正式套件與工具列尚未上架；目前在 Rhino 指令列貼 ScriptEditor 那一行執行。畫面為英文；本說明為正體中文。

## 主要功能

- **樓層登記** — 手動建立各層水平封閉曲線，登記名稱與 FL 結構面高程
- **建築殼發布** — 依高程框把選取圖層寫成一份 IFC（長度單位公分）
- **高度校正** — BIM 裡的高度跟著 FL；`RMInbound` 把回來的幾何扣回 Rhino 模型 Z（不是停在建築標高數字上）
- **管線／牆外參** — BIM 匯出的 IFC 建成網面（不鎖定），手動另存後掛進工作檔對照
- **開案摘要** — 看設定資料夾與上次成功寫出的時間

沒有相機、燈光、即時連線。不要把外參幾何拿去出圖或當 Tag 來源。

## 系統需求

- **Rhino 8**（Windows）
- **Archicad**、**Revit** 或 **Blender Bonsai**（必須是 3D BIM）

交換只使用 **IFC**。Archicad：檔案 → 開啟當新檔（不要 Merge）。Revit：連結 IFC，再依框線高程自建 Level 並開 Floor Plan。Bonsai 只列為作業環境，**本產品不測**。

Archicad、Revit 收殼與牆回檔（含高度校正）已通過。真實風管／水管尚未測。

## 目前怎麼跑

請把 [指令逐項說明](./docs/COMMANDS_zh-TW.md) 裡的那一行貼到 Rhino **指令列**。開始前先把 `.3dm` 存檔（Inbound 可用空白新檔）。`.3dm` 所在資料夾就是作業資料夾；設定與 IFC 在同層 `_LoopFlow_Config/loopflow_R2M/`。

同一資料夾的整棟與單層共用一份 `config.json`。要對單層做 Inbound，請先對單層跑過 `RMModels`，校正值才會是單層的。

## 快速開始

1. 畫各樓層高程框，跑 `RMStorey`。
2. 跑 `RMModels`，寫出 `models/R2M.ifc`。整棟與單層要留兩份時，發布後立刻改名。
3. Archicad：**檔案 → 開啟**該 IFC 當新檔。Revit：**連結 IFC**，再自建同高 Level 並開 Floor Plan。
4. 畫 3D 幾何（測試可用牆），內建匯出 **IFC4**，只出選取物件，座標不要另做偏移。
5. Rhino 空白檔跑 `RMInbound`（選工作檔 `config.json`），手動另存，再掛進工作檔的 Worksession。回來的高度會對上 Rhino 模型。

逐步見 [使用說明總覽](./docs/USER_GUIDE_zh-TW.md) 與 [指令逐項說明](./docs/COMMANDS_zh-TW.md)。

## 授權與出處

MIT。見 [LICENSE](./LICENSE)。圖示出處見 [CREDITS](./CREDITS.md)。
