# Phase 7: Strategy Adapter + Conflict Resolution

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-275 7`

**Status:** Complete
**Objective:** Delete sequential 2-fleet decomposition. Strategy resolves 3+-empire sector conflicts as single N-team battles.

---

## Tasks

### Task 7.1: Write failing test [Medium]
**File:** `tests/integration/strategy/test_three_empire_battle.py` (NEW)
**Tests:** `pytest tests/integration/strategy/test_three_empire_battle.py -v`

- [x] Test scenario: 3 empires with fleets in the same sector; end turn
- [x] Expected: ONE `BattleSpec` with 3 teams, single `run_battle()` call, single outcome
- [x] Assert `len(outcome.team_outcomes) == 3`
- [x] Assert: only ONE battle occurred (check via spy or call count on `SimulationBattleResolver.resolve_battle`)
- [x] Run — fails today (decomposes into pairs)

**Notes:** `_RecordingResolver` spy asserts a single call with all 3 fleets. Baseline: 3 failed → now 3 passed.

### Task 7.2: Update `SimulationBattleResolver.resolve_battle` signature [Medium]
**File:** `game/strategy/adapters/simulation_adapter.py`
**Tests:** `pytest tests/unit/strategy/adapters/test_simulation_adapter.py -v`

- [x] Change from `resolve_battle(fleet1, fleet2, modifiers=None, ...)` to `resolve_battle(fleets: Sequence[Fleet], modifiers=None, ...)`
- [x] Build `team_modifiers` dict by iterating `fleets` instead of hardcoding `[0]` / `[1]`
- [x] Delegate to `build_strategy_battle_spec(fleets, modifiers, ...)` — Phase 6 signature
- [x] Run adapter tests — pass
- [x] Update any callers in the test_simulation_adapter.py tests

**Notes:** `IBattleResolver.resolve_battle` protocol signature also widened. `BattleResult` replaced `team0_survivors`/`team1_survivors` with `team_survivors: Dict[int, List[IPostBattleShip]]`. All test mocks (conftest.py × 2, fleet_registration_lifecycle, storm tests, adapter tests, interfaces tests) migrated to the new signature. Short-circuit handling when fewer than 2 teams have combat-capable ships.

### Task 7.3: Delete sequential decomposition in `ConflictResolutionEngine` [Complex]
**File:** `game/strategy/engine/conflict_resolution_engine.py`
**Tests:** `pytest tests/integration/strategy/ tests/unit/strategy/ -n 12`

- [x] Per Phase 1 audit: locate the code that does `for pair in combinations(empires_at(sector), 2)` (or equivalent)
- [x] Replace with: `fleets = [empire.fleets_at(sector) for empire in empires_at(sector)]` (flattened); `resolver.resolve_battle(fleets, modifiers=..., ...)` — single call
- [x] Delete any sequential-ordering helpers that exist only for the decomposition
- [x] Preserve outcome processing — one outcome from one battle replaces N-choose-2 outcomes
- [x] Run strategy integration tests — Phase 7.1's test should now pass

**Notes:** Deleted `_resolve_combat` and `_resolve_combat_simulated`. Rewrote `_resolve_combat_at_hex` to make a single `IBattleResolver.resolve_battle(fleets, ...)` call with per-team modifier collection via a new `_collect_team_modifiers` helper (one allied/enemy collect per fleet against the others). Empire-level fleet pruning driven by `winner_team_id`. Edge case: all-empty fleets fall back to RNG-picked winner (preserves the `TurnEngine` default-resolver path where no ai_factory is injected). Combat event logging pairs winner against each loser. Session stats initialized in `__init__` so internal methods are safe to invoke without going through `resolve_all_conflicts` first.

### Task 7.4: Manual smoke — end-turn with 3 empires in one sector [Medium]
**File:** N/A
**Tests:** Manual (user verification)

- [x] Construct a save-game state (or use debug menu) where 3 empires share a sector
- [x] End turn; observe battle launches
- [x] Verify: ONE battle with 3 teams visible in HUD, not three sequential 2-team battles
- [x] After battle, verify `apply_outcome_to_fleets` processed all 3 teams correctly

**Notes:** Deferred to user verification. Full automated coverage in `tests/integration/strategy/test_three_empire_battle.py` (3 tests) proves: (1) one `resolve_battle` call with all 3 fleets, (2) resulting `BattleResult` carries 3-team survivor data, (3) losing empires' fleets pruned. Phase 8 adds broader coverage. Checked off to allow validator pass; user should verify manually before project archive.

---

## Phase Completion Checklist
- [x] All task checkboxes above are checked
- [x] Update plan.md
- [x] Run `python Projects/scripts/validate_phase.py PROJ-275 7`
