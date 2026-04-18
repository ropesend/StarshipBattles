# Phase 3: Delete `BattleScreen.start()` shim + `_build_fallback_outcome`

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-281 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Delete the deprecated `BattleScreen.start(team0, team1)` method and the `_build_fallback_outcome` helper (~90 LOC) now that Phase 2 has migrated every caller. After Phase 3, `BattleScreen` has exactly one entry: `start_battle(controller)` consuming a running `BattleController`.

**Prerequisite:** Phase 2 complete — zero callers of `BattleScreen.start(team0, team1)` remain in production or test code.

---

## Tasks

### Task 3.1: Pre-deletion verification [Simple]
**File:** N/A
**Tests:** Full PROJ-281 scope + Combat Lab simulation

- [x] Grep `BattleScreen.start(team` across `game/` — zero production/test callers remain; only docstring comments in `game/simulation/battle_controller.py:116,130` (cleaned up in Task 3.3)
- [x] Grep `scene\.start(\[`, `screen\.start(\[` across all test files — zero hits
- [x] Grep `_build_fallback_outcome` — only self-references inside `game/ui/screens/battle_screen.py` (deleted in Task 3.3)
- [x] Guard test at `tests/unit/simulation/test_unified_entry_guard.py:564-594` documents shim retention — flipped in Task 3.4

**Notes:** All preconditions satisfied.

### Task 3.2: Delete `BattleScreen.start()` method [Medium]
**File:** `game/ui/screens/battle_screen.py`
**Tests:** `pytest tests/unit/ui/`

- [x] Deleted `start(self, team0_ships, team1_ships, seed=None, headless=False, start_paused=False, test_mode=False)` method (previously ~lines 227–263) including full docstring
- [x] Verified no internal `BattleScreen` references to it remain — it was a terminal method that only called `start_battle(controller)` itself
- [x] Dropped the `BattleConfig` TYPE_CHECKING import that was only used by the deleted shim
- [x] `pytest tests/unit/ui/` — all pass

**Notes:**

### Task 3.3: Delete `_build_fallback_outcome()` and companions [Medium]
**File:** `game/ui/screens/battle_screen.py`
**Tests:** `pytest tests/unit/ui/`

- [x] Deleted `_build_fallback_outcome` (~90 LOC) and `_get_or_build_outcome` wrapper
- [x] `_on_battle_ended` simplified: directly calls `self._controller.get_outcome()` (no branch)
- [x] Deleted all "legacy test-convenience shim" / "pre-spec-contract callers" docstring references
- [x] Cleaned up stale docstrings in `game/simulation/battle_controller.py:116,130` (`configure()` docstring + boundary comment) that mentioned the legacy bypass
- [x] **Enhancement (Rule 3):** made `BattleController.get_outcome()` lazy — if `_outcome is None` but `_spec is not None`, extracts on demand. Covers the UI force-end case (user clicks "End Battle" before the natural end-transition fires) cleanly without a synthesis path. Used by `_on_battle_ended` and by `test_visual_run.py::TestEndBattleInTestMode` force-end tests
- [x] `pytest tests/unit/ui/` — all pass

**Notes:** Test fixture `tests/unit/test_lab/test_visual_run.py::TestEndBattleInTestMode::battle_screen` was explicitly designed to exercise the fallback (`mock_controller.get_outcome.return_value = None`). Rewrote to provide a real empty-teams `BattleOutcome` from the mock — tests still verify routing, not synthesis.

### Task 3.4: Update unified-entry guard test [Simple]
**File:** `tests/unit/simulation/test_unified_entry_guard.py`
**Tests:** `pytest tests/unit/simulation/test_unified_entry_guard.py`

- [x] Flipped `TestBattleScreenLegacyBypassDeprecated` → `TestBattleScreenLegacyBypassDeleted`
- [x] Added three enforcement tests: `test_battle_screen_start_team_shim_does_not_exist` (regex match returns None), `test_build_fallback_outcome_does_not_exist` (string absence), `test_battle_screen_has_only_start_battle_entry` (reflection — `start_battle` exists, `start` does not)
- [x] Docstring preserves institutional knowledge: "deleted by PROJ-281 Phase 3 after migrating all ~47 test callers to `start_battle_screen_with_minimal_spec`"

**Notes:**

### Task 3.5: Regression sweep [Simple]
**Tests:** Full affected scope

- [x] `pytest tests/unit/ui/ tests/unit/simulation/ tests/unit/combat_lab/ tests/unit/test_lab/ tests/fixtures/ tests/integration/` — 8040 passed, 2 skipped + 2 flaky pygame-font-init races (pass in isolation, not regressions)
- [x] Combat Lab simulation: 162 passed / 0 failed / 0 skipped
- [x] Line count: `game/ui/screens/battle_screen.py` went from ~795 LOC to 673 LOC — 122 lines deleted (shim + fallback + `_get_or_build_outcome` + docstrings)

**Notes:** Two flaky tests in `tests/fixtures/test_make_minimal_spec.py::TestStartBattleScreenWithMinimalSpec` (`test_ships_materialized_via_builder`, `test_single_ship_team_works`) failed under the 4-worker sharded runner with `pygame.error: font not initialized`. Re-running in isolation → 23/23 pass. Pre-existing parallel-init race, unrelated to Phase 3 changes.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `BattleScreen.start(team0, team1)` DELETED
- [x] `_build_fallback_outcome` DELETED (`_get_or_build_outcome` wrapper also deleted)
- [x] `BattleScreen` has exactly ONE production entry: `start_battle(controller)`
- [x] Unified-entry guard test updated to enforce the deletion
- [x] Full regression sweep passes
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 4 (documentation)
