# PROJ-444: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-18 | Project initialized | Starting point for Post-refactor residue: Data + Facade layer (Bucket A) |
| 2026-05-18 | Phase 1 Task 1.3 (F-A-015 + F-A-016) deferred to a future cross-bucket coordination phase | The typed `BuildQueueItemDTO` retype requires migrating ~6 UI reader sites in `game/ui/screens/empire_build_queue_formatter.py`, `game/ui/panels/build_queue_drag_handler.py`, and several `tests/unit/ui/**` + `tests/integration/ui/**` files. Those paths are PROJ-446-owned per the Phase 1 file-ownership partition; touching them now would violate the cross-bucket boundary. A minimal "immutability-only" variant (wrap in `tuple(MappingProxyType(...))` without typed dataclass) would still need `dto.construction_queue[N][key]` accessors to keep working (MappingProxyType supports `__getitem__`, so the UI readers stay green) — but adding F-A-016's typed dataclass without UI migration is unsafe. Recommend bundling F-A-015 + F-A-016 into PROJ-444 Phase 2 (or a joint phase with PROJ-446) once the UI partition lifts. |
| 2026-05-18 | Phase 1 Task 1.14 (F-A-032 `stars_cache_new` rename) deferred to a cross-bucket cleanup pass | The field is read/written by `game/ui/screens/star_list_filters.py` (PROJ-446 territory) and `tests/performance/test_strategy_panel_regression.py` (outside any current partition). Renaming the field requires editing those non-data/facade callers, which would violate the Phase 1 ownership partition. CLAUDE.md forbids back-compat aliases, so a soft-rename is not an option. The rename is pure polish — no functional impact — and is safe to bundle with the next coordinated touch of the UI star-list path. |
