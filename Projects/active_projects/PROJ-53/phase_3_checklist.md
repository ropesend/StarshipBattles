# Phase 3: Fix Production Code Breakage

**Objective:** Fix all production code that broke due to legacy pattern removal.

**Prerequisite:** Phase 1-2 complete

---

## Tasks

### 3.1 Fix UI Renderer - Direct Property Access
**File:** `game/ui/renderer/renderer.py` (lines 171-177)

- [ ] Replace `ship.current_fuel` with `ship.resources.get_value('fuel')`
- [ ] Replace `ship.max_fuel` with `ship.resources.get_max_value('fuel')`
- [ ] Replace `ship.current_energy` with `ship.resources.get_value('energy')`
- [ ] Replace `ship.max_energy` with `ship.resources.get_max_value('energy')`
- [ ] Replace `ship.current_ammo` with `ship.resources.get_value('ammo')`
- [ ] Replace `ship.max_ammo` with `ship.resources.get_max_value('ammo')`
- [ ] Handle case where resource doesn't exist (return 0)

### 3.2 Fix Fleet Report Window
**File:** `game/ui/screens/fleet_report_window.py` (lines 654-665)

- [ ] Replace `stats['max_fuel']` with resource-based access
- [ ] Replace `stats['total_fuel']` with resource-based access
- [ ] Replace `stats['max_energy']` with resource-based access
- [ ] Replace `stats['total_energy']` with resource-based access
- [ ] Update any other legacy stat keys

### 3.3 Fix Fleet Report Filters
**File:** `game/ui/screens/fleet_report_filters.py` (lines 44-97)

- [ ] Replace hardcoded fuel tracking with resource-based tracking
- [ ] Update filter logic to use resources container

### 3.4 Fix Ship Combat Engine - Shield Regen
**File:** `game/simulation/entities/ship_combat_engine.py` (lines 174-191)

- [ ] Refactor shield regen to use ResourceConsumption ability check
- [ ] Or: Keep direct energy consumption but use `ship.resources.get_resource('energy').consume()`
- [ ] Ensure shield regen respects energy availability

### 3.5 Fix Combat Endurance Calculation
**File:** `game/simulation/entities/combat_endurance.py` (lines 17-105)

- [ ] Remove/refactor `ship.fuel_consumption` calculation
- [ ] Remove/refactor `ship.energy_consumption` calculation
- [ ] Remove/refactor `ship.ammo_consumption` calculation
- [ ] Calculate consumption rates from ResourceConsumption abilities
- [ ] Store results appropriately for UI access

### 3.6 Fix Ship Stats - Legacy Ability Handling
**File:** `game/simulation/entities/ship_stats.py`

- [ ] Remove references to `ShipRepair` ability (or define it)
- [ ] Remove references to `CrystallineArmor` ability (or define it)
- [ ] Remove references to `AmmoGeneration` ability (use ResourceGeneration)
- [ ] Remove any legacy ability name checks
- [ ] Ensure all stat aggregation uses modern ability classes

### 3.7 Fix Ship Serialization
**File:** `game/simulation/entities/ship_serialization.py`

- [ ] Update serialization to use `ship.resources.get_value()` for current values
- [ ] Update serialization to use `ship.resources.get_max_value()` for max values
- [ ] Ensure deserialization sets resources correctly
- [ ] Remove any legacy property serialization

### 3.8 Fix Builder Stats Config
**File:** `game/ui/screens/builder/stats_config.py`

- [ ] Verify dynamic resource discovery still works
- [ ] Update any hardcoded resource name references
- [ ] Fix any legacy ability name checks

### 3.9 Run Production Code Tests
- [ ] Run `pytest tests/unit/` - document remaining failures
- [ ] Run `pytest tests/integration/` - document remaining failures
- [ ] All production-related tests should pass after this phase

---

## Common Fix Patterns

### Direct Property Access
```python
# BEFORE
fuel_pct = ship.current_fuel / ship.max_fuel

# AFTER
max_fuel = ship.resources.get_max_value('fuel')
fuel_pct = ship.resources.get_value('fuel') / max_fuel if max_fuel > 0 else 0
```

### Stats Dictionary Access
```python
# BEFORE
total_fuel = stats['max_fuel']

# AFTER
total_fuel = stats.get('resource_storage', {}).get('fuel', 0)
# Or update stats calculator to provide in expected format
```

### Consumption Calculation
```python
# BEFORE
ship.fuel_consumption = some_calculation()

# AFTER
# Aggregate from ResourceConsumption abilities
fuel_consumption = sum(
    ab.amount for ab in ship.get_abilities('ResourceConsumption')
    if ab.resource_name == 'fuel' and ab.trigger == 'constant'
)
```

---

## Files Modified
- `game/ui/renderer/renderer.py`
- `game/ui/screens/fleet_report_window.py`
- `game/ui/screens/fleet_report_filters.py`
- `game/simulation/entities/ship_combat_engine.py`
- `game/simulation/entities/combat_endurance.py`
- `game/simulation/entities/ship_stats.py`
- `game/simulation/entities/ship_serialization.py`
- `game/ui/screens/builder/stats_config.py`

---

## Verification

After this phase:
```bash
# Should return ZERO in production code
grep -rn "\.current_fuel" game/ --include="*.py"
grep -rn "\.max_fuel" game/ --include="*.py"
grep -rn "\.current_energy" game/ --include="*.py"
grep -rn "\.max_energy" game/ --include="*.py"

# Production tests should pass
pytest tests/unit/simulation/ tests/unit/ui/ -v
```

---

## Notes

- Add null checks for resources that might not exist
- Consider adding helper methods to Ship class if access pattern is verbose
- Keep combat endurance calculation working for UI display
