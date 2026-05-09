# Review Scope: PROJ-384 — Deprecated *_static methods deletion (167 LOC removed)
**Type:** code (delegated by Claude Code)
**Request ID:** req_20260509_004717_dde81f
**Scope:** 
- `game/simulation/components/ability_manager.py` (341 → 285 LOC, -56)
- `game/simulation/components/modifier_manager.py` (330 → 219 LOC, -111)
- `tests/unit/simulation/components/test_ability_manager.py` (3 test methods migrated to instance API)
- `tests/unit/simulation/components/test_modifier_manager.py` (comment re-attribution only)
- Reference: `Reviews/results/2026-05-07_220621_legacy-audit/`
- Reference: `Projects/active_projects/PROJ-384/findings/verification_report.md`

**Context:** Fourth of 11 sequential PROJ runs (Stage 2 lead-off). PROJ-381 + PROJ-382 + PROJ-393 all merged ahead. PROJ-380 was originally scoped to delete the same ModifierManager statics; PROJ-384 supersedes that scope.

**Commit:** 6398bb1da
