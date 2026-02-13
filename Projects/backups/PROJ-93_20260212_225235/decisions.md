# PROJ-93: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-10 | Project initialized | Cleanup from code review — two protocol `layers` annotations still use `Dict[str, Any]` instead of `Dict[LayerType, LayerData]` |
| 2026-02-10 | Import `LayerType` directly, `LayerData` under TYPE_CHECKING | LayerType is in `game.core.constants` (same layer as protocols). LayerData is in `game.simulation.entities` (cross-layer) — must use TYPE_CHECKING guard. No circular deps: simulation never imports protocols.py. |
| 2026-02-10 | Use string forward references `'LayerType'`, `'LayerData'` in annotations | @runtime_checkable protocols execute at import time. String refs prevent runtime import errors when LayerData isn't available outside TYPE_CHECKING block. |
| 2026-02-10 | Keep IResourceHolder (don't delete as dead code) | Created intentionally by PROJ-91 to formalize resource access contract. Has no external consumers yet but is planned infrastructure. |
