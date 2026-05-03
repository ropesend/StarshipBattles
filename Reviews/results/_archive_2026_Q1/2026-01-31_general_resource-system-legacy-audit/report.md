# Resource System Legacy Audit Report

**Date:** 2026-01-31
**Type:** General Review (Targeted Audit)
**Objective:** Identify ALL legacy/hardcoded resource system usage for migration to generic `ResourceConsumption` pattern

---

## Executive Summary

### Overall Finding: System is PARTIALLY MIGRATED

The codebase has **two parallel resource systems** running:
1. **Modern Generic System** - `ResourceConsumption`, `ResourceStorage`, `ResourceGeneration` abilities with resource type parameter
2. **Legacy Shortcut System** - `EnergyStorage`, `FuelStorage`, `AmmoStorage`, `EnergyConsumption`, `EnergyGeneration`, `AmmoGeneration` as ability names

A **compatibility layer** in `game/simulation/components/abilities/__init__.py` automatically converts legacy patterns to modern ones at runtime. However, eliminating legacy patterns entirely requires updates across **50+ files**.

### Statistics

| Category | Count |
|----------|-------|
| **Legacy ability name occurrences** | ~75 |
| **Hardcoded resource property access** | ~40 |
| **Files requiring migration** | 50+ |
| **Critical priority files** | 15 |
| **Test files with legacy patterns** | 25+ |

---

## Priority Findings

### CRITICAL - Must Fix (Production Code)

