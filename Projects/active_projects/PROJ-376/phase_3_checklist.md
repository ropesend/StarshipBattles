# Phase 3: Acceptance + close-out (PROJ-373 review hygiene + re-profile)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-376 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Depends on:** phase_2
**Review Mode:** standard
**Files (planned):**
- `game/ui/panels/build_queue_controller.py` (update `reset_filters` comment + add HFS+ comment per MIN-002)
- `game/ui/components/table/virtual_table.py` (docstring only — MIN-003)
- `tests/unit/ui/components/table/test_virtual_table.py` (column-config-change test — MIN-005)
- `Projects/active_projects/PROJ-373/plan.md` (MAJ-003 + MAJ-004 backfill)
- `Projects/active_projects/PROJ-376/findings/post_proj376_profile.md` (NEW — re-profile evidence)
**Objective:** Re-profile build-queue opens and confirm `< 0.5 s` repeat-open. Activate `BuildQueueController.reset_filters()` documentation (live since PROJ-376). Close out PROJ-373 review residual MIN findings (MIN-001, MIN-002, MIN-003, MIN-005) and PROJ-373 plan.md backfill (MAJ-003, MAJ-004).

---

## Pre-flight

- [ ] Confirm Phase 2 is `verified` per `phase_dag.py status`.
- [ ] Re-read `Reviews/results/2026-05-06_051908_code_proj-373-build-queue-latency-phases-1-3-4-cache-co_req-req_20260506_051906_ddfd29/report.md` MIN-001, MIN-002, MIN-003, MIN-005, MAJ-003, MAJ-004, INFO-003, INFO-008 sections.
- [ ] Confirm `python Tools/profile_game/profile_game.py` works on this machine (output goes to `AgentCoordination/Scratchpad/reports/profiles/`).

---

## Tasks

### Task 3.1: Re-profile build queue [Medium]
**Tests:** `python Tools/profile_game/profile_game.py`

- [ ] Repro: launch game; open build queue at home planet 3× in a row; quit normally. Match PROJ-373's `findings/profile_summary.md` repro exactly.
- [ ] Open the resulting HTML in a browser; capture per-click `_open_build_queue` cumulative time.
- [ ] **First open:** expect ~3.7-4.0 s. (PROJ-373 Phase 1 saves ~2.2 s of validation; Phase 4 `@fast_panel` saves ~3 s of rasterization. Net first-open: ~6.9 s baseline – 2.2 – 3.0 ≈ 1.7-3.7 s, depending on which costs were measured in baseline.)
- [ ] **Repeat opens:** expect well under **500 ms** wall-clock per click. Acceptance bar.
- [ ] If repeat open exceeds 500 ms: investigate. Likely culprits per design.md / PROJ-373 review: (a) `_refresh_items_list()` re-instantiates design buttons (renderer kills + recreates `items_scrollable` children every refresh — see `build_queue_renderer.py:62-65`); (b) `_refresh_queue_display()` row-pool guard didn't trigger (check fingerprint); (c) `manager.update(0)` after hide is too aggressive. Diagnose + remediate before closing out.
- [ ] Write `Projects/active_projects/PROJ-376/findings/post_proj376_profile.md` capturing: first-open time, 3 repeat-open times, mean repeat-open, top-3 hot leaves on a repeat open, before/after table vs. PROJ-373 baseline.

**Notes:**

### Task 3.2: Activate `BuildQueueController.reset_filters()` comment [Simple]
**File:** `game/ui/panels/build_queue_controller.py:260-268`
**Tests:** existing `tests/unit/ui/panels/test_build_queue_controller.py`

- [ ] Edit the docstring at lines 261-265:
  ```python
  def reset_filters(self) -> None:
      """Reset category and role filters to their defaults.

      PROJ-376 (continuation of PROJ-373 Phase 1): called from
      `BuildQueueScreen.open_for_yard` when the screen is reused
      across yard switches. Live as of PROJ-376 Phase 1.
      Does NOT call `on_queue_changed` — caller decides when to refresh.
      """
  ```
  (Replace "Phase 2 prerequisite ... Dead code until then" wording — the method is now live.)
- [ ] **Verify:** existing `test_reset_filters_*` tests still pass.

**Notes:** Closes PROJ-373 review MIN-001.

### Task 3.3: Add HFS+ mtime resolution comment [Simple]
**File:** `game/ui/panels/build_queue_controller.py:201-216`
**Tests:** existing tests (no behavior change)

