# R2M 開發期 Rhino 指令

名稱皆為 **開發暫定，未凍結**。凍結前不要做 Package Manager 畫面名、工具列、正式使用說明。

| 候選 | 角色 |
|---|---|
| `RMStorey` | 選全部高程框 → 點 1F → 輸入 1F 高程 → 點 RF → 自動編列樓層名與高程，搬到 `R2M::Storey` |
| `RMModels` | 確認樓層 → 排除記號 → 巢狀圖層樹 → IFC 類型 → 類別勾選 → 網格密度 → 發布建築殼 IFC |
| `RMInbound` | 確認單位 → 選 IFC → 類別統計 →（可選件數警告）→ 建鎖定網面 |
| `RMOpen` | Health 摘要；開 Config／models／Docs |

介面英文。`RMModels`／`RMOpen` 未存檔則停；`RMStorey`／`RMInbound` 不要求已存檔（未存檔只是不寫 log）。`RMModels` 發布前會再列出圖層→類型對照，避免同層混放牆／天花被靜默當成單一類型。

對照 R2B `RB*`、R2O `RO*`；本產品前綴暫用 `RM`。正式 yak 裝好前，**不要**在指令列打 `RMOpen` 這三個名字（尚未註冊）。

## 可複製貼上（開發期）

在 Rhino **指令列**貼上一整行，按 Enter。兩台 Git 根目錄都是 `E:\_GitHub`。隔離檔再跑，不要動正在編輯的工作檔。

**RMOpen**（先存檔）

```
! _-ScriptEditor _Run "E:\_GitHub\LoopFlow_Rhino-to-MEP-Sync\commands\RMOpen.py"
```

**RMStorey**（先自己畫好各樓層的水平封閉曲線，含 RF）

```
! _-ScriptEditor _Run "E:\_GitHub\LoopFlow_Rhino-to-MEP-Sync\commands\RMStorey.py"
```

**RMModels**（先存檔，且已跑過 `RMStorey`）

```
! _-ScriptEditor _Run "E:\_GitHub\LoopFlow_Rhino-to-MEP-Sync\commands\RMModels.py"
```

**RMInbound**（空白檔即可；測檔選 `fixtures\spike\R2M_spike_pipe.ifc`）

```
! _-ScriptEditor _Run "E:\_GitHub\LoopFlow_Rhino-to-MEP-Sync\commands\RMInbound.py"
```