#### 1. Direct Ship Property Access (BREAKING)
**Files:**
- [renderer.py:171-177](game/ui/renderer/renderer.py#L171-L177) - `ship.current_fuel`, `ship.max_fuel`, `ship.current_energy`, etc.
- [fleet_report_window.py:654-665](game/ui/screens/fleet_report_window.py#L654-L665) - `stats['max_fuel']`, `stats['total_fuel']`
- [fleet_report_filters.py:44-97](game/ui/screens/fleet_report_filters.py#L44-L97) - Hardcoded fuel tracking

**Issue:** Direct access to legacy ship properties instead of `ship.resources.get_value('fuel')`

#### 2. Hardcoded Shield Regeneration
**File:** [ship_combat_engine.py:174-191](game/simulation/entities/ship_combat_engine.py#L174-L191)

**Issue:** Shield regen logic manually consumes energy outside ability system:
```python
if cost_amount > 0 and hasattr(ship, 'resources'):
    energy_res = ship.resources.get_resource('energy')
    if energy_res.current_value >= cost_amount:
        energy_res.consume(cost_amount)
```

**Should use:** ResourceConsumption ability with proper trigger

#### 3. Combat Endurance Hardcoded Calculation
**File:** [combat_endurance.py:17-105](game/simulation/entities/combat_endurance.py#L17-L105)

**Issue:** `ship.fuel_consumption`, `ship.energy_consumption`, `ship.ammo_consumption` are calculated and stored as direct ship attributes instead of aggregating from ResourceConsumption abilities.

#### 4. Missing Ability Definitions
**File:** [ship_stats.py:402-411](game/simulation/entities/ship_stats.py#L402-L411)

**Missing abilities referenced but never defined:**
- `ShipRepair`
- `CrystallineArmor`
- `AmmoGeneration`

#### 5. Strategic Fuel Cost Methods
**Files:**
- [ship_instance.py:246,298](game/strategy/data/ship_instance.py#L246) - `get_fuel_cost_per_hex()`, `get_warp_fuel_cost()`
- [fleet.py:144-427](game/strategy/data/fleet.py#L144-L427) - Fleet fuel calculations

**Issue:** Hardcoded fuel cost methods instead of reading from `resource_consumption_per_hex['fuel']`

---

### HIGH - Legacy Ability Shortcuts in Data

#### JSON Configuration Files

| File | Legacy Patterns | Count |
|------|-----------------|-------|
| [data/components.json](data/components.json) | `EnergyConsumption`, `AmmoGeneration` | 5 |
| [simulation_tests/data/components.json](simulation_tests/data/components.json) | `FuelStorage`, `AmmoStorage`, `EnergyStorage`, `EnergyConsumption` | 12 |
| [tests/unit/data/test_components.json](tests/unit/data/test_components.json) | `EnergyGeneration`, `FuelStorage`, `AmmoStorage`, `EnergyStorage` | 5 |

#### Python Code - Ability Registry
**File:** [abilities/__init__.py:82-97](game/simulation/components/abilities/__init__.py#L82-L97)

Contains shortcut factory lambdas:
```python
"FuelStorage": lambda c, d: ResourceStorage(c, {"resource": "fuel", "amount": d}...)
"EnergyStorage": lambda c, d: ResourceStorage(c, {"resource": "energy", "amount": d}...)
"AmmoStorage": lambda c, d: ResourceStorage(c, {"resource": "ammo", "amount": d}...)
"EnergyGeneration": lambda c, d: ResourceGeneration(c, {"resource": "energy", "amount": d}...)
"EnergyConsumption": lambda c, d: ResourceConsumption(c, {"resource": "energy", "amount": d, "trigger": "constant"}...)
```

These work but should be deprecated once all data migrated.

---

### MEDIUM - Stats Calculator Legacy Handling

**File:** [ship_stats_calculator.py:203-215](game/strategy/services/ship_stats_calculator.py#L203-L215)

Explicit checks for legacy shortcut abilities:
```python
if 'FuelStorage' in abilities:
    resource_storage['fuel'] = abilities['FuelStorage']
if 'EnergyStorage' in abilities:
    resource_storage['energy'] = abilities['EnergyStorage']
if 'AmmoStorage' in abilities:
    resource_storage['ammo'] = abilities['AmmoStorage']
```

---

### MEDIUM - Test Files with Legacy Patterns

| Test File | Pattern | Count |
|-----------|---------|-------|
| [test_combat_endurance.py](tests/unit/combat/test_combat_endurance.py) | `abilities={'EnergyGeneration': ...}` | 4 |
| [test_modifiers.py](tests/unit/strategy/ship_stats/test_modifiers.py) | `abilities={'EnergyStorage': 2000}` | 8 |
| [test_basics.py](tests/unit/strategy/ship_stats/test_basics.py) | `abilities={'FuelStorage': 10000}` | 3 |
| [test_warp.py](tests/unit/strategy/ship_stats/test_warp.py) | Various legacy patterns | 6 |
| [test_abilities.py](tests/unit/entities/test_abilities.py) | `create_ability("FuelStorage", ...)` | 2 |

---

## Legacy Pattern Inventory

### By Pattern Type

#### 1. String Literal Ability Names (75 occurrences)
- `"EnergyStorage"` - 14 occurrences
- `"FuelStorage"` - 12 occurrences
- `"AmmoStorage"` - 8 occurrences
- `"EnergyGeneration"` - 15 occurrences
- `"EnergyConsumption"` - 14 occurrences
- `"AmmoGeneration"` - 3 occurrences
- `"Fuel Storage"` (warning text) - 6 occurrences
- `"Energy Storage"` (warning text) - 3 occurrences

#### 2. Hardcoded Property Access (~40 occurrences)
- `ship.current_fuel` / `ship.max_fuel` - 15 occurrences
- `ship.current_energy` / `ship.max_energy` - 10 occurrences
- `ship.current_ammo` / `ship.max_ammo` - 8 occurrences
- `ship.fuel_consumption` / `ship.energy_consumption` - 7 occurrences

#### 3. Hardcoded Cost Variables (~25 occurrences)
- `warp_fuel_cost` / `warp_energy_cost` - 12 occurrences
- `strategic_fuel_per_hex` - 8 occurrences
- `fuel_cost_per_hex` - 5 occurrences

---

## Migration Mapping

### Ability Name Conversions

| Legacy Pattern | Modern Equivalent |
|----------------|-------------------|
| `"EnergyStorage": 1000` | `"ResourceStorage": [{"resource": "energy", "amount": 1000}]` |
| `"FuelStorage": 5000` | `"ResourceStorage": [{"resource": "fuel", "amount": 5000}]` |
| `"AmmoStorage": 500` | `"ResourceStorage": [{"resource": "ammo", "amount": 500}]` |
| `"EnergyGeneration": 100` | `"ResourceGeneration": [{"resource": "energy", "amount": 100}]` |
| `"AmmoGeneration": 2.0` | `"ResourceGeneration": [{"resource": "ammo", "amount": 2.0}]` |
| `"EnergyConsumption": 5` | `"ResourceConsumption": [{"resource": "energy", "amount": 5, "trigger": "constant"}]` |

### Property Access Conversions

| Legacy Code | Modern Code |
|-------------|-------------|
| `ship.current_fuel` | `ship.resources.get_value('fuel')` |
| `ship.max_fuel` | `ship.resources.get_max_value('fuel')` |
| `ship.fuel_consumption` | Aggregate from ResourceConsumption abilities |
| `ship.get_fuel_cost_per_hex()` | `ship.stats.resource_consumption_per_hex['fuel']` |
| `ship.get_warp_fuel_cost()` | `ship.stats.warp_resource_costs['fuel']` |

---

## What's Already Working Well

### Properly Abstracted Systems

1. **Weapon Firing** - Uses `component.consume_activation()` which delegates to ResourceConsumption abilities
2. **Engine Per-Tick Consumption** - Uses ResourceConsumption with `trigger='constant'`
3. **Strategic Movement** - Uses ResourceConsumption with `trigger='strategic_per_hex'`
4. **Warp Jump Costs** - Uses ResourceConsumption with `trigger='warp_jump'`
5. **Combat Lab Tests** - All RESOURCE-* scenarios use new ResourceConsumption pattern
6. **Builder Stats Config** - [stats_config.py:429-476](game/ui/screens/builder/stats_config.py#L429-L476) dynamically discovers resources

### Compatibility Layer Working
The lambda factories in `abilities/__init__.py` successfully convert legacy JSON to modern ability instances at runtime. No immediate breakage.

---

## Recommended Migration Phases

### Phase 1: Critical Production Code (Week 1-2)
1. Fix [renderer.py](game/ui/renderer/renderer.py) - Replace direct property access
2. Fix [fleet_report_window.py](game/ui/screens/fleet_report_window.py) - Use resource container
3. Fix [ship_combat_engine.py](game/simulation/entities/ship_combat_engine.py) - Shield regen via ability
4. Define missing abilities: `ShipRepair`, `CrystallineArmor`, `AmmoGeneration`

### Phase 2: Strategic Layer Methods (Week 2-3)
1. Update [ship_instance.py](game/strategy/data/ship_instance.py) fuel cost methods
2. Update [fleet.py](game/strategy/data/fleet.py) fleet calculations
3. Remove legacy handling from [ship_stats_calculator.py](game/strategy/services/ship_stats_calculator.py)

### Phase 3: Data Migration (Week 3-4)
1. Convert [data/components.json](data/components.json) to modern format
2. Convert [simulation_tests/data/components.json](simulation_tests/data/components.json)
3. Convert [tests/unit/data/test_components.json](tests/unit/data/test_components.json)

### Phase 4: Test Updates (Week 4-5)
1. Update test fixtures in conftest.py files
2. Migrate unit tests to use modern ability format
3. Verify integration tests pass

### Phase 5: Cleanup (Week 5-6)
1. Remove shortcut factories from `abilities/__init__.py`
2. Remove legacy handling from stats calculator
3. Remove backwards-compatibility shims
4. Update documentation

---

## Files Requiring Migration

### Critical (15 files)
- `game/ui/renderer/renderer.py`
- `game/ui/screens/fleet_report_window.py`
- `game/ui/screens/fleet_report_filters.py`
- `game/simulation/entities/ship_combat_engine.py`
- `game/simulation/entities/combat_endurance.py`
- `game/simulation/entities/ship_stats.py`
- `game/strategy/data/ship_instance.py`
- `game/strategy/data/fleet.py`
- `game/strategy/services/ship_stats_calculator.py`
- `game/simulation/components/abilities/__init__.py`
- `data/components.json`
- `simulation_tests/data/components.json`
- `tests/unit/data/test_components.json`
- `game/ui/screens/builder/stats_config.py` (minor)
- `game/simulation/entities/ship_serialization.py`

### High (12 files)
- Various test files in `tests/unit/`
- Various test files in `tests/integration/`
- Ship JSON files using legacy patterns

### Medium (25+ files)
- Documentation files
- Legacy tool references
- Additional test fixtures

---

## Conclusion

The codebase has a **well-designed modern resource system** (`ResourceConsumption`, `ResourceStorage`, `ResourceGeneration`) that's already handling most functionality. The legacy patterns exist primarily for:

1. **Backwards compatibility** - Shortcut factories convert old format at runtime
2. **Historical code** - UI and fleet code still uses direct property access
3. **Test data** - Many tests use legacy shorthand format

**Risk Assessment:** LOW - The compatibility layer prevents immediate breakage. Migration can be done incrementally.

**Effort Estimate:** 4-6 weeks for complete migration with testing.

---

## Agent Reports

Individual agent findings are available in the `findings/` directory (agent outputs were returned inline due to synchronous execution).
