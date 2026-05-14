# PROJ-414: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-13 | Project initialized | Starting point for Legacy removal — pathfinding.py shim (PROJ-376) (2026-05-13) |
| 2026-05-13 | Bundled findings from `2026-05-13_194106_legacy-audit` by removal cluster `pathfinding_shim (PROJ-376)` per user direction | Bundling driven by removal cluster (one project per system being eradicated) rather than severity to maximize deletion-PR coherence; full bundling discussion in findings/bundling_decisions.md |
| 2026-05-14 | Phase 1 split into 1a (audit), 1b (migrate), 1c (delete) after codex consult | Single-phase "19 callers + delete" was not executable: the checklist listed no concrete strategy for ~30 patch sites, no guard-test deletion, and no per-site intercept_calculator migration plan. Phase split enforces correct TDD ordering (identify failing tests first per group) and prevents silent test-isolation regression (the false-confidence risk PROJ-377 documented). |
| 2026-05-14 | `test_pathfinding_shim_scope.py` must be deleted in Phase 1c (not updated) | The guard was written to prevent accidental drift; its purpose ends when the shim is gone. Updating it to allow deletion would be contradictory. Deletion is the correct action. |
| 2026-05-14 | PROJ-414 supersedes PROJ-377's "no deletion" decision | PROJ-377 deferred deletion because of the test-patch complexity. PROJ-414's Phase 1a audit will produce a complete patch-site map, making the migration feasible. Pattern #36 says shims are temporary; permanent-shim is a policy violation. |
