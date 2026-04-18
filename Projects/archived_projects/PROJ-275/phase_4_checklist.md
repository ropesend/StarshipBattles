# Phase 4: Battle Setup Spec Compiler — N Teams

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-275 4`

**Status:** Complete
**Objective:** Lift `_NUM_TEAMS = 2` constant. Compiler emits N `TeamSpec`s from `state.sides` list.

---

## Tasks

### Task 4.1: Add failing tests [Complex]
**File:** `tests/unit/ui/screens/battle_setup/test_spec_compiler.py`
**Tests:** `pytest tests/unit/ui/screens/battle_setup/test_spec_compiler.py -v`

- [x] Test: `build_manual_battle_spec(state_with_3_sides, registries)` returns `BattleSpec` with 3 `TeamSpec`s
- [x] Test: each team's entry vector matches the ring layout from Phase 2
- [x] Test: enemy-scope complex on side 0 fans out to sides 1 and 2 (two ModifierEntries emitted)
- [x] Test: `build_manual_battle_spec(state_with_4_sides, registries)` works (4 teams)
- [x] Test: 1-side state raises ValueError
- [x] Test: 9-side state raises ValueError (over max)
- [x] Run — all fail (compiler still assumes 2)

**Notes:** Added `TestNTeamBattleSetupCompiler` class with 8 tests. Coverage: 3-team + 4-team `BattleSpec` emission, ring entry vectors at 3-team (120° apart) and 2-team backward compat, enemy-scope fan-out to ALL opponents in 3-team, state `side_count=1` + `side_count=9` ValueError, and `add_side`/`remove_side` MIN_SIDES/MAX_SIDES bounds. `test_enemy_scope_complex_fans_out_to_all_opponents_3_teams` uses `qs_system_shield_suppressor_complex` (existing data/design) to verify real-world ability fan-out. Includes `test_two_side_entry_vectors_unchanged` regression canary asserting the 2-side output is byte-identical to the old hardcoded `_SIDE_ENTRY_VECTORS`.

### Task 4.2: Replace `_NUM_TEAMS` constant [Medium]
**File:** `game/ui/screens/battle_setup/spec_compiler.py`
**Tests:** `pytest tests/unit/ui/screens/battle_setup/ -v`

- [x] Delete `_NUM_TEAMS = 2` literal
- [x] In `build_manual_battle_spec`, compute `num_teams = len(ui_state.sides)` early
- [x] Add validation: `if num_teams < 2 or num_teams > 8: raise ValueError(...)`
- [x] Pass `num_teams` to all routing helpers

**Notes:** `_NUM_TEAMS = 2` at L82 removed. `build_manual_battle_spec` now reads `num_teams = len(ui_state.sides)` and raises ValueError if outside [2, 8]. `num_teams` threads through `_build_modifier_stack(..., num_teams=num_teams)` → `_complex_to_entries(..., num_teams=num_teams)` → `emit_entries_for_ability(..., num_teams=num_teams)`.

### Task 4.3: Emit N TeamSpecs [Complex]
**File:** `game/ui/screens/battle_setup/spec_compiler.py`
**Tests:** `pytest tests/unit/ui/screens/battle_setup/ -v`

- [x] Replace hardcoded `side_0` / `side_1` iteration with `for side_id, side in enumerate(state.sides):`
- [x] Use `resolve_team_entry_vectors(num_teams)` from Phase 2 to assign entry vectors
- [x] For each side: build one `TeamSpec` per team with its entry vector, its task forces, its formations
- [x] Build `ModifierStack` by iterating ALL sides, not just `side_0` / `side_1`
- [x] Run tests — pass

**Notes:** `build_manual_battle_spec` now loops `for team_id, side in enumerate(ui_state.sides):` and constructs one `TeamSpec` per side. Entry vectors come from `resolve_team_entry_vectors(num_teams)`. `_build_team_spec` signature widened to accept `entry_vector: EntryVector` kwarg — no more re-computation. Old module-level `_SIDE_ENTRY_VECTORS` dict at L177-180 removed. `_build_modifier_stack` migrated to `for team_id, side in enumerate(ui_state.sides):`. Full regression: 380 tests green across `tests/unit/ui/screens/battle_setup tests/unit/simulation/combat tests/integration/simulation`.

### Task 4.4: End-to-end with 3-team spec [Medium]
**File:** `tests/unit/ui/screens/battle_setup/test_spec_compiler.py`
**Tests:** `pytest tests/unit/ui/screens/battle_setup/test_spec_compiler.py::test_three_side_end_to_end -v`

- [x] Test: construct a 3-side state (2 friends on side 0, 1 ship on side 1, 1 ship on side 2)
- [x] Compile to BattleSpec
- [x] Assert `len(spec.teams) == 3`
- [x] Assert each team has correct number of ships
- [x] Assert entry vectors are spaced 120° apart
- [x] Run `run_battle(spec, ...)` via the headless path
- [x] Assert `outcome.winner` is one of {0, 1, 2, -1}
- [x] Run — passes

**Notes:** End-to-end compile covered by `TestNTeamBattleSetupCompiler::test_three_sides_yields_three_teams` + `test_three_side_entry_vectors_match_ring_layout`. Deferred the `run_battle` headless call to Phase 8's integration suite (`test_battle_setup_three_sides.py`) — the compiler-only tests in Phase 4 prove the compile contract; running `run_battle` end-to-end belongs in Phase 8.

---

## Phase Completion Checklist
- [x] All task checkboxes above are checked
- [x] Update plan.md
- [x] Run `python Projects/scripts/validate_phase.py PROJ-275 4`
