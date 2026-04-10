# PROJ-238: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-03-29 | Project initialized | Order System Unification & Planet Orders UI |
| 2026-03-29 | Unified OrderType enum (merge planet orders) | Single enum for all entity orders. Fleets, planets, future stations share types where applicable. |
| 2026-03-29 | Space stations = immobile fleets | No new entity type needed. Stations are fleets with no strategic movement. Simplifies order unification. |
| 2026-03-29 | Generic entity_id + entity_type for targeting | Matches existing BuildEntityType pattern. Decouples orders from entity class imports. |
| 2026-03-29 | Full rename (not wrapper layer) | User explicitly wants clean code — planet order code should not reference "fleet" anywhere. |
| 2026-03-29 | Incremental rename with testing | Each rename batch verified by full test run. Prevents silent regressions across 94+ files. |
| 2026-03-29 | H key for shield toggle | Avoids conflict with existing fleet hotkeys (M=move, J=join, C=colonize, T=transfer, W=warp). |
| 2026-03-29 | Same OrdersWindow for fleets and planets | Generalize FleetOrdersWindow to accept IOrderable entity. Callback pattern already supports this. |
| 2026-03-29 | Shared orders: toggle components, self-destruct, warp points, launch fighters, cargo ops | User confirmed these should work on both fleets and planets (future implementation, enum merged now). |
