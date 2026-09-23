# R2M-B01／B03 針刺產物

隔離 Rhino 8.35／CPython 3.9.10 寫出（`tools/ifcopenshell_spike.py`）。輪子不在本目錄（見 repo `.vendor/`，已 gitignore）。全部是 IFC4、單位公尺、座標不平移。

| 檔 | 角色 | 幾何表示法 |
|---|---|---|
| `R2M_spike_shell.ifc` | 建築殼：IfcWall + IfcCovering（天花） | `IfcExtrudedAreaSolid`（參數化量體） |
| `R2M_spike_shell_mesh.ifc` | 同上，幾何等價 | `IfcTriangulatedFaceSet`（**產品實際會用**） |
| `R2M_spike_pipe.ifc` | 管線外參：IfcPipeSegment | `IfcExtrudedAreaSolid` |
| `ac_morph.ifc` | 家中 Archicad 29 Morph 匯出（IFC4 Reference View、Selected elements only）。**不是**真實風管／水管 | Archicad 寫成 `IfcBuildingElementProxy` |

幾何尺寸（公尺）：牆 4 × 0.2 × 2.8，貼在 Y=0 側；天花 4 × 4，底在 2.8、頂在 2.9。管頂在 2.575，與天花底淨空 0.225。`ac_morph.ifc` 尺寸以 Archicad 現場為準。

## 給家中 BIM 驗證

**收建築殼用 `R2M_spike_shell_mesh.ifc`。** 產品會把任意 Rhino 幾何轉三角網面，不會輸出參數化量體，所以只測 `R2M_spike_shell.ifc` 不代表產品行為。Archicad：**檔案 → 開啟**當新檔，不要 Merge。

**Inbound 對位**（2026-09-23 已過）：空白 `.3dm` 跑 `RMInbound`，選 `ac_morph.ifc`，再選工作檔旁 `config.json`，位置正確。完整步驟見 `wip/docs/開發任務與路徑.md` 的 B03。
