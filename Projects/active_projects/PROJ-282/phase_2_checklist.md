# Phase 2: Move `_complex_toggles` onto `BattleSetupState`

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-282 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Move the `_complex_toggles: Dict[str, bool]` dict from `FleetBattleSetupScreen` (where it lives as a private UI attribute) onto `BattleSetupState.BattleSetupSide` (where it belongs as part of the data model). Save/load gets toggle persistence for free after this move.

**Prerequisite:** Phase 1 audit complete — migration plan documented in `.agent_reports/PROJ-282-audit/migration_plan.md`.

---

## Tasks

### Task 2.1: Write tests for new state fields [Medium]
**File:** `tests/unit/ui/screens/test_battle_setup_state.py` (add cases) or new file
**Tests:** `pytest tests/unit/ui/screens/test_battle_setup_state.py`

- [ ] Test: `BattleSetupSide` has `system_complex_toggles: Dict[str, bool]` field, default empty
- [ ] Test: `BattleSetupSide` has `sector_complex_toggles: Dict[str, bool]` field, default empty
- [ ] Test: `to_dict()` includes the new fields
- [ ] Test: `from_dict()` restores the new fields
- [ ] Test: `from_dict()` tolerates legacy saves without the new fields (defaults to empty) — matches "saves are disposable" CLAUDE.md policy but graceful
- [ ] Test: setting `side.system_complex_toggles[complex_id] = True` persists through `to_dict/from_dict` round-trip

**Notes:**

### Task 2.2: Add fields to `BattleSetupSide` [Simple]
**File:** `game/ui/screens/battle_setup_state.py`
**Tests:** `pytest tests/unit/ui/screens/test_battle_setup_state.py` — all pass

- [ ] Add `system_complex_toggles: Dict[str, bool]` field
- [ ] Add `sector_complex_toggles: Dict[str, bool]` field
- [ ] Update `to_dict()` to serialize both fields
- [ ] Update `from_dict()` to restore both fields (use `data.get(key, {})` for legacy compat)
- [ ] Keep existing `system_complexes` / `sector_complexes` list fields if production still uses them — decide during audit whether `*_toggles` replaces them or supplements them

**Notes:** Decide during implementation whether `system_complex_toggles` *replaces* the existing `system_complexes` list or *supplements* it. Read the current screen's toggle-to-list sync code to understand.

### Task 2.3: Update FleetBattleSetupScreen to write toggles into state [Medium]
**File:** `game/ui/screens/battle_setup_screen.py`
**Tests:** `pytest tests/unit/ui/screens/`

- [ ] Locate `self._complex_toggles` initialization (around line 118)
- [ ] Remove the dict; route reads/writes through `self.state.sides[side_idx].system_complex_toggles` (or sector, as appropriate)
- [ ] Locate the battle-launch sync code that copies toggles into `state.system_complexes` — this logic can be simplified or deleted (state already holds the toggles)
- [ ] Verify the Spec compiler still reads the right shape — may need a small update

**Notes:**

### Task 2.4: Regression sweep [Simple]
**Tests:** PROJ-282 scope

- [ ] `pytest tests/unit/ui/screens/` — all pass
- [ ] `pytest tests/unit/ui/` — no regressions in related tests
- [ ] Manual smoke: if possible, toggle a complex in the running battle setup UI and verify it lands in the spec

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `BattleSetupSide` owns the toggle state; screen no longer has `_complex_toggles`
- [ ] Save/load round-trips the toggles correctly
- [ ] No screen-side sync code remains to copy toggles into state — state IS the source of truth
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3 (extract ViewModel)
