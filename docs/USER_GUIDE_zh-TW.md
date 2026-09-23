# LoopFlow R2M 使用說明總覽

> **開發草稿。** 指令名稱尚未凍結。還沒有套件或工具列。
>
> 一分鐘理解怎麼運作。按鈕與逐步操作見 [指令逐項說明](./COMMANDS_zh-TW.md)。產品介紹見 [專案主頁](../README_zh-TW.md)。

## 核心邏輯：Rhino 出殼，BIM 畫管，再當外參回來

**設計判斷只在 Rhino。** BIM 端不裝 LoopFlow。交換只使用 IFC。

1. **先把 `.3dm` 存檔。** 未存檔就不能發布。設定與交換檔都放在這份檔案旁邊。
2. **先登記樓層，再發布建築殼。** `RMStorey` 把高程框編成樓層；`RMModels` 寫出 `models/R2M.ifc`。
3. **BIM 當新檔開啟這份 IFC**（Archicad：檔案 → 開啟；不要 Merge），在裡面畫 3D 管線。
4. **管線 IFC 回到 Rhino。** `RMInbound` 只在目前文件建鎖定網面；另存與掛 Worksession 都手動。
5. **看著外參改原天花／牆／板，再跑 Models。**

沒有相機、燈光、即時連線。系統不會自己往下一通道繼續跑。

## 專案以資料夾為單位

已存檔的 `.3dm` 所在資料夾就是作業資料夾。LoopFlow 會在同一層建立：

```text
_LoopFlow_Config/loopflow_R2M/
  models/      ← R2M.ifc（產品預設檔名；整棟／單層可另存複本）
  inbound/     ← 建議把管線外參 .3dm 放這裡（程式不強制、也不代存）
  config.json
  r2m.log
```

換電腦時把整個專案資料夾一起搬即可。Worksession 的 `.rws` 是個人檔，不在 `.3dm` 裡，換電腦要重掛一次。這不是壞掉。

## 兩端怎麼對

| 你要做的事 | Rhino | BIM |
|---|---|---|
| 登記樓層 | `RMStorey` | — |
| 建築殼 | `RMModels` | **開啟 IFC 當新檔**（Archicad 已測）。Revit 預期用「連結 IFC」，尚未測 |
| 管線外參 | `RMInbound` → 手動另存 → 手動掛 Worksession | 內建匯出 **IFC4**、只出 3D 管線。真實管線匯出尚未測 |
| 看設定與說明 | `RMOpen` | — |

BIM 端沒有 LoopFlow 按鈕。

## 幾個要先懂的名詞

| 名詞 | 意思 |
|---|---|
| **高程框** | 你畫的水平封閉曲線，一個樓層一個，畫在該層自己的高度。框必須比外牆再大一圈；貼齊邊會被擋住。 |
| **FL** | 結構面高程。不要填 FFL 完成面。LoopFlow 出圖記的是 FFL，混用會差一層面材厚度。 |
| **整棟／非整棟** | `RMStorey` 選 WholeBuilding 或 PartialStoreys。只畫其中幾層時不要硬找 1F、RF。 |
| **IfcPlate／IfcCovering** | 未改類型的圖層寫成 Plate。天花請改 Covering。仍用 Proxy 的件在 Archicad 常看不見。 |
| **Worksession 外參** | 管線 `.3dm` 掛進工作檔後不能編輯，但可以抓點、當對圖依據。發布建築殼時會自動排除外參，避免把管線送回 BIM。 |

## 失敗時會停在哪

- 未存檔：`RMModels`／`RMOpen` 停止。`RMStorey`／`RMInbound` 不要求已存檔。
- 沒有高程框、樓層名稱或 FL 重複、或層高與框的高度對不上：不發布。
- 物件碰到框線：擋住。框外同層跳過。低於最低層跳過（指令列會列出件數）。
- 匯出取消、失敗或中斷：上次成功的 `R2M.ifc` 不會被半套檔蓋掉。來源 Rhino 檔會回到執行前的狀態。

## 想知道怎麼按

這一頁只講邏輯。指令列貼上、樓層怎麼畫、Archicad 怎麼開檔，見 [指令逐項說明](./COMMANDS_zh-TW.md)。
