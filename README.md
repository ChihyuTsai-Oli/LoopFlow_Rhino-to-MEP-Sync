# LoopFlow Rhino to MEP Sync (R2M)

Rhino publishes an architectural-shell IFC for Revit / Archicad. Those tools publish MEP IFC back as **locked reference geometry** in Rhino. Design changes stay in Rhino. Exchange format is **IFC only**.

Formal specs (Traditional Chinese) live in [`docs/`](docs/). Source is in [`src/`](src/). Development-period Rhino entries: [`commands/RMModels.py`](commands/RMModels.py), [`commands/RMInbound.py`](commands/RMInbound.py), [`commands/RMOpen.py`](commands/RMOpen.py).

---

Rhino 發布建築殼 IFC 給 Revit／Archicad；BIM 端把管線 IFC 送回 Rhino 當**鎖定參考**。設計判斷只在 Rhino。交換只使用 IFC。

實作規格見 [`docs/`](docs/)。原始碼見 [`src/`](src/)。開發期 Rhino 入口：[`commands/RMModels.py`](commands/RMModels.py)、[`commands/RMInbound.py`](commands/RMInbound.py)、[`commands/RMOpen.py`](commands/RMOpen.py)。

## License

MIT. See [LICENSE](./LICENSE).
