# Regression Report - Resource System Legacy Audit Update Review

## Summary

| ID | Regression Type | Location | Severity |
|----|----------------|----------|----------|
| REG-01 | Missing Ability Class | `abilities/__init__.py` + `ship_stats.py:398` | Critical |
| REG-02 | Missing Ability Class | `abilities/__init__.py` + `ship_stats.py:401` | Critical |
| REG-03 | Silent Ability Skip | `ability_manager.py:179-180` | Major |

## Detailed Regressions

### REG-01: Missing CrystallineArmor Class in ABILITY_REGISTRY
**Location:** `game/simulation/components/abilities/__init__.py:53-81` and `game/simulation/entities/ship_stats.py:398`
**Severity:** Critical

**Issue:**
The `ship_stats.py` file references `'CrystallineArmor'` ability at line 398, but this class is not defined and not registered in `ABILITY_REGISTRY`. The code calls `self._get_ability_total(component_pool, 'CrystallineArmor')`, which silently returns 0.

**Evidence:**
- Line 398 in ship_stats.py: `ship.crystalline_armor = self._get_ability_total(component_pool, 'CrystallineArmor')`
- ABILITY_REGISTRY (lines 53-81) does NOT contain "CrystallineArmor" entry
- ability_manager.py silently skips abilities not in registry
- Components in data/components.json DO define CrystallineArmor abilities (line 197)

**Impact:**
- Components with CrystallineArmor abilities will never contribute to `ship.crystalline_armor`
- The value always remains 0, making crystalline armor completely non-functional
- Feature is silently broken with no runtime errors

**Recommendation:** Add CrystallineArmor class to defense.py and register it in ABILITY_REGISTRY

**Effort:** Simple

---

### REG-02: Missing ShipRepair Class in ABILITY_REGISTRY
**Location:** `game/simulation/components/abilities/__init__.py:53-81` and `game/simulation/entities/ship_stats.py:401`
**Severity:** Critical

**Issue:**
The `ship_stats.py` file references `'ShipRepair'` ability at line 401, but this class is not defined and not registered in `ABILITY_REGISTRY`.

**Evidence:**
- Line 401 in ship_stats.py: `ship.repair_rate = self._get_ability_total(component_pool, 'ShipRepair')`
- ABILITY_REGISTRY does NOT contain "ShipRepair" entry
- Components in data/components.json DO define ShipRepair abilities (line 1116)

**Impact:**
- Components with ShipRepair abilities will never contribute to `ship.repair_rate`
- The value always remains 0, making ship repair completely non-functional
- Ships with repair bay components cannot repair damage

**Recommendation:** Add ShipRepair class and register it in ABILITY_REGISTRY

**Effort:** Simple

---

### REG-03: Silent Ability Instantiation Failures
**Location:** `game/simulation/components/ability_manager.py:179-180`
**Severity:** Major

**Issue:**
The ability instantiation system silently skips any ability not found in ABILITY_REGISTRY without logging a warning. Unknown ability names are never flagged as errors.

**Evidence:**
- Lines 179-180: `if name not in ABILITY_REGISTRY: continue` (no log message)
- Contrast with create_ability() which logs warnings on creation failure
- No indication when abilities are silently skipped

**Impact:**
- Makes debugging harder when new abilities are added but not registered
- Silent data loss during ability instantiation
- Regressions like REG-01 and REG-02 go unnoticed

**Recommendation:** Add warning log when ability is referenced but not found in registry

**Effort:** Simple

---

## Areas Checked (No Regressions Found)

- **Resource Manager System:** ResourceStorage, ResourceGeneration, ResourceConsumption abilities properly registered and working
- **Defense Abilities:** EmissiveArmor, ShieldProjection, ShieldRegeneration, ToHitModifiers all properly implemented
- **Propulsion Abilities:** CombatPropulsion, ManeuveringThruster, StrategicMovement, WarpJump properly registered
- **Crew Management:** CrewCapacity, LifeSupportCapacity, CrewRequired properly implemented
- **Weapon System:** All weapon abilities properly registered
- **Core Tests:** All ability-related unit tests pass
- **Stat Calculation Flow:** Phase 1-6 stat calculation properly handles registered abilities
- **Ability Aggregation:** Two-phase aggregation (intra-group MAX, inter-group SUM) working correctly

## Conclusion

The refactor was successful for all abilities that ARE registered. However, 2 ability classes referenced in ship_stats.py were never migrated:
1. **CrystallineArmor** - Completely missing
2. **ShipRepair** - Completely missing

The silent failure mode (using getattr() defaults) prevents crashes but masks broken functionality. These are not true "regressions" in the sense of working code being broken - rather, they are incomplete migrations where the ability definitions were never created.
