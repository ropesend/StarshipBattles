# Phase 4: Consecutive-battle external_stats reset (HIGH — Tests H3)

**Status:** Complete
**Risk:** LOW (additive guard; no behavior change for fresh ships)
**Depends On:** None
**Objective:** In strategy mode, ships can be reused across consecutive battles (carried through `ShipInstance → Ship → ShipInstance` round-trips). `FleetAuraManager._apply_bonuses` writes `ship.external_stats` at battle start and resets on death. But there's no explicit reset for ships that ENTER a new battle — they inherit whatever external_stats they had in the previous battle. If the previous battle populated `shield_bonus_add=50` and the current battle doesn't, the ship silently keeps the +50.

Audit confirmed: `FleetAuraManager.initialize` doesn't explicitly clear `external_stats` on ship entry. It relies on `_apply_bonuses` overwriting — but `_apply_bonuses` only runs for teams present in `_team_bonuses`. A ship whose team has zero bonuses in the new battle never has its external_stats touched.

## Tasks

### Task 4.1: Failing regression test [Medium]
**File:** `tests/unit/simulation/combat/test_fleet_aura_manager_modifier_stack.py`

- [ ] Failing test: ship with `external_stats = {"shield_bonus_add": 50}` enters a new battle with empty ModifierStack → after `FleetAuraManager.initialize`, ship's external_stats is `{}`.
- [ ] Run — fails (external_stats leaks across).

### Task 4.2: Fix in `FleetAuraManager.initialize` [Simple]
**File:** `game/simulation/combat/fleet_aura_manager.py`

- [ ] At the start of `initialize`, for each ship, explicitly reset `ship.external_stats = {}` if attribute exists.
- [ ] Document that this is the authoritative reset point — `_apply_bonuses` only POPULATES, doesn't guarantee CLEAR.
- [ ] Alternative: do it in `_apply_bonuses` at the start of each invocation — but that runs every tick and would thrash. `initialize` is the right boundary.

### Task 4.3: Additional lifecycle guards [Simple]
- [ ] Destroyed-ship clearing test: ship dies mid-battle → `_apply_bonuses` sets external_stats to `{}`. Already correct-by-accident per round-2 audit; add explicit test to lock.

## Phase Completion Checklist
- [ ] All tasks checked
- [ ] external_stats lifecycle locked by tests
- [ ] Update plan.md
