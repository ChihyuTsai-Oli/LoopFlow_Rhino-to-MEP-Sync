# R2M 開發期 Rhino 指令

名稱皆為 **開發暫定，未凍結**。凍結前不要做 Package Manager 畫面名、工具列。公開使用說明初稿在 `docs/USER_GUIDE_zh-TW.md`／`docs/COMMANDS_zh-TW.md`，仍標開發草稿。

| 候選 | 角色 |
|---|---|
| `RMStorey` | 說明窗 → 選框 → 彈窗選整棟或只做其中幾層 → 編列名稱／高程，搬到 `R2M::Storey` |
| `RMModels` | 確認樓層 → 排除記號 → 最末端圖層（全選／還原上次）→ IFC 類型（未選＝IfcPlate；天花＝IfcCovering）→ 類別勾選 → 網格密度 → 發布建築殼 IFC |
| `RMInbound` | 確認單位 → 選 IFC →（必要時選工作檔 `config.json`）→ 類別統計 →（可選件數警告）→ 建鎖定網面，Z 扣 `elevation_shift` |
| `RMOpen` | Health 摘要；開 Config／models。Open Docs 目前開 repo 根 `docs/`（入口 `docs/README.md`）；合入後有穩定 GitHub 頁再改開該 URL |

介面英文。`RMModels`／`RMOpen` 未存檔則停；`RMStorey`／`RMInbound` 不要求已存檔（未存檔只是不寫 log）。`RMModels` 只發布嚴格落在該層高程框內的勾選圖層物件；碰到框線則停。發布前會再列出圖層→類型對照。未選類型的勾選圖層寫成 `IfcPlate`；天花請選 `IfcCovering`。

對照 R2B `RB*`、R2O `RO*`；本產品前綴暫用 `RM`。正式 yak 裝好前，**不要**在指令列打 `RMOpen` 這三個名字（尚未註冊）。開發期從 ScriptEditor 跑時，每次會丟掉已載入的 `loopflow_r2m`，不必為了換程式碼而重開 Rhino。

## 可複製貼上（開發期）

在 Rhino **指令列**貼上一整行，按 Enter。兩台 Git 根目錄都是 `E:\_GitHub`。隔離檔再跑，不要動正在編輯的工作檔。

**RMOpen**（先存檔）

```
! _-ScriptEditor _Run "E:\_GitHub\LoopFlow_Rhino-to-MEP-Sync\wip\commands\RMOpen.py"
```

**RMStorey**（先自己畫好各樓層的水平封閉曲線，含 RF）

```
! _-ScriptEditor _Run "E:\_GitHub\LoopFlow_Rhino-to-MEP-Sync\wip\commands\RMStorey.py"
```

**RMModels**（先存檔，且已跑過 `RMStorey`）

```
! _-ScriptEditor _Run "E:\_GitHub\LoopFlow_Rhino-to-MEP-Sync\wip\commands\RMModels.py"
```

**RMInbound**（空白檔即可；測檔選 `wip\fixtures\spike\R2M_spike_pipe.ifc`）

```
! _-ScriptEditor _Run "E:\_GitHub\LoopFlow_Rhino-to-MEP-Sync\wip\commands\RMInbound.py"
```
