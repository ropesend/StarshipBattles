# Phase 6: Strategy Spec Compiler — N Fleets

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-275 6`

**Status:** Not Started
**Objective:** `build_strategy_battle_spec` accepts `Sequence[Fleet]`. Fan-out modifiers across N fleets.

---

## Tasks

### Task 6.1: Write failing tests [Medium]
**File:** `tests/unit/strategy/combat/test_spec_compiler.py`
**Tests:** `pytest tests/unit/strategy/combat/test_spec_compiler.py -v`

- [ ] Test: `build_strategy_battle_spec([fleet_a, fleet_b, fleet_c], ...)` returns a BattleSpec with 3 teams
- [ ] Test: storm modifier on a sector with 3 fleets fans out correctly
- [ ] Test: `FleetCombatModifiers.damage_mult` for team 0 applied only to team 0; other teams default
- [ ] Test: 1-fleet input raises ValueError (no battle needed)
- [ ] Run — fail

**Notes:**

### Task 6.2: Change signature to `Sequence[Fleet]` [Medium]
**File:** `game/strategy/combat/spec_compiler.py`
**Tests:** `pytest tests/unit/strategy/combat/ -v`

- [ ] Change `build_strategy_battle_spec(fleets: Sequence[Fleet], ...)` — was probably `fleet1, fleet2`
- [ ] Compute `num_teams = len(fleets)` early; validate `2 <= num_teams <= 8`
- [ ] Use `resolve_team_entry_vectors(num_teams)` from Phase 2 for each team's entry vector
- [ ] Emit one `TeamSpec` per fleet

**Notes:**

### Task 6.3: Migrate modifier emission helpers [Medium]
**File:** `game/strategy/combat/spec_compiler.py`
**Tests:** `pytest tests/unit/strategy/combat/ -v`

- [ ] `_entries_from_environmental_effects`: accept `num_teams`; fan-out enemy-scope entries using `emit_entries_for_ability`
- [ ] `_entries_from_fleet_combat_modifiers`: iterate `team_modifiers.items()` instead of hardcoded `[0]` / `[1]`
- [ ] Apply stack_group naming convention consistently (e.g. `team{N}_shield_mult`)
- [ ] Run tests — pass

**Notes:**

### Task 6.4: Update `apply_outcome_to_fleets` post_battle_hook [Medium]
**File:** `game/strategy/combat/post_battle_hook.py`
**Tests:** `pytest tests/unit/strategy/combat/test_post_battle_hook.py -v`

- [ ] Audit per Phase 1 finding — confirm or fix any 2-team assumption in the hook
- [ ] Ensure `outcome.team_outcomes.items()` iteration handles any N
- [ ] Ensure fleet pruning works for all team_ids present in outcome, not just 0/1
- [ ] Run tests — pass

**Notes:**

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] Update plan.md
- [ ] Run `python Projects/scripts/validate_phase.py PROJ-275 6`
