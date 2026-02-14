# Test Coverage Analysis Report: game/simulation/

**Generated:** 2026-02-13
**Scope:** `game/simulation/` directory (all subdirectories)
**Test Files Analyzed:** 75+ test files in `tests/unit/simulation/`

---

## Summary

The `game/simulation/` directory has **strong overall test coverage** with 2406+ test functions across 75 files. Most critical systems are well-tested. However, several coverage gaps exist in edge cases and some modules have thin test coverage.

**Strengths:**
- Comprehensive damage calculation tests (47+ tests with weighted distribution, armor types, layer propagation)
- Excellent projectile management coverage (60+ tests including collision, guidance, interception)
- Strong weapon ability integration tests (28+ tests covering modifiers, formulas, geometry)
- Good BattleEngine tick processing coverage (49+ tests)
- Ship physics mixin fully tested (43+ tests)

**Key Gaps Identified:**
- Missing integration tests for full combat scenarios (damage -> ability loss -> stat recalculation)
- Some ability classes lack isolation tests (defense abilities, crew abilities)
- BattleLogger has tests but not in simulation test folder
- Formula system exception handling could use more edge case coverage
- Resource consumption during combat tick flow undertested

---

## Findings

#### MEDIUM: Missing integration tests for component destruction cascading effects

**Location:** `game/simulation/combat/damage_calculator.py` + `game/simulation/entities/ship_stats.py`

**Issue:** While damage calculator tests component HP reduction, there are no integration tests verifying that:
1. Component destruction triggers ability removal
2. Ship stats recalculation after component loss correctly updates aggregated values
3. The full cascade: damage -> component destroyed -> ability lost -> stats recalculated -> combat behavior changes

**Production Code:**
```python
# damage_calculator.py line 156
ship.recalculate_stats()
ship.update_derelict_status()
```

**Test Gap:** No test verifies the full cascade from damage through to stat recalculation effects.

**Recommendation:** Add integration tests that:
- Apply damage to destroy a propulsion component, verify thrust drops to zero
- Destroy a weapon component, verify fire_weapons returns fewer projectiles
- Destroy shield generator, verify max_shields drops

---

#### LOW: Defense ability classes undertested in isolation

**Location:** `game/simulation/components/abilities/defense.py`

**Issue:** The defense ability classes (`ShieldProjection`, `ShieldRegeneration`, `ToHitAttackModifier`, `ToHitDefenseModifier`, `EmissiveArmor`) have integration tests but lack isolation unit tests for individual methods.

**Missing Tests:**
- `EmissiveArmor.recalculate()` - currently a pass statement, no test verifies it
- `ToHitDefenseModifier.get_ui_rows()` formatting edge cases
- `ShieldRegeneration` with zero base_rate behavior

**Existing Coverage:** `tests/unit/simulation/components/abilities/test_defense_integration.py` (36 tests) covers modifier stacking but not class-level edge cases.

**Recommendation:** Add `test_defense_isolation.py` with:
- Tests for each ability's `__init__` parameter handling
- Tests for `get_primary_value()` return values
- Tests for `recalculate()` with various modifier combinations

---

#### LOW: Crew ability classes have minimal test coverage

**Location:** `game/simulation/components/abilities/crew.py`

**Issue:** The crew ability module contains `CrewCapacity` and `LifeSupportCapacity` abilities. While these are tested indirectly through ship validation tests, they lack direct unit tests.

**Missing Tests:**
- Direct tests for `CrewCapacity.get_primary_value()`
- `LifeSupportCapacity` initialization and stat binding
- Edge cases for crew-related abilities when capacity is zero

**Recommendation:** Create `test_crew_abilities.py` with direct tests for crew-related ability classes.

---

#### MEDIUM: Resource consumption during combat tick flow lacks end-to-end testing

**Location:** `game/simulation/systems/resource_manager.py` + `game/simulation/components/component.py`

**Issue:** Resource consumption is tested in isolation (`test_resource_manager_edge_cases.py`) but the full combat tick flow:
1. Weapon fires -> consumes energy
2. Engine thrusts -> consumes fuel
3. Shield regenerates -> consumes energy
4. Component disabled when resources depleted

