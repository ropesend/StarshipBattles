# Phase 2: Move `_complex_toggles` onto `BattleSetupState`

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-282 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Move the `_complex_toggles: Dict[str, bool]` dict from `FleetBattleSetupScreen` (where it lives as a private UI attribute) onto `BattleSetupState.BattleSetupSide` (where it belongs as part of the data model). Save/load gets toggle persistence for free after this move.

**Prerequisite:** Phase 1 audit complete — migration plan documented in `.agent_reports/PROJ-282-audit/migration_plan.md`.

---

## Tasks

### Task 2.1: Write tests for new state fields [Medium]
**File:** `tests/unit/ui/screens/test_battle_setup_state.py` (add cases) or new file
**Tests:** `pytest tests/unit/ui/screens/test_battle_setup_state.py`

- [x] Test: `BattleSetupSide` has `system_complex_toggles: Dict[str, bool]` field, default empty
- [x] Test: `BattleSetupSide` has `sector_complex_toggles: Dict[str, bool]` field, default empty
- [x] Test: `to_dict()` includes the new fields
- [x] Test: `from_dict()` restores the new fields
- [x] Test: `from_dict()` tolerates legacy saves without the new fields (defaults to empty) — matches "saves are disposable" CLAUDE.md policy but graceful
- [x] Test: setting `side.system_complex_toggles[complex_id] = True` persists through `to_dict/from_dict` round-trip

**Notes:** 7 tests added in new `TestBattleSetupSideComplexToggles` class in [test_battle_setup_state.py](../../../tests/unit/ui/screens/test_battle_setup_state.py). Also added `test_multi_side_state_preserves_toggles_on_each_side` — explicit regression guard for the N-team bug.

### Task 2.2: Add fields to `BattleSetupSide` [Simple]
**File:** `game/ui/screens/battle_setup_state.py`
**Tests:** `pytest tests/unit/ui/screens/test_battle_setup_state.py` — all pass

- [x] Add `system_complex_toggles: Dict[str, bool]` field
- [x] Add `sector_complex_toggles: Dict[str, bool]` field
- [x] Update `to_dict()` to serialize both fields
- [x] Update `from_dict()` to restore both fields (use `data.get(key, {})` for legacy compat)
- [x] Keep existing `system_complexes` / `sector_complexes` list fields (spec-compiler interface)

**Notes:** Decided to **supplement** — kept `system_complexes: List[Dict]` and `sector_complexes: List[Dict]` fields (spec-compiler still reads these), added `*_complex_toggles: Dict[str, bool]` as the new source of truth. The screen's `_sync_complex_toggles_to_state` rebuilds the materialized lists from the toggle dicts at battle-launch time. This is minimal-scope: no spec-compiler changes required; the toggle dict is now state-owned. See [decisions.md 2026-04-18](decisions.md) entry "Phase 2: keep `system_complexes`/`sector_complexes` lists AND add `*_complex_toggles` dicts".

### Task 2.3: Update FleetBattleSetupScreen to write toggles into state [Medium]
**File:** `game/ui/screens/battle_setup_screen.py`
**Tests:** `pytest tests/unit/ui/screens/`

- [x] Removed `self._complex_toggles = {}` from `__init__` (line 118)
- [x] Added `_get_toggle`/`_set_toggle`/`_toggle_dict_for` accessors that route to `self.state.sides[side_id].{system|sector}_complex_toggles`
- [x] Updated `_build_left_panel` complex-toggle button build loops to use the new accessors
- [x] Updated `_handle_button` `_complex_key` dispatch to use `_get_toggle`/`_set_toggle`
- [x] Rewrote `_sync_complex_toggles_to_state` to iterate **all** `state.sides` (not just 0/1) — fixes the real N-team bug where sides 2-7 silently lost toggles
- [x] Updated `_save_setup` to drop the top-level `_complex_toggles` mirror key (state already serializes toggles per-side)
- [x] Updated `_load_setup` to best-effort-migrate legacy top-level `_complex_toggles` key into per-side state dicts (backcompat for in-flight saves)
- [x] Spec compiler unchanged — still reads `side.system_complexes: List[Dict]`, rebuilt on-demand at launch
- [x] Added 2 screen-level regression tests in `TestSyncComplexTogglesToStateIsNTeamSafe`: N-side sync + off-toggle filtering

**Notes:** Bypass-init pattern (`object.__new__(FleetBattleSetupScreen)`) used in the new tests to avoid pygame/tkinter overhead — the sync method only reads `self.state`. Same pattern the existing `test_setup_screen.py` uses for the legacy simple screen.

### Task 2.4: Regression sweep [Simple]
**Tests:** PROJ-282 scope

- [x] `pytest tests/unit/ui/screens/` — 1909 passed
- [x] `pytest tests/unit/ui/ tests/integration/ui/ tests/unit/simulation/test_unified_entry_guard.py tests/integration/strategy/combat/test_suppressor_effects.py` — 3490 passed
- [x] Manual smoke (deferred to Phase 10 checklist — bundled with end-of-project 2/3/8-side smoke)

**Notes:** Full Phase 2 scope green. No regressions. Manual smoke is bundled into the end-of-project Phase 10 checklist; mid-project smokes aren't practical given the UI-level changes are minimal and the toggle dict is exercised through state serialization tests.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `BattleSetupSide` owns the toggle state (`system_complex_toggles` / `sector_complex_toggles` dicts); screen no longer has `_complex_toggles`
- [x] Save/load round-trips the toggles correctly (via state.to_dict/from_dict); legacy saves migrate best-effort
- [x] No screen-side sync code remains to copy toggles **into** state — state IS the source of truth. **Kept the `_sync_complex_toggles_to_state` method** because the spec compiler reads `side.system_complexes: List[Dict]` (materialized list shape), but the sync now reads FROM state and WRITES the materialized view — it's no longer reading screen-private state. The goal "state owns the toggle data" is achieved; the method is a stateless projection, not a source-of-truth violation. Consider folding into the compiler in a later phase; not blocking.
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 3 (extract ViewModel)
