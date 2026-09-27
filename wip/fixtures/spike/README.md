# R2M-B01／B03 針刺與 BIM 回檔測檔

隔離 Rhino 8.35／CPython 3.9.10 寫出的針刺檔（`tools/ifcopenshell_spike.py`）。輪子不在本目錄（見 `wip/.vendor/`，已 gitignore）。針刺 IFC 是 IFC4、**單位公尺**、座標不平移。**產品 `RMModels` 改寫公分**（ED-22）。

| 檔 | 角色 | 幾何表示法 |
|---|---|---|
| `R2M_spike_shell.ifc` | 建築殼：IfcWall + IfcCovering（天花） | `IfcExtrudedAreaSolid`（參數化量體） |
| `R2M_spike_shell_mesh.ifc` | 同上，幾何等價 | `IfcTriangulatedFaceSet`（**產品實際會用**） |
| `R2M_spike_pipe.ifc` | 管線外參：IfcPipeSegment | `IfcExtrudedAreaSolid` |
| `ac_wall.ifc` | 家中 Archicad 29 牆匯出（IFC4）。**不是**真實風管／水管 | `IfcWall`；3F／4F |
| `revit_wall.ifc` | 家中 Revit 3F／4F 牆匯出（IFC4）。**不是**真實風管／水管 | Revit 牆 |

幾何尺寸（公尺，針刺檔）：牆 4 × 0.2 × 2.8，貼在 Y=0 側；天花 4 × 4，底在 2.8、頂在 2.9。管頂在 2.575，與天花底淨空 0.225。`ac_wall.ifc`／`revit_wall.ifc` 尺寸以現場為準。

舊測檔 `ac_morph.ifc`（Morph／Proxy）已由 `ac_wall.ifc` 取代。

## 給家中 BIM 驗證

**收建築殼用產品 `RMModels` 產出（公分）或針刺 `R2M_spike_shell_mesh.ifc`。** 不要只測 `R2M_spike_shell.ifc`。Archicad：**檔案 → 開啟**當新檔，不要 Merge。Revit：**連結 IFC**，再自建同高 Level 並開 Floor Plan。

**Inbound 對位（2026-09-28 已過）**

空白 `.3dm` 跑 `RMInbound`，選工作檔旁 `config.json`（先對**單層**跑過 `RMModels`，`elevation_shift` 才不是 0）。

- Archicad：`ac_wall.ifc`，高度有校正。
- Revit：`revit_wall.ifc`，高度有校正。

完整步驟見 `wip/docs/開發任務與路徑.md` 的 B03 與 `docs/COMMANDS_zh-TW.md`。
