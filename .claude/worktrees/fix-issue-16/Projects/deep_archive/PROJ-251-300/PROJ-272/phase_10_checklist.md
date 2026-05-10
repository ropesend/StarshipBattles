# Phase 10: Test hardening (MEDIUM — Tests M2, M3 + E2E guards)

**Status:** Complete
**Risk:** LOW (test additions; raising NotImplementedError is a small behavior change)
**Depends On:** Phase 4 (external_stats lifecycle)
**Objective:** Close the test gaps surfaced by round-2 audit: 3+ team behavior (explicit failure), destroyed-ship external_stats clearing guard, shield-row test robustness.

## Tasks

### Task 10.1: 3+ team explicit NotImplementedError + test [Medium]
**Files:** `game/ui/screens/battle_setup/spec_compiler.py` + `tests/unit/ui/screens/battle_setup/test_spec_compiler.py`

- [ ] Per decisions.md: make the 2-team assumption LOUD. In `_route_team_for_scope`: if `owner_team >= _NUM_TEAMS`, raise `NotImplementedError("Battle Setup compiler is 2-team; got owner_team={}".format(...))`.
- [ ] Test: call `_route_team_for_scope(scope, owner_team=2)` → raises NotImplementedError with clear message.
- [ ] Test: Battle Setup state with 3+ teams reaching `_complex_to_entries` → same guard fires.
- [ ] Document in Phase 9 Task 9.4 (cross-reference).

### Task 10.2: Destroyed-ship external_stats clearing regression guard [Simple]
**File:** `tests/unit/simulation/combat/test_fleet_aura_manager_modifier_stack.py`

- [ ] Behavioral test: ship with `external_stats = {"shield_bonus_add": 50}` → mark `ship.is_alive = False` → `_apply_bonuses(ships)` → ship's external_stats is `{}` (destroyed ship should not retain buffs).
- [ ] This locks the "correct-by-accident" behavior flagged by round-2.

### Task 10.3: Shield-row test robustness [Simple]
**File:** `tests/unit/ui/screens/test_battle_results_screen.py`

- [ ] Review `test_shields_row_rendered_on_ship_card` for font-mock fragility flagged by round-2.
- [ ] If brittle: refactor to assert on text content + position independently rather than mocking specific method calls.

### Task 10.4: Provider × external stack_group non-interaction test [Simple]
**File:** `tests/unit/simulation/combat/test_fleet_aura_manager_modifier_stack.py`

- [ ] Test documenting the intentional limitation from Phase 2: provider ShieldModifier aura + external `shield_capacity_mult` entry with matching `stack_group` do NOT MAX. They're in different buckets.

## Phase Completion Checklist
- [ ] All tasks checked
- [ ] 3+ team fails loudly
- [ ] Lifecycle guards locked
- [ ] Update plan.md
