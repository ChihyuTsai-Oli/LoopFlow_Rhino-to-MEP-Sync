# LoopFlow R2M 使用說明總覽

> 指令名稱已凍結：`RMOpen`、`RMStorey`、`RMModels`、`RMInbound`。還沒有 Package Manager 套件；開發期可開工具列。畫面為英文。
>
> 一分鐘理解怎麼運作。按鈕與逐步操作見 [指令逐項說明](./COMMANDS_zh-TW.md)。產品介紹見 [專案主頁](../README_zh-TW.md)。

## 核心邏輯：Rhino 出殼，BIM 畫管，再當外參回來

**設計判斷只在 Rhino。** BIM 端不裝 LoopFlow。交換只使用 IFC。

1. **先把 `.3dm` 存檔。** 未存檔就不能發布。設定與交換檔都放在這份檔案旁邊。
2. **先登記樓層，再發布建築殼。** `RMStorey` 把高程框編成樓層；`RMModels` 寫出 `models/R2M.ifc`（長度單位公分）。
3. **BIM 收這份 IFC**（Archicad：檔案 → 開啟當新檔，不要 Merge。Revit：連結 IFC，再依框線高程自建 Level 並開 Floor Plan），在裡面畫 3D 幾何。BIM 裡的高度跟著高程框填的 FL。Bonsai 與 Revit、Archicad 一樣用 IFC 作業，本產品**不測 Bonsai**。
4. **幾何 IFC 回到 Rhino（高度校正）。** BIM 世界座標仍是建築標高。`RMInbound` 會把每個頂點的高度扣回 Rhino 模型（不是停在 FL 數字上），讓回來的牆／管對上天花。另存與掛 Worksession 都手動。
5. **看著外參改原天花／牆／板，再跑 Models。**

沒有相機、燈光、即時連線。系統不會自己往下一通道繼續跑。

## 專案以資料夾為單位

已存檔的 `.3dm` 所在資料夾就是作業資料夾。LoopFlow 會在同一層建立：

```text
_LoopFlow_Config/loopflow_R2M/
  models/      ← R2M.ifc（產品預設檔名；整棟／單層請發布後立刻改名）
  inbound/     ← 建議把外參 .3dm 放這裡（程式不強制、也不代存）
  config.json  ← 含高度校正值 elevation_shift（最後一次 RMModels 寫入）
  r2m.log
```

同一資料夾裡的整棟與單層**共用**這份 `config.json`。要對單層做 Inbound，請先對單層跑過 `RMModels`，校正值才會是單層的（整棟通常是 0）。

換電腦時把整個專案資料夾一起搬即可。Worksession 的 `.rws` 是個人檔，不在 `.3dm` 裡，換電腦要重掛一次。這不是壞掉。

## 兩端怎麼對

| 你要做的事 | Rhino | BIM |
|---|---|---|
| 登記樓層 | `RMStorey` | — |
| 建築殼 | `RMModels` | Archicad：**開啟 IFC 當新檔**（已測）。Revit：**連結 IFC**，再自建同高 Level 並開 Floor Plan（已測）。Bonsai 同為 IFC 作業環境，**不測** |
| 幾何外參（含高度校正） | `RMInbound` → 手動另存 → 手動掛 Worksession | BIM 匯出 **IFC4**、只出選取物件。Archicad 牆與 Revit 牆回檔高度已過；真實風管／水管尚未測 |
| 看設定與說明 | `RMOpen` | — |

BIM 端沒有 LoopFlow 按鈕。

## 幾個要先懂的名詞

| 名詞 | 意思 |
|---|---|
| **高程框** | 你畫的水平封閉曲線，一個樓層一個，畫在該層自己的高度。框必須比外牆再大一圈；貼齊邊會被擋住。 |
| **FL** | 結構面高程。不要填 FFL 完成面。LoopFlow 出圖記的是 FFL，混用會差一層面材厚度。 |
| **高度校正** | BIM 依 FL 畫；Rhino 模型常把樓層畫在自己的 Z。`RMInbound` 用 `config.json` 的 `elevation_shift` 把回來的幾何扣回模型。 |
| **整棟／非整棟** | `RMStorey` 選 WholeBuilding 或 PartialStoreys。只畫其中幾層時不要硬找 1F、RF。 |
| **IfcPlate／IfcCovering** | 未改類型的圖層寫成 Plate。天花請改 Covering。仍用 Proxy 的件在 Archicad 常看不見。 |
| **Worksession 外參** | 回來的 `.3dm` 掛進工作檔後是外參，可以抓點、當對圖依據。`RMInbound` **不鎖定**網面。發布建築殼時會自動排除外參。 |

## 失敗時會停在哪

- 未存檔：`RMModels`／`RMOpen` 停止。`RMStorey`／`RMInbound` 不要求已存檔。
- 沒有高程框、樓層名稱或 FL 重複、或層高與框的高度對不上：不發布。
- 物件碰到框線：擋住。框外同層跳過。低於最低層跳過（指令列會列出件數）。
- 匯出取消、失敗或中斷：上次成功的 `R2M.ifc` 不會被半套檔蓋掉。來源 Rhino 檔會回到執行前的狀態。
- `config.json` 沒有 `elevation_shift`：`RMInbound` 停止，不猜 0。

## 想知道怎麼按

這一頁只講邏輯。指令列貼上、樓層怎麼畫、Archicad／Revit 怎麼開檔，見 [指令逐項說明](./COMMANDS_zh-TW.md)。
