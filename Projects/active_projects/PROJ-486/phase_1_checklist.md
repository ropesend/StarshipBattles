# Phase 1: Delete `load_state` + retire 4 test callers

**Status:** Complete
**Objective:** Delete the ~87-LOC `BattleController.load_state` method and reconcile the 4 test callers in `test_state.py`.

---

## Tasks

### Task 1.1: Reconcile 4 test callers of `load_state`
**File:** `tests/unit/simulation/battle_controller/test_state.py`

- [x] Read each `load_state` invocation at `test_state.py:90, 128, 245, 268`
- [x] Disposition: ALL FOUR exercise save/restore round-trip behavior on the dead `load_state` path. None of them assert anything about `save_state` that isn't already covered by `test_save_state_captures_state`. RETIRE (delete).
- [x] Record disposition in Notes section below

### Task 1.2: Delete `BattleController.load_state` from production
**File:** `game/simulation/battle_controller.py`

- [x] Deleted `BattleController.load_state` (~87 LOC; previously at lines 509-595 post-`67116932d`). Inline `# PROJ-270 Phase 10` note removed with the method.
- [x] Verified `save_state` has no `load_state`-referencing docstring; left it unchanged.
- [x] Verified `_require_registries_for_state_restore` still has a live caller at `battle_controller.py:185` (inside `add_ships_from_state`), so its tests at `TestRequireRegistriesForStateRestore` were retained.

### Phase Verification
- [x] `pytest tests/unit/simulation/battle_controller/` 97 passed
- [x] `pytest tests/unit/simulation/battle_controller/test_state.py` 7 passed (down from 11; the 4 deleted load_state tests are gone, the 7 remaining cover save_state + get_results + _require_registries + outcome capture)
- [x] `grep -n "def load_state" game/simulation/battle_controller.py` returns 0 matches
- [x] Module import smoke: `hasattr(BattleController, 'load_state')` → False; `hasattr(BattleController, 'save_state')` → True; `hasattr(BattleController, '_require_registries_for_state_restore')` → True

**Notes (filled in during Task 1.1):**
- test_state.py:90 (was `test_load_state_restores_battle`) — RETIRED: exercises full `load_state` round-trip including `restore_config_from_state`, projectile restore, boundary fallback. All dead behavior after `load_state` deletion.
- test_state.py:128 (was `test_load_state_handles_error`) — RETIRED: exercises `load_state`'s error-result path. Dead.
- test_state.py:245 (was `test_load_state_restores_alive_projectiles_only`) — RETIRED: characterization test for `load_state`'s projectile-restore subroutine. Dead.
- test_state.py:268 (was `test_load_state_resolves_projectile_owner_via_ship_id_map`) — RETIRED: characterization test for `load_state`'s `ship_lookup` resolution. Dead.

The entire `TestBattleControllerLoadStateProjectiles` class (including its `_build_load_state_setup` helper) was deleted as a unit, since both of its tests targeted `load_state`. `BattleConfig` import in the test file's imports was removed (only callers were inside the deleted block).

The original class `TestBattleControllerStateSaveLoad` was renamed to `TestBattleControllerStateSave` since only the 2 save_state tests remain.

---

## Phase Completion Checklist
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to mark project complete

_Source audit: `Reviews/results/2026-05-20_210635_legacy-audit/`. See `findings/source_audit.md` for the link._
