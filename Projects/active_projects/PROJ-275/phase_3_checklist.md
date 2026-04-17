# Phase 3: `_route_team_for_scope` Returns `List[int]`

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-275 3`

**Status:** Not Started
**Objective:** Widen the routing helper's signature. All callers update to iterate.

---

## Tasks

### Task 3.1: Write failing tests [Medium]
**File:** `tests/unit/ui/screens/battle_setup/test_spec_compiler.py`
**Tests:** `pytest tests/unit/ui/screens/battle_setup/test_spec_compiler.py::test_route_team_for_scope -v`

- [ ] Test: `_route_team_for_scope("self", 0, num_teams=2)` returns `[0]`
- [ ] Test: `_route_team_for_scope("self", 0, num_teams=3)` returns `[0]`
- [ ] Test: `_route_team_for_scope("enemy_sector", 0, num_teams=2)` returns `[1]`
- [ ] Test: `_route_team_for_scope("enemy_sector", 0, num_teams=3)` returns `[1, 2]`
- [ ] Test: `_route_team_for_scope("enemy_sector", 1, num_teams=4)` returns `[0, 2, 3]`
- [ ] Run — all fail (signature is still `int`-returning)

**Notes:**

### Task 3.2: Update `_route_team_for_scope` signature [Medium]
**File:** `game/ui/screens/battle_setup/spec_compiler.py`
**Tests:** `pytest tests/unit/ui/screens/battle_setup/ -v`

- [ ] Change signature to `_route_team_for_scope(scope_str: str, owner_team: int, num_teams: int) -> List[int]`
- [ ] Replace arithmetic 2-team trick at L476 with list comprehension: `[t for t in range(num_teams) if t != owner_team]`
- [ ] Delete the `raise NotImplementedError` at L467-474 (no longer needed)
- [ ] Keep `_NUM_TEAMS = 2` for the moment — Phase 4 will parameterize it
- [ ] Run tests — pass

**Notes:**

### Task 3.3: Update PROJ-273 helper signature [Medium]
**File:** `game/simulation/combat/ability_stat_registry.py`
**Tests:** `pytest tests/unit/simulation/combat/test_ability_stat_registry.py -v`

- [ ] `emit_entries_for_ability(ability_name, ability_data, *, scope, owner_team, num_teams, source, stack_group=None) -> List[ModifierEntry]` — confirm signature already has `num_teams` (it does — added in PROJ-273)
- [ ] Update internal logic: fan-out `enemy_*` scopes to all opponents, not just one
- [ ] Tests: add 3-team and 4-team cases (1 enemy-scope ability on team 0 produces N-1 entries)
- [ ] Run tests — pass

**Notes:**

### Task 3.4: Update `_complex_to_entries` caller [Medium]
**File:** `game/ui/screens/battle_setup/spec_compiler.py`
**Tests:** `pytest tests/unit/ui/screens/battle_setup/ -v`

- [ ] Locate the loop inside `_complex_to_entries` (around L300-375)
- [ ] Change from `target_team = _route_team_for_scope(scope_str, owner_team)` to `target_teams = _route_team_for_scope(scope_str, owner_team, _NUM_TEAMS)`
- [ ] Wrap the entry emission in `for target_team in target_teams:`
- [ ] Run existing Battle Setup tests — still pass (2-team behavior preserved when `_NUM_TEAMS=2`)

**Notes:**

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] Update status / plan.md as usual
- [ ] Run `python Projects/scripts/validate_phase.py PROJ-275 3`
