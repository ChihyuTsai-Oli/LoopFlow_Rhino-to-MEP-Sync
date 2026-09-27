# 開發期工具列

`LoopFlow_R2M.rui` 由 `wip/tools/build_toolbar_rui.py` 產生。不要手改裡面的 GUID。

四顆按鈕（Open／Storey／Models／Inbound）目前跑 ScriptEditor，指向 `E:\\_GitHub\\LoopFlow_Rhino-to-MEP-Sync\\wip\\commands\\`。正式 yak 登錄指令後再改成 `! _RMOpen` 等。

圖示：`LoopFlow_R2M.svg` 是工具列分頁圖，`R2M_Open.svg`／`R2M_Storey.svg`／`R2M_Models.svg`／`R2M_Inbound.svg` 是按鈕。寫進 rui 後這五個 SVG 會刪掉；要換圖就再放回來重跑產生器。
