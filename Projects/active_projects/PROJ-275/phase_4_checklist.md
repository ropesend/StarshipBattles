# Phase 4: Battle Setup Spec Compiler — N Teams

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-275 4`

**Status:** Not Started
**Objective:** Lift `_NUM_TEAMS = 2` constant. Compiler emits N `TeamSpec`s from `state.sides` list.

---

## Tasks

### Task 4.1: Add failing tests [Complex]
**File:** `tests/unit/ui/screens/battle_setup/test_spec_compiler.py`
**Tests:** `pytest tests/unit/ui/screens/battle_setup/test_spec_compiler.py -v`

- [ ] Test: `build_manual_battle_spec(state_with_3_sides, registries)` returns `BattleSpec` with 3 `TeamSpec`s
- [ ] Test: each team's entry vector matches the ring layout from Phase 2
- [ ] Test: enemy-scope complex on side 0 fans out to sides 1 and 2 (two ModifierEntries emitted)
- [ ] Test: `build_manual_battle_spec(state_with_4_sides, registries)` works (4 teams)
- [ ] Test: 1-side state raises ValueError
- [ ] Test: 9-side state raises ValueError (over max)
- [ ] Run — all fail (compiler still assumes 2)

**Notes:**

### Task 4.2: Replace `_NUM_TEAMS` constant [Medium]
**File:** `game/ui/screens/battle_setup/spec_compiler.py`
**Tests:** `pytest tests/unit/ui/screens/battle_setup/ -v`

- [ ] Delete `_NUM_TEAMS = 2` literal
- [ ] In `build_manual_battle_spec`, compute `num_teams = len(state.sides)` early
- [ ] Add validation: `if num_teams < 2 or num_teams > 8: raise ValueError(...)`
- [ ] Pass `num_teams` to all routing helpers

**Notes:**

### Task 4.3: Emit N TeamSpecs [Complex]
**File:** `game/ui/screens/battle_setup/spec_compiler.py`
**Tests:** `pytest tests/unit/ui/screens/battle_setup/ -v`

- [ ] Replace hardcoded `side_0` / `side_1` iteration with `for side_id, side in enumerate(state.sides):`
- [ ] Use `resolve_team_entry_vectors(num_teams)` from Phase 2 to assign entry vectors
- [ ] For each side: build one `TeamSpec` per team with its entry vector, its task forces, its formations
- [ ] Build `ModifierStack` by iterating ALL sides, not just `side_0` / `side_1`
- [ ] Run tests — pass

**Notes:**

### Task 4.4: End-to-end with 3-team spec [Medium]
**File:** `tests/unit/ui/screens/battle_setup/test_spec_compiler.py`
**Tests:** `pytest tests/unit/ui/screens/battle_setup/test_spec_compiler.py::test_three_side_end_to_end -v`

- [ ] Test: construct a 3-side state (2 friends on side 0, 1 ship on side 1, 1 ship on side 2)
- [ ] Compile to BattleSpec
- [ ] Assert `len(spec.teams) == 3`
- [ ] Assert each team has correct number of ships
- [ ] Assert entry vectors are spaced 120° apart
- [ ] Run `run_battle(spec, ...)` via the headless path
- [ ] Assert `outcome.winner` is one of {0, 1, 2, -1}
- [ ] Run — passes

**Notes:**

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] Update plan.md
- [ ] Run `python Projects/scripts/validate_phase.py PROJ-275 4`
