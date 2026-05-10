# Test Coverage Gap Analysis: game/simulation/

**Sweep Agent Report**
**Date:** 2026-02-13
**Scope:** `game/simulation/` and all subdirectories
**Cross-reference:** `tests/unit/simulation/`, `tests/integration/`, `simulation_tests/`

---

## Executive Summary

The simulation layer has **strong test coverage** overall, with 70+ production files mapped to corresponding test files. The combat subsystem (damage calculator, targeting system, weapon firing) is particularly well-tested with comprehensive unit tests. However, several gaps exist in edge case coverage, integration testing, and newly extracted modules.

**Overall Assessment:** GOOD coverage with specific gaps to address

---

## Finding Categories

### CRITICAL: Core Game Logic Without Coverage

#### 1. [CRITICAL] `combat_endurance.py` - No Direct Unit Tests
**File:** `C:\Dev\Starship Battles\game\simulation\entities\combat_endurance.py`

**Description:** The `calculate_combat_endurance()` function computes critical ship statistics including:
- Fuel, ammo, and energy consumption rates
- Endurance times (how long ship can fight)
- DPS calculations for weapons
- Energy recharge time
- Cached summary statistics

**Gap:** No dedicated test file exists for this module. The function is tested indirectly through ShipStatsCalculator tests, but:
- No tests for edge cases (zero consumption, infinite endurance)
- No tests for activation-based consumption rate conversion
- No tests for energy net calculation (positive vs negative)
- No tests for `_calculate_cached_summary()` accuracy

**Impact:** Endurance calculations affect AI decision-making and UI display.

**Recommendation:**
```
Create: tests/unit/simulation/entities/test_combat_endurance.py
Test cases needed:
- Zero consumption = infinite endurance
- Negative energy net = drain endurance
- Positive energy net = infinite energy endurance
- DPS calculation accuracy
- Activation trigger rate conversion
```

---

#### 2. [CRITICAL] `ship_stats.py` - ShipStatsCalculator Phase Methods Not Directly Tested
**File:** `C:\Dev\Starship Battles\game\simulation\entities\ship_stats.py`

**Description:** While `test_ship_stats_calculator_phases.py` exists, it tests phases at a high level. The following internal methods lack direct unit tests:

- `_aggregate_resource_abilities()` - Resource storage/generation aggregation
- `_aggregate_propulsion_abilities()` - Thrust, strategic movement, warp
- `_aggregate_defense_abilities()` - Armor HP pool, shields, shield regen
- `_aggregate_hangar_abilities()` - Vehicle launch, storage, cycle time

**Gap:** These private methods contain complex aggregation logic that should be tested in isolation.

**Impact:** Bugs in aggregation affect all ship stat calculations.

**Recommendation:** Add focused tests for each aggregation helper method.

---

### MAJOR: Public APIs Without Tests

#### 3. [MAJOR] `WarpJump` Ability - Incomplete Test Coverage
**File:** `C:\Dev\Starship Battles\game\simulation\components\abilities\propulsion.py`

**Description:** The `WarpJump` ability class has:
- `can_jump(ship_mass)` method - checks if ship is light enough to use warp drive
- `max_tonnage` and `energy_cost` attributes

**Gap:** No tests found for:
- `can_jump()` boundary conditions (exactly at limit, just under, just over)
- Energy cost handling during warp transit
- UI row generation for warp capabilities

**File Search:** Grep for "WarpJump" in tests found only snapshot files, no unit tests.

**Recommendation:**
```python
# Add to tests/unit/simulation/components/abilities/test_propulsion.py
class TestWarpJump:
    def test_can_jump_under_limit(self): ...
    def test_can_jump_at_limit(self): ...
    def test_can_jump_over_limit_returns_false(self): ...
    def test_energy_cost_zero_default(self): ...
```

---

#### 4. [MAJOR] `StrategicMovement` Ability - No Scope Testing
**File:** `C:\Dev\Starship Battles\game\simulation\components\abilities\propulsion.py`

**Description:** The `StrategicMovement` ability supports multiple scopes:
- `AbilityScope.SELF` (default)
- `AbilityScope.ALLIED_SECTOR` (tug boost)
- `AbilityScope.ALLIED_SYSTEM` (orbital array)

**Gap:** No tests verify:
- Scope parsing from JSON data
- Scope validation (reject invalid scopes)
- Movement point aggregation with different scopes

**Recommendation:** Add scope-specific tests similar to existing ability base tests.

---

#### 5. [MAJOR] `SimulationDesignLoader` - Error Path Testing
**File:** `C:\Dev\Starship Battles\game\simulation\services\design_loader.py`

**Description:** `test_simulation_design_loader.py` exists but examination shows minimal error path coverage.

**Gap:** Missing tests for:
- Invalid JSON file handling (malformed JSON)
- Missing required fields in design data
- OSError during file I/O
- Registries validation (None registries)

**Impact:** Silent failures when loading corrupted design files.

**Recommendation:** Add pytest.raises tests for each error branch.

---

### MINOR: Missing Edge Cases

#### 6. [MINOR] `BeamWeaponAbility.calculate_hit_chance()` - Boundary Conditions
**File:** `C:\Dev\Starship Battles\game\simulation\components\abilities\weapons.py`

**Description:** The sigmoid hit chance calculation has specific boundary handling:
```python
clamped_score = max(-20.0, min(20.0, net_score))
```

**Gap:** No tests for:
- Extreme net_score values (very high/low)
- OverflowError handling
- Score clamping at boundaries

**Existing Coverage:** Basic hit chance calculation tested in `test_weapons_isolation.py`.

