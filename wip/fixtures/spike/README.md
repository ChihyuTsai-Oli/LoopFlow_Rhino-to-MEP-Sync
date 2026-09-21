# R2M-B01／B03 針刺產物

隔離 Rhino 8.35／CPython 3.9.10 寫出（`wip/tools/ifcopenshell_spike.py`）。輪子不在本目錄（見 repo `wip/.vendor/`，已 gitignore）。全部是 IFC4、單位公尺、座標不平移。

| 檔 | 角色 | 幾何表示法 |
|---|---|---|
| `R2M_spike_shell.ifc` | 建築殼：IfcWall + IfcCovering（天花） | `IfcExtrudedAreaSolid`（參數化量體） |
| `R2M_spike_shell_mesh.ifc` | 同上，幾何等價 | `IfcTriangulatedFaceSet`（**產品實際會用**） |
| `R2M_spike_pipe.ifc` | 管線外參：IfcPipeSegment | `IfcExtrudedAreaSolid` |

幾何尺寸（公尺）：牆 4 × 0.2 × 2.8，貼在 Y=0 側；天花 4 × 4，底在 2.8、頂在 2.9。管頂在 2.575，與天花底淨空 0.225。

## 給家中 BIM 驗證

**用 `R2M_spike_shell_mesh.ifc`。** 產品會把任意 Rhino 幾何轉三角網面，不會輸出參數化量體，所以只測 `R2M_spike_shell.ifc` 不代表產品行為。

請用 BIM 軟體的**連結**功能（Revit「連結 IFC」／Archicad「合併」），不要當原生檔轉來轉去。確認能開啟、尺寸對、元件在原點附近、看得到 Level 1 樓層。完整步驟見 `wip/docs/開發任務與路徑.md` 的「B03 家中 BIM 驗證步驟」。
