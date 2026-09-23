# LoopFlow R2M WIP

此資料夾是 R2M 的 Git 追蹤開發工作區。給使用者看的說明在 repo 根 `docs/`（`USER_GUIDE`／`COMMANDS`）。

```text
wip/
  docs/           # 實作規格、資料契約、工作流程、進度
  src/            # 產品原始碼
  commands/       # 開發期 ScriptEditor 入口
  tests/          # 系統 Python 單元測試
  tools/          # 針刺與決策表工具
  fixtures/       # 可提交、輕量且不含私人資料的測檔
```

單元測試在本資料夾執行：`python -m unittest discover -s tests -t .`

IfcOpenShell 本機快取在 `wip/.vendor/`（gitignore）。大型 Rhino／BIM 工作檔不放進 repo，路徑見工作區根目錄 `工作檔路徑.md`。
