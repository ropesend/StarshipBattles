# Phase 2: Dead functions (deprecated static methods)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-380 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete (superseded by PROJ-384)
**Objective:** Delete the 5 deprecated `ModifierManager` static methods identified by audit `2026-05-07_220215_audit_shrink` (DUP-X-05) while preserving the still-used internal helper `remove_modifier_inplace`.

> **Superseded by PROJ-384 (commit `6398bb1da`).** PROJ-384's full audit of `*_static` methods deleted **all 6** `ModifierManager` `*_static` methods including `remove_modifier_inplace` (which it confirmed had zero non-deprecated callers). PROJ-380's scope-reduction (preserve `remove_modifier_inplace`) was overtaken by PROJ-384's broader analysis. `grep -n "_static" game/simulation/components/modifier_manager.py` returns 0 hits, confirming all 6 methods are gone. No work remains in this phase.

---

## Tasks

### Task 2.1: Remove deprecated `*_static` methods from `ModifierManager` [Simple]
**File:** `game/simulation/components/modifier_manager.py`
**Tests:** `pytest tests/unit/simulation/components/test_modifier_manager.py` then `pytest tests/ --testmon`

Verification confirmed zero external callers of the 5 deprecated static methods across `game/`, `combat_lab/`, and `tests/`. Two of them call each other internally (`add_modifier_static` → `remove_modifier_inplace`; `get_stat_summary_static` → `get_all_effects_static`), so the deletions must go in together. `remove_modifier_inplace` is **not** marked deprecated and must remain — but recheck whether it has any non-deprecated caller before deciding to keep or also delete.

- [x] Re-grep `ModifierManager.remove_modifier_inplace` and bare `remove_modifier_inplace(` across `game/`, `combat_lab/`, `tests/` to confirm whether any non-deprecated code path still uses it; record the count in **Notes** before deleting anything — _Superseded by PROJ-384 (commit 6398bb1da) which deleted all 6 *_static methods. PROJ-380's scope-reduction (preserve `remove_modifier_inplace`) was overtaken by PROJ-384's full audit confirming zero callers._
- [x] Remove `add_modifier_static` (lines 223–251, ~29 LOC) — _Superseded by PROJ-384 (commit 6398bb1da)._
- [x] Remove `remove_modifier_static` (lines 253–259, ~7 LOC) — _Superseded by PROJ-384 (commit 6398bb1da)._
- [x] Remove `get_modifier_static` (lines 276–285, ~10 LOC) — _Superseded by PROJ-384 (commit 6398bb1da)._
- [x] Remove `get_all_effects_static` (lines 287–294, ~8 LOC) — _Superseded by PROJ-384 (commit 6398bb1da)._
- [x] Remove `get_stat_summary_static` (lines 296–330, ~35 LOC) — _Superseded by PROJ-384 (commit 6398bb1da)._
- [x] If the regrep above returned zero non-deprecated callers, also remove `remove_modifier_inplace` (lines 261–274, ~14 LOC); otherwise keep it and add a one-line comment noting it is the surviving internal helper — _Superseded by PROJ-384 (commit 6398bb1da) which confirmed zero callers and deleted it._
- [x] Run `pytest tests/unit/simulation/components/test_modifier_manager.py` — _Verified green by PROJ-384 closeout._
- [x] Verify: full sharded suite green; LOC delta ≈ −89 (preserving `remove_modifier_inplace`) or ≈ −103 (if also removed) — _PROJ-384 reports −111 LOC for modifier_manager.py (330 → 219)._

**Notes:** Audit's claim of 100 LOC reclaim assumed the entire 221–330 block could be removed. Independent verification reduced the scope: 5 of 6 candidate methods are safe to delete; the sixth is an internal helper. Final LOC reclaim depends on the regrep result above. (DUP-X-05, scope-reduced) — **OVERRIDDEN: PROJ-384 deleted all 6, total −111 LOC, sharded suite green.**

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase

_Source audit: `Reviews/results/2026-05-07_220215_audit_shrink/`. See [findings/source_audit.md](findings/source_audit.md) for the link._
