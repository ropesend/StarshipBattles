# Review Scope: PROJ-373 build-queue latency phases 1, 3, 4 — cache correctness, lifecycle safety, theme scoping
**Type:** code (delegated by Claude Code)
**Request ID:** req_20260506_051906_ddfd29
**Scope:** Three commits on `feat/03c-phase-aware-execution`:
- `d68c39805` — Phase 1: validation cache on `BuildQueueController` (`game/ui/panels/build_queue_controller.py` + `tests/unit/ui/panels/test_build_queue_controller.py` ≥ 13 new cases)
- `aca743a25` — Phase 3: VirtualTable row-pool rebuild guard (`game/ui/components/table/virtual_table.py` + tests under `tests/unit/ui/components/table/`)
- `8df0b40e2` — Phase 4: scoped `@fast_panel` rectangle shape (`data/builder_theme.json` + `game/ui/screens/build_queue_panel_factory.py` + factory tests)

Notably NOT in scope: Phase 2 (BuildQueueScreen instance reuse) — deferred.

**Instructions:** Focus areas:
1. Phase 1 cache correctness — mtime fingerprint, lazy validator, reset_filters() reachability, test coverage of invalidation
2. Phase 3 row-pool rebuild guard — side-effect suppression, edge cases, profile-evidence defense
3. Phase 4 scoped @fast_panel — panel coverage, theme correctness, visual regression risk
4. Cross-cutting interactions and acceptance criterion
5. Phase 2 deferral hygiene in plan/decisions docs

**Context:** Wave A project 3 of 3. Phase 2 deferred due to pygame_gui lifecycle complexity. Three shipped phases deliver independent value but do not meet full <0.5s repeat-open acceptance criterion alone.
