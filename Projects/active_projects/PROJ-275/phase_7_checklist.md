# Phase 7: Strategy Adapter + Conflict Resolution

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-275 7`

**Status:** Not Started
**Objective:** Delete sequential 2-fleet decomposition. Strategy resolves 3+-empire sector conflicts as single N-team battles.

---

## Tasks

### Task 7.1: Write failing test [Medium]
**File:** `tests/integration/strategy/test_three_empire_battle.py` (NEW)
**Tests:** `pytest tests/integration/strategy/test_three_empire_battle.py -v`

- [ ] Test scenario: 3 empires with fleets in the same sector; end turn
- [ ] Expected: ONE `BattleSpec` with 3 teams, single `run_battle()` call, single outcome
- [ ] Assert `len(outcome.team_outcomes) == 3`
- [ ] Assert: only ONE battle occurred (check via spy or call count on `SimulationBattleResolver.resolve_battle`)
- [ ] Run — fails today (decomposes into pairs)

**Notes:**

### Task 7.2: Update `SimulationBattleResolver.resolve_battle` signature [Medium]
**File:** `game/strategy/adapters/simulation_adapter.py`
**Tests:** `pytest tests/unit/strategy/adapters/test_simulation_adapter.py -v`

- [ ] Change from `resolve_battle(fleet1, fleet2, modifiers=None, ...)` to `resolve_battle(fleets: Sequence[Fleet], modifiers=None, ...)`
- [ ] Build `team_modifiers` dict by iterating `fleets` instead of hardcoding `[0]` / `[1]`
- [ ] Delegate to `build_strategy_battle_spec(fleets, modifiers, ...)` — Phase 6 signature
- [ ] Run adapter tests — pass
- [ ] Update any callers in the test_simulation_adapter.py tests

**Notes:**

### Task 7.3: Delete sequential decomposition in `ConflictResolutionEngine` [Complex]
**File:** `game/strategy/turn_engine/conflict_resolution_engine.py`
**Tests:** `pytest tests/integration/strategy/ tests/unit/strategy/ -n 12`

- [ ] Per Phase 1 audit: locate the code that does `for pair in combinations(empires_at(sector), 2)` (or equivalent)
- [ ] Replace with: `fleets = [empire.fleets_at(sector) for empire in empires_at(sector)]` (flattened); `resolver.resolve_battle(fleets, modifiers=..., ...)` — single call
- [ ] Delete any sequential-ordering helpers that exist only for the decomposition
- [ ] Preserve outcome processing — one outcome from one battle replaces N-choose-2 outcomes
- [ ] Run strategy integration tests — Phase 7.1's test should now pass

**Notes:**

### Task 7.4: Manual smoke — end-turn with 3 empires in one sector [Medium]
**File:** N/A
**Tests:** Manual

- [ ] Construct a save-game state (or use debug menu) where 3 empires share a sector
- [ ] End turn; observe battle launches
- [ ] Verify: ONE battle with 3 teams visible in HUD, not three sequential 2-team battles
- [ ] After battle, verify `apply_outcome_to_fleets` processed all 3 teams correctly

**Notes:**

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] Update plan.md
- [ ] Run `python Projects/scripts/validate_phase.py PROJ-275 7`
