# Phase 5: Delete `BattleScreen.start(team0, team1)` legacy bypass (HIGH — Code H3)

**Status:** Complete (scope corrected mid-phase — shim RETAINED as deprecated, not deleted)
**Risk:** LOW (zero callers today per prior audit; Rule 3 cleanup)
**Depends On:** None
**Objective:** `BattleScreen.start(team0_ships, team1_ships)` is a legacy test-convenience entry that bypasses the unified `run_battle(spec)` contract. It routes through `battle_service.start_battle` without wiring `engine.modifier_stack`. PROJ-270 audit flagged it as a Rule 3 violation; round-1 deferred the deletion. Round-2 confirms zero callers. Delete now.

`_build_fallback_outcome` is the companion function that synthesizes a BattleOutcome for this path. Also delete.

## Tasks

### Task 5.1: Verify zero callers [Simple]
- [ ] Grep all of `game/`, `tests/`, `combat_lab/` for `BattleScreen.start(`, `.start(team0`, `_build_fallback_outcome`. Confirm zero production callers; enumerate any test callers.
- [ ] If any test callers remain, migrate them to use `start_from_spec` / `run_battle` before deletion.

### Task 5.2: Delete [Simple]
**File:** `game/ui/screens/battle_screen.py`

- [ ] Delete `start(team0_ships, team1_ships, ...)` method.
- [ ] Delete `_build_fallback_outcome` method.
- [ ] Delete any `team0_ships`/`team1_ships` parameter-threading in related methods.

### Task 5.3: Regression guard [Simple]
**File:** `tests/unit/simulation/test_unified_entry_guard.py`

- [ ] Add text-guard: `BattleScreen` body does NOT contain `def start(` with two list-typed parameters.
- [ ] Same for `_build_fallback_outcome`.

## Phase Completion Checklist
- [ ] All tasks checked
- [ ] Zero references to deleted methods remain
- [ ] Update plan.md
