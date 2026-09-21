# LoopFlow R2M Repository Instructions

範圍：本 repo。另須遵守上一層 `E:\_GitHub\AGENTS.md`。

## 開始作業前必讀

AI 必須依序完整讀取：

1. `wip/docs/實作總覽.md`
2. `wip/docs/資料契約.md`
3. `wip/docs/工作流程.md`
4. `wip/docs/開發任務與路徑.md`
5. `wip/docs/系統設定.md`
6. `wip/docs/重構進度.md`

契約細節未盤完或需追溯決策時另讀：`wip/docs/前期規劃/資料生態決策表.md`、`wip/docs/rhino指令.md`。`前期規劃/` 其餘檔是原則／過程，不是日常實作規格；與六份正式文件衝突時以六份為準。

公開的 `README*.md` 是使用者入口，不是實作權威。開發中的文件、原始碼、fixtures 與測試統一放在 `wip/`。Dropbox 工作檔路徑依上一層 `工作檔路徑.md` 解析，不得寫死單一電腦的絕對路徑。

## 產品定位

獨立產品：**Rhino 發布建築殼 IFC ↔ Revit／Archicad 發布管線 IFC（鎖定參考回 Rhino）**。不是 LoopFlow 2.0 出圖、不是 R2B、不是 R2O。沒有 3D BIM 對口就不做。BIM 端不寫外掛。

跨產品順序：R2B／R2O 主鏈已發布；本產品 IfcOpenShell **Rhino 端針刺已過**，尚未寫產品指令。功能碼須兩端能測再寫（Models 的消費＝BIM 能連結）。

## 分支與版本

- `main` 目前是文件骨架；尚無發布 tag。
- 開始寫程式時從 `main` 建立 `v1-development`，每批再開 `codex/v1-<scope>`；不要把 R2M 合進 LoopFlow／R2B／R2O 的整合分支。
- 日後 tag／Release 永不移動或覆寫。

## 文件與語言

- 維護、架構、設定與進度文件一律使用繁體中文。
- 對外英文 README 是發布翻譯；功能事實改變時必須與繁中同步。
- 模組完整責任、流程、schema、副作用寫入 `wip/docs/` 六份正式文件。
- 新增或修改的 docstring、區塊註解與行內註解使用繁體中文；API、識別字、Rhino／IFC／第三方授權文字維持原文。

## AI 作業流程

**開發節奏：能做就做、需確認再停。** 在已決契約與 `開發任務與路徑.md` 範圍內直接推進文件與可自動驗證的實作；僅在改已決 ED、凍結使用者可見名稱／檔名、破壞性操作、本機正式 runtime 安裝、或明顯契約衝突時停下來問使用者。

1. 確認 repo、branch、origin 與乾淨工作樹；只用 fast-forward pull。
2. 讀取上述六份文件，從 `重構進度.md` 確認目前階段與限制。
3. 一批只處理一個範圍。
4. 本階段以文件為準；針刺與功能碼另批。
5. 同步更新六份正式文件中受影響者。
6. 檢查 diff 後提交、推送。

使用者不負責操作 Git 或自行推導技術步驟；AI 應直接完成安全、可逆的操作，並以簡短繁體中文回報結果。
