# R2M 開發期 Rhino 指令

名稱 **已凍結**（2026-09-28）：`RMOpen`、`RMStorey`、`RMModels`、`RMInbound`。公開套件 `loopflow-rhino-to-mep-sync` **1.0.0**。開發工具列：`wip/docs/toolbar/LoopFlow_R2M.rui`（按鈕跑 `! _RMOpen` 等）。公開說明在 `docs/USER_GUIDE_zh-TW.md`／`docs/COMMANDS_zh-TW.md`（英文已對齊）。

| 指令 | 角色 |
|---|---|
| `RMStorey` | 說明窗 → 選框 → 彈窗選整棟或只做其中幾層 → 編列名稱／高程，搬到 `R2M::Storey` |
| `RMModels` | 確認樓層 → 排除記號 → 最末端圖層（全選／還原上次）→ IFC 類型（未選＝IfcPlate；天花＝IfcCovering）→ 類別勾選 → 網格密度 → 發布建築殼 IFC |
| `RMInbound` | 確認單位 → 選 IFC →（必要時選工作檔 `config.json`）→ 類別統計 →（可選件數警告）→ 建網面（不鎖定），Z 扣 `elevation_shift` |
| `RMOpen` | Health 摘要；開 Config／models。Open Docs 開 GitHub 專案頁 `https://github.com/ChihyuTsai-Oli/LoopFlow_Rhino-to-MEP-Sync` |

介面英文。`RMModels`／`RMOpen` 未存檔則停；`RMStorey`／`RMInbound` 不要求已存檔（未存檔只是不寫 log）。`RMModels` 只發布嚴格落在該層高程框內的勾選圖層物件；碰到框線則停。發布前會再列出圖層→類型對照。未選類型的勾選圖層寫成 `IfcPlate`；天花請選 `IfcCovering`。

對照 R2B `RB*`、R2O `RO*`；本產品前綴 `RM`。套件裝好並重開 Rhino 後，指令列可打這四個名字，或按工具列。登錄後的指令仍會先找本機 `wip/src`，每次丟掉已載入的 `loopflow_r2m`，改程式不必重開 Rhino。`wip/commands/` 的 ScriptEditor 入口仍保留當後備。

## 開發工具列

Rhino：**Options → Toolbars → File → Open** `E:\_GitHub\LoopFlow_Rhino-to-MEP-Sync\wip\docs\toolbar\LoopFlow_R2M.rui`。分頁名 **LoopFlow R2M**。圖示由 `wip/tools/build_toolbar_rui.py` 產生，不要手改 GUID。

## 可複製貼上

在 Rhino **指令列**貼上一整行，按 Enter。須已裝 `loopflow-rhino-to-mep-sync` 並重開 Rhino。兩台 Git 根目錄都是 `E:\_GitHub`。隔離檔再跑，不要動正在編輯的工作檔。

**RMOpen**（先存檔）

```
! _RMOpen
```

**RMStorey**（先自己畫好各樓層的水平封閉曲線，含 RF）

```
! _RMStorey
```

**RMModels**（先存檔，且已跑過 `RMStorey`）

```
! _RMModels
```

**RMInbound**（空白檔即可；測檔選 `wip\fixtures\spike\R2M_spike_pipe.ifc`）

```
! _RMInbound
```
