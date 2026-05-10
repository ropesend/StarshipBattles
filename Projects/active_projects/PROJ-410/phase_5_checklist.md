# Phase 5: Final Verification + Doc Updates

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-410 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State
> 4. Update `Projects/projects_index.md`

**Status:** Not Started
**Objective:** Full-suite verification, smoke timing for repeat-open `<0.5s` budget, and Pattern #11 doc extension.

**Hard constraints:**
- All static guards green.
- Repeat-open wall-clock `<0.5s` at baseline resolution (preserves PROJ-376 phase 2 budget).
- Pattern doc gets a verified-date stamp bump only if substantive content changed.

---

## Tasks

### Task 5.1: Full sharded test suite [Simple]
**File:** (no edit)
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Run the canonical full suite. All shards pass, 0 failures, 0 errors.
- [ ] Test count is at least 19828 (baseline) plus the net additions from Phase 1 (~7–9 new tests, no removals).
- [ ] Note the wall time for the audit log if it changed materially from the 116 s baseline.

**Notes:**

---

### Task 5.2: Static guards + perf-lock tests [Simple]
**File:** (no edit)
**Tests:** `pytest tests/static_guards/ tests/unit/ui/components/table/test_virtual_table.py::TestRowPoolReuseGuard tests/unit/ui/screens/test_strategy_build_queue_manager.py::TestSecondClickReuse tests/unit/ui/screens/test_build_queue_screen_lifecycle.py -v`

- [ ] `tests/static_guards/test_facade_bypass_guard.py` — green.
- [ ] `TestRowPoolReuseGuard` — all 4–5 tests green; widget `.kill()` count assertions still hold.
- [ ] `TestSecondClickReuse` — green; manager reuse preserved.
- [ ] `test_request_close_*` lifecycle tests — green.

**Notes:**

---

### Task 5.3: Smoke timing — repeat-open `<0.5s` [Simple]
**File:** (no edit) — manual smoke test
**Tests:** Manual.

- [ ] Run the game (`python -m game.app` or current entry point), open build queue, switch yards 5 times. Confirm wall-clock per-switch is `<0.5s` at baseline 2560×1600 resolution.
- [ ] If timing regresses, profile per Performance Analyst's notes:
  - Cost of `invalidate_widget_caches()`: expected 1–2 ms.
  - Cost of next `update_visible_rows()` re-render: expected 6–15 ms.
  - Cumulative per yard switch: expected 7–17 ms.
- [ ] If profile shows the B-hook redundancy is significant (>10 ms cumulative across rapid queue mutations), file a follow-up project note in `decisions.md` for adding a generation counter on `BuildQueueQueueDataSource` (deferred per Decision 8).

**Notes:**

---

### Task 5.4: Update `docs/02_PATTERNS.md` Pattern #11 [Simple]
**File:** `docs/02_PATTERNS.md` Pattern #11 (Surface Caching)
**Tests:** None (doc only).

- [ ] Add a short subsection or note: "When a cached widget pool is reused for *different content* (e.g. yard switch in `BuildQueueScreen`), expose an `invalidate_widget_caches()` method that nulls per-cell caches without `.kill()`-ing pool widgets. Pair with an ephemeral `_data_identity_dirty` flag that is cleared after one re-render so subsequent frames keep the early-return perf optimization."
- [ ] Reference `game/ui/components/table/virtual_table.py::invalidate_widget_caches` as the canonical example.
- [ ] Bump `> **Last verified:**` line below the H1 to today's date with a one-sentence summary of the change.
- [ ] Stay within Pattern #11; do NOT introduce a new numbered pattern.

**Notes:**

---

### Task 5.5: Close-out updates [Simple]
**File:** `Projects/projects_index.md`, `Projects/active_projects/PROJ-410/plan.md` (Quick Status + Current State), `Projects/active_projects/PROJ-410/decisions.md`
**Tests:** None.

- [ ] Update `Projects/projects_index.md` row for PROJ-410 to `Complete` with completion date.
- [ ] Update `plan.md` Quick Status table — all phases `Complete`.
- [ ] Update `plan.md` Current State to reflect completion.
- [ ] Add final entries to `decisions.md` if any decisions were made during implementation that aren't already captured.
- [ ] If profile note from Task 5.3 warrants a follow-up project, leave a stub line in `Projects/projects_index.md` (or a TODO note in `decisions.md`).

**Notes:**

---

## Phase Completion Checklist

When all tasks above are done:

- [ ] All Phase 5 task checkboxes are checked.
- [ ] Full sharded suite green; no new failures.
- [ ] All static + perf-lock guards green.
- [ ] Repeat-open timing acceptable (`<0.5s`).
- [ ] `docs/02_PATTERNS.md` Pattern #11 updated (if substantive change).
- [ ] `Projects/projects_index.md` reflects completion.
- [ ] User verification of the QA scenarios from `findings/build_queue_caching_overhaul.md` (open same-yard twice; switch yards; end turn → next player; load saved game; ship-yard ↔ planetary-yard).
- [ ] Update status at top of this file to `Complete`.
- [ ] Run `python Projects/scripts/validate_phase.py PROJ-410 5` — output PASSED.
- [ ] Final user "Project Complete" sign-off.
