# Phase 5: Battle Setup State + UI — N Sides

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-275 5`

**Status:** Not Started
**Objective:** Migrate `BattleSetupState.side_0` / `side_1` to `sides: List[BattleSetupSide]`. UI supports add/remove sides.

---

## Tasks

### Task 5.1: Migrate `BattleSetupState` to list-based sides [Complex]
**File:** `game/ui/screens/battle_setup_state.py`
**Tests:** `pytest tests/unit/ui/screens/ -v`

- [ ] Change `side_0: BattleSetupSide` and `side_1: BattleSetupSide` fields to `sides: List[BattleSetupSide]` (default `[BattleSetupSide(), BattleSetupSide()]`)
- [ ] Add backcompat properties `side_0` (= `sides[0]`) and `side_1` (= `sides[1]`) — mark as DEPRECATED
- [ ] All serialization / deserialization code updated to use `sides` list
- [ ] Validation: `2 <= len(sides) <= 8` enforced at state-init time
- [ ] Run unit tests — pass

**Notes:**

### Task 5.2: Add/remove side controls in Battle Setup screen [Complex]
**File:** `game/ui/screens/battle_setup/screen.py`
**Tests:** Manual + any existing UI tests

- [ ] Add two buttons: "Add Side" (disabled at 8), "Remove Side" (disabled at 2)
- [ ] `add_side()` appends a fresh `BattleSetupSide` to `state.sides`; triggers panel refresh
- [ ] `remove_side(index)` removes the given side's BattleSetupSide; triggers panel refresh
- [ ] `_complex_toggles` dict key signature preserved (already keyed `(side_id, scope, design_id)`); adding/removing a side prunes stale keys
- [ ] Update `_sync_complex_toggles_to_state` (L1086) to iterate `state.sides` dynamically

**Notes:**

### Task 5.3: Refactor panels to parameterize on side index [Complex]
**File:** `game/ui/screens/battle_setup/panels/` (multiple)
**Tests:** Manual — launch Battle Setup, verify rendering

- [ ] Per Phase 1 audit — for each panel identified as hardcoded:
  - Replace `side_0 = state.side_0` with a per-side loop that creates one panel instance per side
  - Add side-index parameter to panel `__init__`
  - Panels lay out horizontally in 3+ side scenarios (scrollable if needed — consult Phase 1 audit recommendations)
- [ ] Each side's panel reads from `state.sides[index]`
- [ ] Test manually at 2 / 3 / 4 / 5 sides to confirm visual correctness

**Notes:**

### Task 5.4: Delete backcompat shims [Simple]
**File:** `game/ui/screens/battle_setup_state.py`
**Tests:** `pytest tests/unit/ui/screens/ -v`

- [ ] Grep: `grep -rn "\.side_0\|\.side_1" game/ tests/` — there should be ZERO results outside the state file itself
- [ ] Remove the `side_0` / `side_1` properties
- [ ] Run tests — pass

**Notes:**

### Task 5.5: Manual smoke at each team count [Medium]
**File:** N/A
**Tests:** Manual

- [ ] Launch Battle Setup, confirm it opens with 2 sides (default)
- [ ] Add a third side, populate with a ship, complete a battle — outcome shows 3 teams
- [ ] Add a fourth side, complete a battle — outcome shows 4 teams
- [ ] Remove to 2 sides, complete a battle — same as before
- [ ] Verify UI doesn't break at extreme (8 sides)

**Notes:**

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] Update plan.md
- [ ] Run `python Projects/scripts/validate_phase.py PROJ-275 5`
