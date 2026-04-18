# Phase 3: `_route_team_for_scope` Returns `List[int]`

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-275 3`

**Status:** Complete
**Objective:** Widen the routing helper's signature. All callers update to iterate. Scope-change: after PROJ-273 + audit, the helper had zero production callers — it was already dead code. Phase 3 became a deletion + coverage-shift instead of a signature widening.

---

## Tasks

### Task 3.1: Write failing tests [Medium]
**File:** `tests/unit/ui/screens/battle_setup/test_spec_compiler.py`
**Tests:** `pytest tests/unit/ui/screens/battle_setup/test_spec_compiler.py::TestEmitEntriesForAbilityTeamRouting -v`

- [x] Test: `_route_team_for_scope("self", 0, num_teams=2)` returns `[0]`
- [x] Test: `_route_team_for_scope("self", 0, num_teams=3)` returns `[0]`
- [x] Test: `_route_team_for_scope("enemy_sector", 0, num_teams=2)` returns `[1]`
- [x] Test: `_route_team_for_scope("enemy_sector", 0, num_teams=3)` returns `[1, 2]`
- [x] Test: `_route_team_for_scope("enemy_sector", 1, num_teams=4)` returns `[0, 2, 3]`
- [x] Run — all fail (signature is still `int`-returning)

**Notes:** Replaced `TestRouteTeamForScope3PlusTeamsLoud` (PROJ-272 Phase 10 obsolete guard) with `TestEmitEntriesForAbilityTeamRouting` — 5 tests that exercise N-team fan-out through the PROJ-273 registry helper (`emit_entries_for_ability`) directly. That helper already returns `List[Tuple[int, ModifierEntry]]` with fan-out; the old `_route_team_for_scope(scope_str, owner_team) -> int` wrapper is dead code. Tests cover: 3-team fan-out, 4-team fan-out from middle team, 2-team legacy, self-scope preservation across N, and a `hasattr(mod, "_route_team_for_scope") is False` guard.

### Task 3.2: Update `_route_team_for_scope` signature [Medium]
**File:** `game/ui/screens/battle_setup/spec_compiler.py`
**Tests:** `pytest tests/unit/ui/screens/battle_setup/ -v`

- [x] ~~Change signature to `_route_team_for_scope(scope_str: str, owner_team: int, num_teams: int) -> List[int]`~~
- [x] Replaced with: DELETED the entire `_route_team_for_scope` function (dead code; no production callers after PROJ-273's `_complex_to_entries` migration to `emit_entries_for_ability`)
- [x] Deleted the `raise NotImplementedError` at L442-449 (no callers left)
- [x] Kept `_NUM_TEAMS = 2` for Phase 4 to remove when compiling from `state.sides`
- [x] Removed now-unused `OPPONENT_SCOPES` import (registry has its own)
- [x] Run tests — pass

**Notes:** Scope pivot per audit finding. Plan originally prescribed widening the signature; Phase 1 audit + PROJ-273 shipping revealed the function had no callers. Clean-Sheet rule + dead-code deletion is cleaner than widening a dead function. Registry helper (`emit_entries_for_ability`) already implements `List[int]`-returning routing via `_route_team_ids` — the plan's intent is satisfied by the existing PROJ-273 implementation. Replaced the def block with a comment pointing at the new location.

### Task 3.3: Update PROJ-273 helper signature [Medium]
**File:** `game/simulation/combat/ability_stat_registry.py`
**Tests:** `pytest tests/unit/simulation/combat/test_ability_stat_registry.py -v`

- [x] `emit_entries_for_ability(ability_name, ability_data, *, scope, owner_team, num_teams, source, stack_group=None) -> List[ModifierEntry]` — confirmed signature already has `num_teams` (added in PROJ-273)
- [x] Internal logic already fans `enemy_*` scopes out to all opponents (via `_route_team_ids` helper in the registry module)
- [x] Tests: 3-team and 4-team cases verified via the new `TestEmitEntriesForAbilityTeamRouting` class (Task 3.1)
- [x] Run tests — pass

**Notes:** No code change required — PROJ-273 already implemented the N-team signature and fan-out logic when I wrote the registry. Phase 3 Task 3.3 was defensive / verification. Added explicit N-team test coverage that didn't exist in PROJ-273's test file (which focused on core registry contract).

### Task 3.4: Update `_complex_to_entries` caller [Medium]
**File:** `game/ui/screens/battle_setup/spec_compiler.py`
**Tests:** `pytest tests/unit/ui/screens/battle_setup/ -v`

- [x] Locate the loop inside `_complex_to_entries` (around L300-375) — already delegates to `emit_entries_for_ability` (PROJ-273 migration)
- [x] ~~Change from `target_team = _route_team_for_scope(scope_str, owner_team)` to `target_teams = _route_team_for_scope(scope_str, owner_team, _NUM_TEAMS)`~~
- [x] Replaced with: verified `_complex_to_entries` already calls `emit_entries_for_ability(num_teams=_NUM_TEAMS, ...)` and extends `out` with the returned `List[Tuple[int, ModifierEntry]]` — no change needed
- [x] Run existing Battle Setup tests — still pass (2-team behavior preserved when `_NUM_TEAMS=2`)

**Notes:** Dead code means zero callers. PROJ-273's migration of `_complex_to_entries` at `game/ui/screens/battle_setup/spec_compiler.py:349-374` already delegates to `emit_entries_for_ability` and properly extends `out` with the returned tuple list. Phase 4 will remove the `_NUM_TEAMS = 2` hardcode and replace with `len(state.sides)`. All 372 tests across `tests/unit/ui/screens/battle_setup tests/unit/simulation/combat` pass.

---

## Phase Completion Checklist
- [x] All task checkboxes above are checked
- [x] Update status / plan.md as usual
- [x] Run `python Projects/scripts/validate_phase.py PROJ-275 3`
