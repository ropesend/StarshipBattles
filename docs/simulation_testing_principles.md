# Simulation Testing Principles

This document captures lessons learned from troubleshooting and fixing simulation tests in the Combat Lab. Future agents should reference this when working on tests.

---

## Table of Contents

1. [Validation System Overview](#validation-system-overview)
2. [Common Issues and Solutions](#common-issues-and-solutions)
3. [Test-by-Test Troubleshooting Log](#test-by-test-troubleshooting-log)
4. [Key Principles for Future Agents](#key-principles-for-future-agents)

---

## Validation System Overview

### How Validation Works

1. **Validation Rules** are defined in `TestMetadata.validation_rules`:
   - `ExactMatchRule`: Expects exact integer/string match (uses `==`)
   - `DeterministicMatchRule`: Expects floating-point match with tiny tolerance (1e-9)
   - `StatisticalTestRule`: Uses p-value testing for RNG-based outcomes

2. **Validation Context**: Rules access data via dot-notation paths like:
   - `ship.mass` - Ship attribute from extracted data
   - `results.final_velocity_magnitude` - Value stored in scenario.results
   - `low_mass_ship.max_speed` - Custom context added by scenario

3. **Context Building**: The `run_validation()` method builds a context dict:
   ```python
   context = {
       'test_scenario': self,
       'battle_engine': battle_engine,
       'results': self.results,
       'metadata': self.metadata,
       'ship': self._extract_ship_validation_data(self.ship),  # For propulsion tests
       'attacker': self._extract_ship_validation_data(self.attacker),  # For weapon tests
   }
   ```

4. **Path Resolution**: The validation system resolves paths like `ship.mass`:
   - First looks up `ship` in context → gets extracted ship data dict
   - Then looks up `mass` in that dict → gets the float value

5. **Results Storage**: Validation results are stored in `self.results['validation_results']` as a list of dicts.

### Green Checkmark Display

For green "V" checkmarks to appear in Test Details panel:
1. `run_validation()` must be called during `verify()`
2. Condition text must map to a validation rule name in `_is_condition_verified()`
3. The validation must have status 'PASS'

---

## Common Issues and Solutions

### Issue 1: Validation results not showing actual values

**Symptom**: Test fails but shows "Expected: None, Actual: None" for some validations.

**Root Cause**: The validation rule's `path` doesn't resolve to the correct attribute.

**Example**: Path `ship.total_thrust` fails because `_extract_ship_validation_data()` didn't include `total_thrust`.

**Solution**: Update `_extract_ship_validation_data()` in `simulation_tests/scenarios/base.py` to include all needed attributes:
```python
data = {
    'ship': ship,
    'mass': ship.mass,
    'hp': ship.hp,
    'max_hp': ship.max_hp,
    # Propulsion attributes
    'total_thrust': getattr(ship, 'total_thrust', 0.0),
    'max_speed': getattr(ship, 'max_speed', 0.0),
    'acceleration_rate': getattr(ship, 'acceleration_rate', 0.0),
    'turn_speed': getattr(ship, 'turn_speed', 0.0),
}
```

---

### Issue 2: "bad operand type for abs(): 'tuple'" error

**Symptom**: Validation fails with message "bad operand type for abs(): 'tuple'"

**Root Cause**: The validation path points to a tuple value (like `(x, y)` coordinates) but expects a float.

**Example**: `PropulsionScenario` stores velocities in two ways:
- `results['initial_velocity'] = (x, y)` - tuple of coordinates
- `results['initial_velocity_magnitude'] = speed` - float scalar

If the validation rule uses `results.initial_velocity`, it tries to do `abs(tuple - 0.0)` which fails.

**Solution**: Use the `_magnitude` suffix paths for scalar values:
```python
# WRONG - this is a tuple (x, y)
path='results.initial_velocity'

# CORRECT - this is a float
path='results.initial_velocity_magnitude'
```

---

### Issue 3: Validation runs before results are stored

**Symptom**: Validation rules reference keys that exist in `verify()` but return None.

**Root Cause**: The parent template's `verify()` calls `run_validation()` BEFORE the subclass stores its results.

**Example in PropThrusterTurnRateScenario**:
```python
def verify(self, battle_engine):
    super().verify(battle_engine)  # Parent calls run_validation() HERE
    # These values are stored AFTER validation runs - too late!
    self.results['expected_turn_speed'] = self.expected_turn_speed
```

**Solution**: Store results BEFORE calling `super().verify()`:
```python
def verify(self, battle_engine):
    # Store scenario-specific results FIRST
    self.results['expected_turn_speed'] = self.expected_turn_speed
    self.results['actual_turn_speed'] = self.ship.turn_speed

    # NOW call parent (which runs validation)
    try:
        super().verify(battle_engine)
    except NotImplementedError:
        pass
```

---

### Issue 4: Ship JSON expected_stats don't match physics

**Symptom**: Load-time warning like "expected_stats.turn_speed mismatch - JSON says X, ship has Y"

**Root Cause**: The `expected_stats` values in ship JSON were calculated incorrectly.

**Example**: Test_Thruster_Simple.json had `turn_speed: 826.45` but the correct formula result is 414.09.

**Solution**: Recalculate and update the ship JSON:
1. Use the physics formulas with K constants from `physics_constants.py`
2. Update the `expected_stats` section with correct values
3. Update the formula descriptions in `propulsion_details.formulas`

---

### Issue 5: ExactMatchRule fails on floats

**Symptom**: Values that look identical (e.g., 40 vs 40.0) fail exact match.

**Root Cause**: `ExactMatchRule` uses `==` comparison. While Python's `40 == 40.0` is True, some edge cases with floating point may fail.

**Solution**: Use `DeterministicMatchRule` for any floating-point values (even integers stored as floats).

---

## Test-by-Test Troubleshooting Log

### PROP-001: Engine Provides Thrust - Ship Accelerates

**Date**: 2026-01-17

**Initial Status**: FAILING (3 of 4 validations failed)

**Issues Found**:
1. `ship.total_thrust` and `ship.max_speed` paths returned None - `_extract_ship_validation_data()` didn't include propulsion attributes
2. `results.initial_velocity` path returned tuple instead of float

**Fixes Applied**:
1. Added propulsion attributes to `_extract_ship_validation_data()` in base.py
2. Changed path from `results.initial_velocity` to `results.initial_velocity_magnitude`

**Final Status**: PASSING (4/4 validations)

---

### PROP-002: Thrust/Mass Ratio Affects Max Speed

**Date**: 2026-01-17

**Initial Status**: PASSING (all validations worked after PROP-001 fixes)

**Notes**: This test already had its own `run_validation()` override that added ships to context correctly.

**Final Status**: PASSING (10/10 validations)

---

### PROP-003: Thruster Provides Turn Rate

**Date**: 2026-01-17

**Initial Status**: FAILING (2 of 4 validations failed)

**Issues Found**:
1. `results.expected_turn_speed` and `results.actual_turn_speed` returned None
2. Root cause: `verify()` called `super().verify()` first, which ran validation before results were stored

**Fixes Applied**:
1. Moved results storage before `super().verify()` call

**Additional Fix**:
- Fixed Test_Thruster_Simple.json `expected_stats.turn_speed` from 826.45 to 414.09

**Final Status**: PASSING (4/4 validations, no load warnings)

---

### PROP-004: Turn Rate Allows Rotation

**Date**: 2026-01-17

**Initial Status**: PASSING (worked after PROP-001 and PROP-003 fixes)

**Final Status**: PASSING (3/3 validations)

---

### PROP-001b: Ship Without Engine Stays Stationary

**Date**: 2026-01-17

**Initial Status**: FAILING (1 of 5 validations failed)

**Issues Found**:
1. `results.final_velocity` path - same tuple vs magnitude issue as PROP-001

**Fixes Applied**:
1. Changed path from `results.final_velocity` to `results.final_velocity_magnitude`

**Final Status**: PASSING (5/5 validations)

---

### PROP-003b: Thruster-Only Ship Rotates But Cannot Translate

**Date**: 2026-01-17

**Initial Status**: FAILING (1 of 5 validations failed)

**Issues Found**:
1. `results.final_velocity` path - same tuple vs magnitude issue

**Fixes Applied**:
1. Changed path from `results.final_velocity` to `results.final_velocity_magnitude`

**Final Status**: PASSING (5/5 validations)

---

## Key Principles for Future Agents

### 1. Path Naming Convention

When adding validation rules, follow this pattern:
- **Tuples** (coordinates): `results.initial_position`, `results.final_velocity`
- **Scalars** (magnitudes): `results.initial_velocity_magnitude`, `results.final_velocity_magnitude`
- **Ship attributes**: `ship.mass`, `ship.total_thrust`, `ship.max_speed`

### 2. Validation Rule Type Selection

| Data Type | Rule Type | Tolerance |
|-----------|-----------|-----------|
| Integers | `ExactMatchRule` | 0 |
| Strings | `ExactMatchRule` | 0 |
| Floats (deterministic) | `DeterministicMatchRule` | 1e-9 |
| Floats (RNG-based) | `StatisticalTestRule` | p < 0.05 |

### 3. Timing of Results Storage

When implementing `verify()` in a scenario:
```python
def verify(self, battle_engine):
    # 1. Calculate values
    actual_value = self.ship.some_attribute

    # 2. Store ALL results FIRST
    self.results['my_expected'] = self.expected_value
    self.results['my_actual'] = actual_value

    # 3. THEN call parent (which runs validation)
    try:
        super().verify(battle_engine)
    except NotImplementedError:
        pass

    # 4. Return pass/fail
    return actual_value == self.expected_value
```

### 4. Debugging Validation Failures

When a validation shows "Expected: None, Actual: None":
1. Check if the path exists in the context dict
2. Check if `_extract_ship_validation_data()` includes the needed attribute
3. Check if the value is stored in `self.results` before `run_validation()` is called
4. Check if you're using tuple path vs magnitude path

### 5. Ship JSON Validation

When creating test ships:
1. Calculate `expected_stats` using the physics formulas
2. Use exact floating-point values (not rounded)
3. Test the ship loads without warnings

### 6. Context Structure

The validation context has this structure:
```python
{
    'test_scenario': <TestScenario instance>,
    'battle_engine': <BattleEngine instance>,
    'results': {
        'ticks_run': 100,
        'initial_velocity_magnitude': 0.0,
        'final_velocity_magnitude': 156.25,
        'distance_traveled': 46406.25,
        # ... more results
    },
    'metadata': <TestMetadata>,
    'ship': {  # From _extract_ship_validation_data()
        'ship': <Ship object>,
        'mass': 40.0,
        'hp': 100,
        'max_hp': 100,
        'total_thrust': 500.0,
        'max_speed': 312.5,
        # ... more attributes
    }
}
```

### 7. Load-Time Validation

Ship JSONs with `expected_stats` are validated at load time. Mismatches produce warnings but don't fail the test. However:
- Warnings indicate the test data is wrong
- Fix the JSON to match actual physics calculations
- Use the same K constants as the game (`K_SPEED`, `K_THRUST`, `K_TURN`)
