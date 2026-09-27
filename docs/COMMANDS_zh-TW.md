# LoopFlow R2M 指令逐項說明

> 指令名稱已凍結：`RMOpen`、`RMStorey`、`RMModels`、`RMInbound`。還沒有套件或工具列；目前貼 ScriptEditor 那一行執行。
>
> 整體流程見 [使用說明總覽](./USER_GUIDE_zh-TW.md)。
>
> Rhino 對話框為英文。

## 目前怎麼跑

正式 yak 還沒裝。請在 Rhino **指令列**貼上一整行再按 Enter。兩台電腦的 Git 根目錄都是 `E:\_GitHub`。請開隔離檔再跑，不要動正在編輯的工作檔。

每次從 ScriptEditor 跑都會丟掉已載入的程式，同一 Rhino 視窗重跑就會用磁碟上的新碼。

## 快速索引

| 階段 | Rhino | BIM | 一句話 |
|---|---|---|---|
| 開案 | `RMOpen` | — | 看設定根與上次成功時間；開資料夾或本說明 |
| 樓層 | `RMStorey` | — | 選高程框，編成樓層名與 FL |
| 建築殼 | `RMModels` | 開啟／連結 IFC | 選圖層寫出 `R2M.ifc`（公分） |
| 幾何外參 | `RMInbound` | 內建匯出 IFC4 | 空白檔建網面（不鎖定）；**高度校正**後手動另存與掛載 |

## 目錄

