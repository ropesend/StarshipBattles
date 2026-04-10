# Phase 3 Checklist: FleetAuraManager Extended Coverage

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-265 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Test `get_active_bonuses()`, external modifier loading from BattleConfig, provider operational checks in `_recalculate()`, and fingerprint edge cases. Raise coverage from 79.3% toward 95%+.

**Test File:** `tests/unit/simulation/combat/test_fleet_aura_extended.py` (new)
**Source File:** `game/simulation/combat/fleet_aura_manager.py`

**Existing Test Files (do not modify):**
- `tests/unit/simulation/combat/test_fleet_aura_cache.py` -- cache/aggregation tests
- `tests/unit/simulation/combat/test_fleet_aura_register.py` -- register_ship() tests

---

## Task 3.1: Test Fixtures and Helpers [Simple]
**Tests:** N/A (setup only)

- [ ] Create test file with imports: `FleetAuraManager`, `AuraProvider`, `ExternalModifier`, `AbilityScope`
- [ ] Create helper: `_make_ship(team_id, name, alive, derelict, abilities)` -- returns a MagicMock ship with configurable fleet-scope abilities. Each ability tuple: `(ability_name, value, scope, stack_group)`
- [ ] Create helper: `_make_config(team_modifiers, global_modifiers)` -- returns a mock BattleConfig object with `team_modifiers` dict and `global_modifiers` list attributes

**Notes:** [Filled during implementation]

---

## Task 3.2: get_active_bonuses -- Ship Providers [Medium]
**Tests:** `pytest tests/unit/simulation/combat/test_fleet_aura_extended.py -v -k "test_get_active_bonuses"`

- [ ] Write test: `get_active_bonuses(team_id)` returns list of dicts with correct fields: ability, value, source, scope, active (lines 260-272)
- [ ] Write test: only providers from the requested team are included (filter by team_id)
- [ ] Write test: dead ship providers are excluded (`is_alive=False`) (line 264)
- [ ] Write test: derelict ship providers are excluded (`is_derelict=True`) (line 264)
- [ ] Write test: empty result when no providers exist for team
- [ ] Run tests -- confirm they pass

**Notes:** [Filled during implementation]

---

## Task 3.3: get_active_bonuses -- External Modifiers [Simple]
**Tests:** `pytest tests/unit/simulation/combat/test_fleet_aura_extended.py -v -k "test_get_active_bonuses_external"`

- [ ] Write test: external modifier with `team_id=None` (global) appears in results for any team (lines 275-283)
- [ ] Write test: external modifier with specific `team_id` appears only for that team (line 276)
- [ ] Write test: external modifier has scope='external' in result dict (line 280)
- [ ] Write test: mixed ship providers and external modifiers both appear in results
- [ ] Run tests -- confirm they pass

**Notes:** [Filled during implementation]

---

## Task 3.4: External Modifier Loading from BattleConfig [Medium]
**Tests:** `pytest tests/unit/simulation/combat/test_fleet_aura_extended.py -v -k "test_external_modifier"`

- [ ] Write test: `initialize()` with config containing `team_modifiers` loads per-team ExternalModifier entries (lines 78-85)
- [ ] Write test: `initialize()` with config containing `global_modifiers` loads global ExternalModifier entries with `team_id=None` (lines 86-92)
- [ ] Write test: team modifiers are applied to correct team's bonuses during `_recalculate()` (lines 230-233)
- [ ] Write test: global modifiers are applied to ALL teams' bonuses during `_recalculate()` (lines 226-228)
- [ ] Write test: `initialize()` with `config=None` loads no external modifiers (line 77 guard)
- [ ] Run tests -- confirm they pass

**Approach:** Create a mock config object with `team_modifiers = {0: [{'ability': 'ToHitAttackModifier', 'value': 3.0, 'source': 'Nebula'}]}` and `global_modifiers = [{'ability': 'ToHitDefenseModifier', 'value': -2.0, 'source': 'Solar Flare'}]`. Verify bonuses are applied to ships via `fleet_attack_bonus` / `fleet_defense_bonus`.

**Notes:** [Filled during implementation]

---

## Task 3.5: Provider Operational Check in _recalculate() [Medium]
**Tests:** `pytest tests/unit/simulation/combat/test_fleet_aura_extended.py -v -k "test_provider_operational"`

- [ ] Write test: provider ship alive with operational component contributing aura -- bonus applied (baseline, lines 192-205 happy path)
- [ ] Write test: provider ship alive but aura-providing component destroyed (is_operational=False) -- bonus NOT applied (lines 192-205, comp_still_operational=False branch)
- [ ] Write test: provider ship alive, component operational but ability scope changed to SELF -- bonus NOT applied (line 198 check)
- [ ] Write test: provider ship dead (is_alive=False) -- bonus NOT applied (line 188 guard)
- [ ] Run tests -- confirm they pass

**Approach:** Initialize the manager with a provider ship that has a fleet-scope ability. Then modify the component's `is_operational` state and call `update()` to trigger `_recalculate()`. Verify the bonus disappears from team bonuses.

**Notes:** [Filled during implementation]

---

## Task 3.6: _get_provider_fingerprint Edge Cases [Simple]
**Tests:** `pytest tests/unit/simulation/combat/test_fleet_aura_extended.py -v -k "test_fingerprint"`

- [ ] Write test: fingerprint changes when provider ship dies (is_alive changes False) (line 165-166)
- [ ] Write test: fingerprint changes when provider ship becomes derelict (line 166)
- [ ] Write test: fingerprint includes operational component count -- destroying a component changes fingerprint (line 165)
- [ ] Write test: fingerprint for dead provider uses op_count=0 (line 165, else branch)
- [ ] Run tests -- confirm they pass

**Approach:** Call `_get_provider_fingerprint()` directly on the manager instance before and after state changes. Compare tuples to verify change detection.

**Notes:** [Filled during implementation]

---

## Task 3.7: Full Phase Verification [Simple]
**Tests:** `pytest tests/unit/simulation/combat/test_fleet_aura_extended.py -v`

- [ ] Run full new test file -- all tests pass
- [ ] Run existing fleet aura tests: `pytest tests/unit/simulation/combat/test_fleet_aura_cache.py tests/unit/simulation/combat/test_fleet_aura_register.py -v` -- no regressions
- [ ] Run existing simulation tests: `pytest tests/unit/simulation/ -v` -- no regressions
- [ ] Measure coverage: `pytest tests/unit/simulation/combat/test_fleet_aura_extended.py tests/unit/simulation/combat/test_fleet_aura_cache.py tests/unit/simulation/combat/test_fleet_aura_register.py --cov=game/simulation/combat/fleet_aura_manager --cov-report=term-missing`
- [ ] Verify coverage improvement from 79.3% baseline
- [ ] Verify lines 77-92, 161-169, 192-205, 256-285 are now covered

**Notes:** [Filled during implementation]

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to "Complete"
