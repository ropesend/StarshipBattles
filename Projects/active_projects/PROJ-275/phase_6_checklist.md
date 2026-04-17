# Phase 6: Strategy Spec Compiler — N Fleets

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-275 6`

**Status:** Complete
**Objective:** `build_strategy_battle_spec` accepts `Sequence[Fleet]`. Fan-out modifiers across N fleets.

---

## Tasks

### Task 6.1: Write failing tests [Medium]
**File:** `tests/unit/strategy/combat/test_spec_compiler.py`
**Tests:** `pytest tests/unit/strategy/combat/test_spec_compiler.py -v`

- [x] Test: `build_strategy_battle_spec([fleet_a, fleet_b, fleet_c], ...)` returns a BattleSpec with 3 teams
- [x] Test: storm modifier on a sector with 3 fleets fans out correctly
- [x] Test: `FleetCombatModifiers.damage_mult` for team 0 applied only to team 0; other teams default
- [x] Test: 1-fleet input raises ValueError (no battle needed)
- [x] Run — fail

**Notes:** 9 new tests added under `TestStrategyCompilerNFleets`. Initial run: 4 failed / 3 passed (entry vectors hardcoded to origin + 1-fleet validation absent).

### Task 6.2: Change signature to `Sequence[Fleet]` [Medium]
**File:** `game/strategy/combat/spec_compiler.py`
**Tests:** `pytest tests/unit/strategy/combat/ -v`

- [x] Change `build_strategy_battle_spec(fleets: Sequence[Fleet], ...)` — was probably `fleet1, fleet2`
- [x] Compute `num_teams = len(fleets)` early; validate `2 <= num_teams <= 8`
- [x] Use `resolve_team_entry_vectors(num_teams)` from Phase 2 for each team's entry vector
- [x] Emit one `TeamSpec` per fleet

**Notes:** Signature was already `List[Fleet]`; added `_MIN_TEAMS=2`/`_MAX_TEAMS=8` validation and threaded `entry_vector` into `_team_spec_for_fleet`. Pre-existing tests using single-fleet inputs (test_spec_compiler.py + test_spec_compiler_formation.py) updated to add a placeholder opponent fleet. LINE_ASTERN test now measures positions relative to entry-vector origin.

### Task 6.3: Migrate modifier emission helpers [Medium]
**File:** `game/strategy/combat/spec_compiler.py`
**Tests:** `pytest tests/unit/strategy/combat/ -v`

- [x] `_entries_from_environmental_effects`: accept `num_teams`; fan-out enemy-scope entries using `emit_entries_for_ability`
- [x] `_entries_from_fleet_combat_modifiers`: iterate `team_modifiers.items()` instead of hardcoded `[0]` / `[1]`
- [x] Apply stack_group naming convention consistently (e.g. `team{N}_shield_mult`)
- [x] Run tests — pass

**Notes:** Already done in PROJ-273. `_build_modifier_stack` already iterates `for team_id in range(team_count)` and routes per-team entries; environmental effects emit a single global entry that applies to every team regardless of N. New tests confirm behavior at 3 teams.

### Task 6.4: Update `apply_outcome_to_fleets` post_battle_hook [Medium]
**File:** `game/strategy/combat/post_battle_hook.py`
**Tests:** `pytest tests/unit/strategy/combat/test_post_battle_hook.py -v`

- [x] Audit per Phase 1 finding — confirm or fix any 2-team assumption in the hook
- [x] Ensure `outcome.team_outcomes.items()` iteration handles any N
- [x] Ensure fleet pruning works for all team_ids present in outcome, not just 0/1
- [x] Run tests — pass

**Notes:** Hook iterates `outcome.teams` and `fleets_by_team_id` keyed by team_id — already N-team friendly. New test `test_three_team_post_battle_hook_routes_outcomes_to_each_team` verifies a synthetic 3-team outcome correctly removes destroyed ships from teams 1 and 2 while team 0's ship survives.

---

## Phase Completion Checklist
- [x] All task checkboxes above are checked
- [x] Update plan.md
- [x] Run `python Projects/scripts/validate_phase.py PROJ-275 6`