...lacks end-to-end integration tests.

**Production Code Flow:**
```python
# component.py consume_activation()
def consume_activation(self):
    for ability in self.ability_instances:
        if isinstance(ability, ResourceConsumption):
            # Consume from ship resources
```

**Recommendation:** Add integration test that:
- Creates ship with limited energy
- Fires weapons until energy depleted
- Verifies weapons stop firing when out of energy

---

#### LOW: BattleLogger tests exist but outside simulation test folder

**Location:** `tests/unit/combat/test_battle_logger.py` (not in `tests/unit/simulation/`)

**Issue:** `BattleLogger` is defined in `game/simulation/systems/battle_engine.py` but its tests are in `tests/unit/combat/`, creating folder structure inconsistency.

**Recommendation:** Either:
- Move tests to `tests/unit/simulation/systems/test_battle_logger.py`, or
- Extract `BattleLogger` to its own module if it's used outside simulation

---

#### LOW: Formula system exception handling edge cases

**Location:** `game/simulation/formula_system.py`

**Issue:** While `test_formula_exceptions.py` exists with 16 tests, some edge cases are not covered:
- Division by zero in formulas
- Very large numbers causing overflow
- Nested parentheses edge cases
- Empty formula strings

**Existing Tests:** `tests/unit/simulation/test_formula_exceptions.py` (16 tests)
**Related Tests:** `tests/unit/systems/test_formula_overflow_underflow.py`

**Recommendation:** Ensure simulation-specific formula usage edge cases are covered.

---

#### LOW: ShipStatQuerier class lacks dedicated tests

**Location:** `game/simulation/entities/ship_stat_querier.py`

**Issue:** The `ShipStatQuerier` class provides stat querying utilities but has no dedicated test file. It may be tested indirectly through ship tests.

**Recommendation:** Add `test_ship_stat_querier.py` with tests for all public methods.

---

#### LOW: ship_serialization module could use error path testing

**Location:** `game/simulation/entities/ship_serialization.py`

**Issue:** `test_ship_serialization.py` has 58 tests for successful serialization paths but limited testing of error paths:
- Corrupt data handling
- Missing required fields
- Invalid component references

**Recommendation:** Add tests for serialization error paths and data validation failures.

---

## Top 5 Priority Issues

1. **MEDIUM: Component destruction cascade integration tests** - Critical for ensuring damage correctly impacts ship capabilities
2. **MEDIUM: Resource consumption combat flow end-to-end tests** - Important for verifying resource economy works correctly in battle
3. **LOW: Defense ability isolation tests** - Minor gap but ensures ability classes work correctly
4. **LOW: Crew ability unit tests** - Ensures crew mechanics are properly tested
5. **LOW: ShipStatQuerier dedicated tests** - Utility class should have explicit coverage

---

## Module Coverage Summary

| Module | Test File Exists | Test Count | Coverage Assessment |
|--------|------------------|------------|---------------------|
| `battle_engine.py` | Yes | 65+ | Strong |
| `damage_calculator.py` | Yes | 47+ | Strong |
| `projectile_manager.py` | Yes | 60+ | Strong |
| `targeting_system.py` | Yes | 34+ | Strong |
| `weapon_firing_system.py` | Yes | 28+ | Good |
| `ship_physics.py` | Yes | 43+ | Strong |
| `resource_manager.py` | Yes | 15+ | Good |
| `ship_stats.py` | Yes | 14+ | Adequate |
| `ship_formation.py` | Yes | 76+ | Strong |
| `component.py` | Partial | Varies | Tested via integration |
| `abilities/weapons.py` | Yes | 77+ | Strong |
| `abilities/defense.py` | Partial | 36+ | Integration only |
| `validation/*.py` | Yes | 50+ | Good |

---

## Notes

- Test baseline: 8155+ passing tests project-wide
- Simulation tests: ~2406 test functions across 75 files
- pytest-xdist used for parallel execution (12 workers CLI, 4 VS Code)
- Test monitor (`--testmon`) available for incremental runs