[01 開啟設定與說明](#01-開啟設定與說明) · [02 樓層高程框](#02-樓層高程框) · [03 建築殼](#03-建築殼) · [04 BIM 收檔](#04-bim-收檔) · [05 幾何外參與高度校正](#05-幾何外參與高度校正) · [06 不要做的事](#06-不要做的事)

---

## 01　開啟設定與說明

**指令**：`RMOpen`（先存檔）

```
! _-ScriptEditor _Run "E:\_GitHub\LoopFlow_Rhino-to-MEP-Sync\wip\commands\RMOpen.py"
```

跳出英文 Health 視窗。摘要列出設定根路徑，以及上次成功寫出的時間。未存檔會被擋住。

按鈕：

- **Open Config** — 開啟 `_LoopFlow_Config/loopflow_R2M/`
- **Open models** — `R2M.ifc` 所在資料夾
- **Open Docs** — 目前開本機 `docs/`（本說明的入口是 [docs/README.md](./README.md)）。上 GitHub 之後會改開該頁

---

## 02　樓層高程框

**指令**：`RMStorey`（不要求已存檔；未存檔只是不寫 log）

```
! _-ScriptEditor _Run "E:\_GitHub\LoopFlow_Rhino-to-MEP-Sync\wip\commands\RMStorey.py"
```

Models 之前必須先有 **R2M 高程框**。沒有就擋住，不發布。

### 畫框

自己畫封閉曲線，**一個樓層一個框，畫在該樓層自己的高度上**。框只要是水平的平面封閉曲線即可，形狀不拘。

- **框必須比外牆再大一圈。** 貼齊邊的物件會被 `RMModels` 擋住。
- 臨時編輯的物件移到框外即可（例如 x+1000），不必換圖層；同層框外件會被跳過。
- **RF 一定要畫（整棟模式）。** 屋頂板、女兒牆都掛在 RF。只畫其中幾層時不要硬找 RF，改走非整棟模式。
- **有屋凸就在 RF 上面再畫框**（機房、水塔、樓梯間），會自動編成 R2F、R3F。
- **沒有屋凸就不用多畫。** 最高層沒有上界，比它高的物件一律掛它。
- 地下室畫在 1F 下面，會自動編成 B1、B2（由近而遠）。

**非整棟、跨層物件：** 幾何的底部或頂部只要超出目前已畫高程框的範圍，就要把那一層框也畫進去，Archicad 才顯示得完整。底部超出＝低於最低層會被跳過。頂部超出＝對方檔沒有那層標高，看起來會黏在下一層。整棟模式框已齊，不適用這條。不發明沒畫的樓層。

### 登記

選框前會先彈窗確認：框必須閉合、水平、且嚴格大於要發布的物件。先選全部框，再彈窗選 **WholeBuilding** 或 **PartialStoreys**（不要在指令列按 Enter 選模式）。

**整棟（WholeBuilding）**

1. 選取全部樓層框 → Enter
2. 選取 1F 框 → Enter
3. 彈窗輸入 1F 高程（Rhino 文件單位，公分檔就填公分）→ Enter
4. 選取 RF 框 → Enter

其餘樓層的高程由各框自身的 Z 推算，名稱依序自動編 B1／1F／2F／RF／R2F。

**只做其中幾層（PartialStoreys）**

模型不是整棟時用這個，例如整棟 20 層但只畫 5F。**不要**硬找 1F、RF，也**不要**補空樓層進 IFC。

1. 選取模型裡實際有的樓層框 → Enter
2. 點其中一層當基準 → Enter
3. 彈窗輸入該層名稱（例如 `5F`）→ Enter
4. 彈窗輸入該層 FL（例如 `1600`）→ Enter

其餘依框的高低連續編號（5F 上面是 6F；低於 1F 是 B1）。非整棟不產生 RF／R2F。

兩種模式都會把框搬到圖層 `R2M::Storey`，並寫入 UserText `R2M_StoreyName`（樓層名）與 `R2M_FL`（FL 結構面高程）。

### 修改

- **改樓高**：移動框到新的高度，重跑 `RMStorey`。
- **改樓層名**：可以直接改 `R2M_StoreyName`，但**重跑 `RMStorey` 會整批覆寫回自動名稱**。
- **不要手改 `R2M_FL`。** 它由 `RMStorey` 寫入。FL 可以是建築標高，不必等於框在模型裡的 Z。
- 高程用 **FL 結構面**。不要填 FFL 完成面。LoopFlow 出圖記的是 FFL，兩者差一層面材厚度（約 3 到 5 公分）。兩邊不互相讀取；改樓高時兩邊都要改。

---

## 03　建築殼

**指令**：`RMModels`（先存檔，且已跑過 `RMStorey`）

```
! _-ScriptEditor _Run "E:\_GitHub\LoopFlow_Rhino-to-MEP-Sync\wip\commands\RMModels.py"
```

英文對話框一次問完：

1. **確認樓層** — 列出目前高程框、FL 與框的 Z。缺少、名稱或 FL 重複、或層高差與框的 Z 差對不上則擋住。
2. **排除記號**（預設 `//`；空白＝不排除）。圖層路徑含此文字者不匯出。
3. **最末端圖層** — 只列出沒有子層的圖層。**Select All**／**Select None**。第一次全不勾。同一個資料夾裡的整棟檔與單層檔會分開記住。
4. **IFC 類型** — 勾起來才匯出。下拉**預設** `IfcPlate`。天花選 `IfcCovering`。牆／板／柱／樑／樓梯請改成對應類型。舊存的 Proxy 會顯示成 Plate。要藏請取消勾選。
5. **幾何類別** — 顯示數量；Point／Curve 預設不勾。
6. **網格密度** — 粗／中／細，預設中。

底部按鈕：

- **Save Config** — 立刻寫這個檔的面板，對話框不關
- **Load Config** — 讀回這個檔上次的紀錄
- **Publish** — 先寫面板再出 IFC
- **Cancel**

成功後寫入 `models/R2M.ifc`。失敗不會蓋掉上次成功的檔。來源 Rhino 檔會回到執行前的狀態。

發布時：

- 只有**嚴格落在該層高程框內**的物件才匯出；碰到框線擋住；框外同層跳過；低於最低層跳過。
- Worksession 外參不會被包進建築 IFC。
- 過半物件仍是 Proxy 時，指令列會警告：Archicad 可能不顯示這些件。
- 產品預設檔名永遠是 `R2M.ifc`。若同一專案要留整棟與單層兩份，請自己另存複本改名。
- IFC 長度單位是**公分**。Revit 畫面仍常以公尺顯示樓層標高（例如 755 公分顯示成 8 公尺），這是 Revit 進位，不是檔寫錯。
- 每次成功發布會把**高度校正值**寫進同一份 `config.json`（整棟與單層共用；最後一次發布的那份會蓋掉前一次）。

---

## 04　BIM 收檔

BIM 端沒有 LoopFlow。建築殼是**參考**，不是給對方接手編輯的模型。

**Archicad（已測）**

1. **檔案 → 開啟**，把 `R2M.ifc` 當新檔。
2. 不必刪任何預設 Story。
3. **不要 Merge。** Merge 非整棟檔時，可能把 IFC 第 0 層對到 Ground Floor。
4. 不要 Update 進既有範本（會留下刪不掉的 Ground Floor）。

單層檔請連跨層物件碰到的那一層框一起畫進去再發布，開啟才完整。

**Revit（已測）**

1. Rhino `RMModels` 匯出 IFC。
2. Revit **Link IFC**（不要 Open、不要 Import）。
3. 依 IFC 框線高程，手動建立同高 Level（範本 Level 0／1 會留下）。
4. **View → Plan Views → Floor Plan**，讓該 Level 出現在 Project Browser → Floor Plans。

天花在 Rhino 請選 `IfcCovering`。未改下拉會寫成 `IfcPlate`。仍選 Proxy 的件 Archicad 常不顯示。

---

## 05　幾何外參與高度校正

**指令**：`RMInbound`（空白檔即可，不要求已存檔）

```
! _-ScriptEditor _Run "E:\_GitHub\LoopFlow_Rhino-to-MEP-Sync\wip\commands\RMInbound.py"
```

### 高度校正是什麼

BIM 裡的樓層高度是 FL（例如 3F＝1060 公分）。Rhino 工作檔常把那一層畫在模型自己的 Z（例如框在 0）。兩邊差一個固定值。

`RMModels` 把這個差值寫進 `config.json` 的 `elevation_shift`。`RMInbound` 把回來的每個頂點改成「IFC 世界 Z − 這個差值」，讓牆／管對上 Rhino 天花，而不是停在建築標高數字上。

- 同一資料夾的整棟與單層**共用**這份校正值。要對單層做 Inbound，請先對單層跑過 `RMModels`。
- 沒有這個欄位就停，不猜 0。
- XY 不平移。

Archicad 牆與 Revit 牆回檔，高度校正都已通過。真實風管／水管尚未測。

### 從 Archicad 出牆（已測；不是風管／水管）

1. 依上一節把建築殼 IFC **當新檔開啟**。
2. 在該檔畫牆（測試用；真實作業畫 3D 風管或水管）。
3. 用 Archicad **內建** IFC 匯出：**IFC4**；只出選取物件；座標不要另做偏移。
4. 測檔：`wip/fixtures/spike/ac_wall.ifc`。

### 從 Revit 出牆（已測；不是風管／水管）

1. 依上一節連結建築殼 IFC，自建 Level 並開 Floor Plan。
2. 在 3F、4F 各建 wall。
3. 選取要匯出的物件，**File → Export → IFC (IFC4)**。
4. 測檔：`wip/fixtures/spike/revit_wall.ifc`。

### Rhino

1. 開一個**空白 `.3dm`**，單位設成與工作檔相同。
2. 貼上上面的 `RMInbound` 那一行，選剛匯出的 IFC。確認文件單位。空白檔還會請你選工作檔旁的 `config.json`。
3. **手動**另存成 `.3dm`（建議工作檔旁 `_LoopFlow_Config/loopflow_R2M/inbound/`，固定檔名）。
4. 回工作檔**手動**用 Worksession 掛上該 `.3dm`。

指令**不**寫檔、**不**另存、**不**掛載。匯入的網面**不鎖定**。掛成 Worksession 後在工作檔裡仍是外參，可以抓點、當對圖依據，不要當出圖來源。

管線更新時：重跑 Rhino 1 到 3，覆寫同一個 `.3dm`，再到 Worksession 管理員按 Refresh。固定檔名才能這樣更新。

第一版**沒有**碰撞檢查，也不把 BIM 衝突點畫成 Rhino 點。人看外參網面與天花重疊即可。

---

## 06　不要做的事

- 不要在指令列直接打 `RMOpen` 這幾個名字（尚未註冊成 Rhino 指令）；請貼 ScriptEditor 那一行。
- 不要把外參幾何拿去出圖或當 Tag 來源。
- 不要用手改 `R2M_FL`。
- 不要為了迎合 Merge／範本而在 IFC 裡補一層 0 m 空樓層。
- 不要把建築殼轉成 BIM 原生元素再各自修改；設計變更一律回 Rhino。
- 不要把整棟建築或 2D 圖一併當成外參 IFC 送回 Rhino。
- 不要在整棟剛發布完、校正值已變成 0 時，直接對單層做 Inbound。