- [ ] Add a one-line comment near line 213 (right above `return os.stat(path).st_mtime_ns`):
  ```python
  # PROJ-373 review MIN-002: legacy HFS+ has 1-second mtime resolution.
  # Two saves within the same second on HFS+ produce identical fingerprints
  # → cache returns stale validation. Self-corrects on next open per
  # design.md alternative F (false invalidation is harmless).
  ```
- [ ] **Verify:** lint clean.

**Notes:** Closes PROJ-373 review MIN-002.

### Task 3.4: Document `rebuild_row_pool` layout-pass dependency [Simple]
**File:** `game/ui/components/table/virtual_table.py`
**Tests:** existing virtual-table tests

- [ ] Find the public `rebuild_row_pool()` method docstring; add:
  ```
  Note: Reads ``_list_view_panel.get_relative_rect()`` for dimension
  fingerprinting. Callers MUST ensure pygame_gui has completed its
  layout pass before calling — typically by running ``manager.update(0.0)``
  beforehand. PROJ-373 review MIN-003.
  ```
- [ ] **Verify:** docstring renders sensibly; no tests break.

**Notes:** Closes PROJ-373 review MIN-003.

### Task 3.5: Add column-config-change test [Simple]
**File:** `tests/unit/ui/components/table/test_virtual_table.py`
**Tests:** `pytest tests/unit/ui/components/table/test_virtual_table.py::TestRowPoolReuseGuard -v`

- [ ] In `TestRowPoolReuseGuard`, add `test_column_config_change_triggers_rebuild`:
  - Construct a `VirtualTable` with a 2-column `column_manager`.
  - Call `rebuild_row_pool()`; capture pool widget identity.
  - Mutate `column_manager.get_visible_columns()` to return 3 columns (or use the column-manager's API to add a column).
  - Without changing panel dimensions, call `rebuild_row_pool()` again.
  - Assert: old `bg.kill()` called for each row; new pool has 3-column widgets.
- [ ] **Verify:** test passes (the PROJ-373 Phase 3 guard already includes column fingerprint per `virtual_table.py:163-174`, so this should pass directly — confirms MIN-005 coverage).

**Notes:** Closes PROJ-373 review MIN-005.

### Task 3.6: Backfill PROJ-373 plan.md (MAJ-003 + MAJ-004) [Simple]
**File:** `Projects/active_projects/PROJ-373/plan.md`

- [ ] Update Quick Status row 17 (Phase 1 row) — replace:
  ```
  | 1. Cache `_validate_designs` results (effective only within a single open until Phase 2 lands) | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
  ```
  with:
  ```
  | 1. Cache `_validate_designs` results | Complete (cross-open value live since PROJ-376 Phase 2) | [phase_1_checklist.md](phase_1_checklist.md) |
  ```
- [ ] Update detailed Phase 2 section (lines 105-108) — replace `**Status:** Deferred — see [decisions.md](decisions.md) for rationale. Do not implement; revisit in a follow-up project where a focused single-purpose effort can untangle the pygame_gui lifecycle, modal stack, FEAT-17 pause-button, and per-yard reference graph.` with:
  ```
  **Status:** Deferred → Completed in PROJ-376 (2026-05-XX). See `Projects/active_projects/PROJ-376/` for the lifecycle refactor that delivered Phase 2's instance-reuse goal.
  ```
- [ ] Update Quick Status row 18 (Phase 2) — change `Deferred (see decisions.md)` to `Completed in PROJ-376`.
- [ ] **Verify:** plan.md still parses cleanly; cross-references intact.

**Notes:** Closes PROJ-373 review MAJ-003 + MAJ-004.

### Task 3.7: Sharded suite + commit [Simple]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] `git status --short` confirms only Phase 3 files dirty.
- [ ] Run `python Projects/scripts/phase_complete.py PROJ-376 phase_3 --repo .worktrees/phases/PROJ-376/phase_3`.

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Re-profile evidence in `findings/post_proj376_profile.md` shows repeat-open `< 0.5 s`
- [ ] `BuildQueueController.reset_filters()` docstring updated (live since PROJ-376)
- [ ] `BuildQueueController._design_fingerprint` HFS+ comment added
- [ ] `VirtualTable.rebuild_row_pool` docstring documents layout-pass dependency
- [ ] `tests/unit/ui/components/table/test_virtual_table.py` includes column-config-change test
- [ ] PROJ-373 plan.md backfilled (MAJ-003 + MAJ-004)
- [ ] Sharded suite green
- [ ] Update status at top of this file to `Complete (Committed)` then `Complete (Verified)` after review
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State: project ready for final audit