**Recommendation:** Add boundary tests for sigmoid function extremes.

---

#### 7. [MINOR] `ResourceRegistry.has_sufficient()` Not Tested at Zero
**File:** `C:\Dev\Starship Battles\game\simulation\systems\resource_manager.py`

**Description:** `test_resource_manager_edge_cases.py` has good coverage but misses:
- `has_sufficient(0)` - should always return True
- `has_sufficient(negative)` - undefined behavior

**Recommendation:** Add explicit zero and negative amount tests.

---

#### 8. [MINOR] `ShipValidatorHelper` - Validation Warning Coverage
**File:** `C:\Dev\Starship Battles\game\simulation\entities\ship_validator_helper.py`

**Description:** `test_ship_validator_helper.py` exists in `tests/unit/entities/` but doesn't test:
- `get_validation_warnings()` return format
- Warning vs error distinction
- Multiple concurrent validation issues

**Recommendation:** Add tests for warning aggregation.

---

#### 9. [MINOR] `ShipStatQuerier.max_weapon_range` - SeekerWeapon Range Fallback
**File:** `C:\Dev\Starship Battles\game\simulation\entities\ship_stat_querier.py`

**Description:** The property calculates seeker range from `projectile_speed * endurance` when range is 0.

**Gap:** No test for this fallback calculation.

**Recommendation:**
```python
def test_max_weapon_range_seeker_fallback_calculation():
    # SeekerWeapon with range=0, speed=500, endurance=10
    # Expected: 500 * 10 = 5000
```

---

### INFO: Test Organization Suggestions

#### 10. [INFO] Consolidate Ship Entity Tests
**Current State:** Ship-related tests are spread across:
- `tests/unit/entities/`
- `tests/unit/simulation/entities/`
- `tests/unit/simulation/ship_combat_engine/`

**Suggestion:** Consider consolidating under `tests/unit/simulation/entities/` for clarity.

---

#### 11. [INFO] Missing `__init__.py` in Some Test Directories
**Observation:** Some test directories lack `__init__.py`, which can cause pytest collection issues.

**Affected:**
- `tests/unit/simulation/abilities/` - has `__init__.py` but incomplete
- `tests/unit/simulation/managers/` - structure OK

---

#### 12. [INFO] Integration Test Gap: Combat-to-Strategy Transition
**Observation:** No integration tests verify:
- Ship state preservation after battle ends
- Damage/resource state carrying over to strategy layer
- Combat result affecting fleet status

**Location:** Should be in `tests/integration/fleet_combat/`

---

## Coverage Verification Summary

### Well-Tested Modules (ACCEPTABLE)

| Module | Test File | Coverage Notes |
|--------|-----------|----------------|
| `combat/damage_calculator.py` | `test_damage_calculator.py` | ~1160 lines, comprehensive |
| `combat/targeting_system.py` | `test_targeting_system.py` | ~914 lines, comprehensive |
| `combat/weapon_firing_system.py` | `test_weapon_firing_system.py` | ~1294 lines, comprehensive |
| `components/abilities/base.py` | `test_ability_base.py` | ~863 lines, excellent |
| `components/abilities/weapons.py` | `test_weapons_isolation.py` | Good isolation tests |
| `components/modifier_manager.py` | `test_modifier_manager.py` | Covers modifier application |
| `systems/resource_manager.py` | `test_resource_manager_edge_cases.py` | Edge cases covered |
| `systems/battle_engine.py` | `test_battle_engine_tick.py` | Tick processing tested |
| `entities/ship_stats.py` | `test_ship_stats_calculator_phases.py` | Phase orchestration tested |

### Modules Requiring Attention

| Module | Issue | Priority |
|--------|-------|----------|
| `entities/combat_endurance.py` | No dedicated test file | CRITICAL |
| `components/abilities/propulsion.py` (WarpJump) | No unit tests | MAJOR |
| `components/abilities/propulsion.py` (StrategicMovement) | No scope tests | MAJOR |
| `services/design_loader.py` | Error paths not tested | MAJOR |
| `entities/ship_stat_querier.py` | Seeker range fallback not tested | MINOR |

---

## Recommended Actions

### Immediate (CRITICAL/MAJOR)

1. **Create `test_combat_endurance.py`** - New test file for endurance calculations
2. **Add WarpJump tests to propulsion abilities** - Boundary conditions for can_jump()
3. **Add StrategicMovement scope tests** - Verify multi-scope behavior
4. **Expand design loader error tests** - All exception paths

### Near-term (MINOR)

5. **Add sigmoid boundary tests** for BeamWeaponAbility
6. **Add zero/negative amount tests** for ResourceRegistry
7. **Add SeekerWeapon range fallback test** to ship stat querier tests

### Future (INFO)

8. **Consider test directory consolidation** for ship entities
9. **Add combat-strategy integration tests** for state transitions

---

## Methodology Notes

**Phase 1:** Mapped 72 production files in `game/simulation/` to ~90 test files in `tests/unit/simulation/`, `tests/integration/`, and `simulation_tests/`.

**Phase 2:** Analyzed public APIs in tested files, checking method signatures against test coverage.

**Phase 3:** Traced critical paths through damage calculation, ability stacking, and combat tick processing.

**Phase 4:** Reviewed test quality - most tests have proper assertions, minimal heavy mocking.

**Phase 5:** Checked integration tests - good coverage for save/load, turn engine, but combat-strategy gaps.

**Phase 6:** Identified missing boundary tests and error recovery scenarios.

---

*Report generated by Sweep Agent*
