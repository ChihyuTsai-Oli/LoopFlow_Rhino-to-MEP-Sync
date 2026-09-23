# LoopFlow｜Rhino to MEP Sync

[English](./README.md)

> **開發草稿。** 指令名稱、畫面名與安裝方式尚未凍結。還沒有 Package Manager 套件或工具列。請不要把本頁當成已發布產品的安裝說明。

Rhino 發布建築殼 IFC 給 Revit／Archicad／Blender Bonsai；BIM 端把管線 IFC 送回 Rhino，當**鎖定的 Worksession 外參**。設計判斷只在 Rhino。交換只使用 IFC。BIM 端沒有 LoopFlow 外掛。

[▶ 使用說明](./docs/README.md) · [▶ GitHub](https://github.com/ChihyuTsai-Oli/LoopFlow_Rhino-to-MEP-Sync)

## 主要功能

- **建築殼發布** — 依樓層高程框，把選取圖層寫成一份建築殼 IFC
- **樓層登記** — 自己畫各層水平封閉曲線，登記名稱與 FL 結構面高程
- **管線外參** — 把 BIM 匯出的 3D 管線 IFC 轉成鎖定網面，手動掛進工作檔對照
- **開案摘要** — 看設定資料夾與上次成功寫出的時間

沒有相機、燈光、即時連線。不要把外參幾何拿去出圖或當 Tag 來源。

## 系統需求

- **Rhino 8**（Windows）
- **Archicad**、**Revit** 或 **Blender Bonsai**（必須是 3D BIM）。沒有 3D 就不做

測試暫以 Archicad 為準。Archicad 用「檔案 → 開啟」把 IFC 當新檔，整棟與單層已通過。Revit 與 Bonsai 尚未測。從 BIM 匯出真實管線 IFC 尚未測過。

Rhino 對話框為英文；本說明為正體中文。

## 開發期怎麼跑

正式 yak 尚未打包。請把 [指令逐項說明](./docs/COMMANDS_zh-TW.md) 裡的那一行貼到 Rhino **指令列**，用 ScriptEditor 跑。指令名稱（`RMOpen`、`RMStorey`、`RMModels`、`RMInbound`）是開發暫定，尚未註冊成正式指令。

開始前先把 `.3dm` 存檔（Inbound 可用空白新檔）。`.3dm` 所在資料夾就是作業資料夾；設定與 IFC 在同層 `_LoopFlow_Config/loopflow_R2M/`。

## 快速開始

1. 畫各樓層高程框，跑 `RMStorey`。
2. 跑 `RMModels`，寫出 `models/R2M.ifc`。
3. Archicad：**檔案 → 開啟**，把該 IFC 當新檔。不要 Merge。
4. 在該檔畫幾段跨越天花的 **3D** 風管或水管，再用內建功能匯出 **IFC4**（只出 3D 管線）。
5. Rhino 開空白檔跑 `RMInbound`，手動另存，再掛進工作檔的 Worksession。

逐步與按鈕見 [使用說明總覽](./docs/USER_GUIDE_zh-TW.md) 與 [指令逐項說明](./docs/COMMANDS_zh-TW.md)。

## 授權與出處

MIT。見 [LICENSE](./LICENSE)。圖示出處見 [CREDITS](./CREDITS.md)。
