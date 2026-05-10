# Phase 1: Remove Compatibility Layer

**Objective:** Delete all legacy shortcut factories and mappings. This WILL break things.

**Expected Outcome:** Tests fail, JSON loading fails, runtime errors. This is intentional.

**Status:** Complete

---

## Tasks

### 1.1 Remove Lambda Factories from abilities/__init__.py
- [x] Delete `"FuelStorage"` lambda factory (line ~82)
- [x] Delete `"EnergyStorage"` lambda factory (line ~83)
- [x] Delete `"AmmoStorage"` lambda factory (line ~84)
- [x] Delete `"EnergyGeneration"` lambda factory (line ~85)
- [x] Delete `"EnergyConsumption"` lambda factory (line ~86)
- [x] Delete `"AmmoConsumption"` lambda factory (line ~87)

### 1.2 Remove ABILITY_CLASS_MAP Entries
- [x] Delete `"FuelStorage": "ResourceStorage"` mapping (line ~92)
- [x] Delete `"EnergyStorage": "ResourceStorage"` mapping (line ~93)
- [x] Delete `"AmmoStorage": "ResourceStorage"` mapping (line ~94)
- [x] Delete `"EnergyGeneration": "ResourceGeneration"` mapping (line ~95)
- [x] Delete `"EnergyConsumption": "ResourceConsumption"` mapping (line ~96)
- [x] Delete `"AmmoConsumption": "ResourceConsumption"` mapping (line ~97)

### 1.3 Remove Legacy Handling from ship_stats_calculator.py
- [x] Delete `if 'FuelStorage' in abilities:` block (lines ~203-204)
- [x] Delete `if 'EnergyStorage' in abilities:` block (lines ~206-207)
- [x] Delete `if 'AmmoStorage' in abilities:` block (lines ~209-210)
- [x] Delete any other legacy ability name checks

### 1.4 Remove Legacy Handling from ability_aggregator.py
- [x] Delete BUG-08 FuelStorage alias code (lines ~116-123)
- [x] Delete FuelStorage alias in calculate_ability_totals_for_layer (lines ~237-244)
- [x] Remove any other legacy ability name references

### 1.5 Run Tests to Identify Breakage
- [x] Run `pytest tests/` to find all failures
- [x] Document all failing test files
- [x] Document all error types

---

## Breakage Report

**14 tests failed** (5897 passed, 5 skipped)

### Failing Tests:
1. `tests/unit/combat/test_combat_endurance.py::TestCombatEndurance::test_energy_endurance_drain`
2. `tests/unit/combat/test_combat_endurance.py::TestCombatEndurance::test_energy_recharge`
3. `tests/unit/combat/test_shields.py::TestShields::test_stats_init`
4. `tests/unit/combat/test_shields.py::TestShields::test_regeneration`
5. `tests/unit/combat/test_shields.py::TestShields::test_energy_starvation`
6. `tests/unit/entities/test_abilities.py::TestAbilities::test_create_ability_primitives`
7. `tests/unit/strategy/ship_stats/test_basics.py::TestStatAggregation::test_fuel_storage_aggregation`
8. `tests/unit/strategy/ship_stats/test_basics.py::TestIntegrationScenarios::test_escort_with_warp_drive`
9. `tests/unit/strategy/ship_stats/test_modifiers.py::TestModifierApplication::test_scaled_battery_energy_capacity`
10. `tests/unit/strategy/ship_stats/test_modifiers.py::TestModifierApplication::test_multiple_small_vs_one_large_battery`
11. `tests/unit/strategy/ship_stats/test_modifiers.py::TestModifierApplication::test_warp_capability_with_scaled_battery`
12. `tests/unit/strategy/ship_stats/test_modifiers.py::TestModifierApplication::test_no_modifiers_uses_base_values`
13. `tests/unit/strategy/ship_stats/test_toggles.py::TestComponentToggles::test_toggled_off_resource_storage_not_counted`
14. `tests/repro_issues/test_bug_05_deep_repro.py::test_shield_regen_consumption`

### Error Types:
- **Assertion failures**: Tests using legacy ability names in fixtures
- **Missing abilities**: Tests expecting EnergyStorage/FuelStorage to work

---

## Files Modified
- `game/simulation/components/abilities/__init__.py`
- `game/strategy/services/ship_stats_calculator.py`
- `game/simulation/entities/ability_aggregator.py`

---

## Verification

```bash
# Legacy factories are gone:
grep -n "FuelStorage" game/simulation/components/abilities/__init__.py  # Returns nothing
grep -n "EnergyStorage" game/simulation/components/abilities/__init__.py  # Returns nothing
```

---

## Notes

- Phase 1 complete - compatibility layer removed
- 14 test failures as expected - proceed to Phase 2 to fix JSON configs
- Some failures are in test fixtures using legacy patterns directly
