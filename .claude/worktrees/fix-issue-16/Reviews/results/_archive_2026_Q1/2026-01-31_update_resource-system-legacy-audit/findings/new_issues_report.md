# New Issues Report - Resource System Legacy Audit Update Review

## Summary

| ID | Severity | Title | Location |
|----|----------|-------|----------|
| NEW-01 | Critical | Potential Attribute Access Issue in Weapon Activation Costs | `combat_endurance.py:74` |
| NEW-02 | Major | Shield Energy Cost Uses String Class Name Check | `ship_stats.py:289` |
| NEW-03 | Info | Legacy Resource Key Filter in UI Stats Config | `stats_config.py:421` |

## Detailed New Findings

### NEW-01: Potential Attribute Access Issue in Weapon Activation Costs
**Severity:** Critical
**Location:** `game/simulation/entities/combat_endurance.py:72-77`

**Issue:**
The code attempts to access `ab.resource_name` and `ab.amount` directly on ResourceConsumption ability instances within an activation trigger block:

```python
if reload_t > 0:
    rate = ab.amount / reload_t
    if ab.resource_name == 'ammo':
        c_ammo += rate
    elif ab.resource_name == 'energy':
        c_energy += rate
```

**Impact:**
- Combat endurance calculations could fail if a weapon component has a malformed ResourceConsumption ability
- Lacks defensive `getattr()` used elsewhere in codebase

**Recommendation:**
Use `getattr(ab, 'resource_name', '')` with fallback:

```python
resource_name = getattr(ab, 'resource_name', '')
amount = getattr(ab, 'amount', 0.0)
```

**Effort:** Simple
**Why Not in Original:** Code path may not have been fully exercised during original review.

---

### NEW-02: Shield Energy Cost Uses String Class Name Check
**Severity:** Major
**Location:** `game/simulation/entities/ship_stats.py:286-291`

**Issue:**
Shield regen cost calculation manually searches for ResourceConsumption abilities by checking string equality on class name:

```python
if ab.__class__.__name__ == 'ResourceConsumption' and getattr(ab, 'resource_name', '') == 'energy':
    total_shield_cost += getattr(ab, 'amount', 0.0)
    break
```

**Impact:**
- Uses fragile string class name comparison instead of `isinstance()`
- Only takes first match, ignoring multiple ResourceConsumption abilities
- Assumes ShieldRegeneration only consumes energy

**Recommendation:**
Use `isinstance()` check and aggregate all matching abilities:

```python
if isinstance(ab, ResourceConsumption) and ab.resource_name == 'energy':
    total_shield_cost += ab.amount
```

**Effort:** Medium
**Why Not in Original:** New manifestation in refactored code integrating shield regen into stats calculator.

---

### NEW-03: Legacy Resource Key Filter in UI Stats Config
**Severity:** Info
**Location:** `game/ui/screens/builder/stats_config.py:421`

**Issue:**
The stats config maintains a runtime filter for legacy resource keys:

```python
legacy_keys = ['max_fuel', 'max_energy', 'max_ammo', 'fuel_endurance', 'ammo_endurance', 'energy_endurance']
base_rows = [r for r in STATS_LOGISTICS if r.key not in legacy_keys]
```

**Impact:**
- Requires matching between two separate lists
- Runtime filtering instead of cleaning source data
- Minor maintenance overhead

**Recommendation:**
Clean the source - remove legacy keys directly from `STATS_LOGISTICS` definition.

**Effort:** Simple
**Why Not in Original:** Symptom of partial migration approach noted in original review.

---

## Areas Searched (No New Issues)

- `game/simulation/systems/resource_manager.py` - Consistent attribute patterns
- `game/strategy/services/ship_stats_calculator.py` - Correctly builds resource cost dicts
- `game/strategy/data/ship_instance.py` - Correctly accesses stats via dictionary keys
- `game/strategy/data/fleet.py` - No hardcoded resource access
- `game/simulation/entities/ship_serialization.py` - Correctly uses resource interface
- `data/resources.json` - Standard resource definitions
- UI resource getters - Dynamic resource discovery works correctly

## Conclusion

The refactor introduced **1 critical and 1 major** new issues related to attribute access and ability filtering patterns. These are technical debt from the partial migration approach:

1. NEW-01 is a defensive programming gap
2. NEW-02 is a consequence of integrating shield regen into generic stats calculator
3. NEW-03 is incomplete legacy data cleanup

All are fixable with minor code changes.
