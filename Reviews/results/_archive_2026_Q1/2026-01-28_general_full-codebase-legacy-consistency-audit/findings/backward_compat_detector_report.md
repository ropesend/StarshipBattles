# Backward Compatibility Detector Report

## Summary
- **Total issues found:** 19
- **Critical:** 2, **Major:** 8, **Minor:** 6, **Info:** 3

---

## Critical Findings

### BCD-001: DUAL REGISTRY SYSTEM (IRegistryProvider vs GameRegistries)
**Severity:** CRITICAL
**Location:**
- `game/core/registry.py:40-74`
- `game/simulation/services/vehicle_design_service.py:56-98`
- `game/simulation/services/modifier_service.py:36-98`
- `game/simulation/entities/ship_serialization.py:113-150`

**Issue:** The codebase maintains TWO parallel dependency injection patterns:

**OLD (PROJ-27 - IRegistryProvider):**
```python
service = VehicleDesignService(registry=provider)  # Deprecated pattern
```

**NEW (PROJ-38 - GameRegistries):**
```python
service = VehicleDesignService(registries=game_registries)  # Preferred pattern
```

Multiple classes implement fallback logic:
```python
if registries is not None:
    self._registries = registries
    self._registry = None
elif registry is not None:
    self._registry = registry
    self._registries = None
else:
    try:
        self._registries = get_default_registries()
    except RuntimeError:
        self._registry = get_default_registry_provider()
```

**Impact:** Code complexity, duplicated logic in 15+ files, confusion for new developers

**Recommendation:** Complete deprecation of IRegistryProvider pattern - migrate all callers to GameRegistries

**Effort:** Complex

---

### BCD-002: DEPRECATED REGISTRY UTILITY FUNCTIONS
**Severity:** MAJOR
**Location:** `game/core/registry.py:298-361`

**Issue:** Five utility functions (`get_component_registry()`, `get_modifier_registry()`, `get_vehicle_classes()`, `get_validator()`, `get_resource_registry()`) are marked deprecated with DeprecationWarning but still widely used throughout the codebase. They emit runtime warnings on every call.

**Backward Compat Pattern:**
- Functions fallback to global RegistryManager singleton
- New pattern should use GameRegistries dependency injection
- 119 PROJ references show incomplete migration

**Recommendation:**
1. Audit all callers of these deprecated functions
2. Complete migration to GameRegistries dependency injection (PROJ-38)
3. Remove deprecated functions after verification
4. Consider keeping one compatibility layer if total migration will take multiple sprints

**Effort:** Complex (affects multiple systems)

---

## Major Findings

### BCD-003: MODULAR SERVICE STATIC/INSTANCE METHOD OVERLOADING
**Severity:** MAJOR
**Location:** `game/simulation/services/modifier_service.py:54-98`

**Issue:** ModifierService.is_modifier_allowed() supports BOTH patterns:
```python
# Static-style (legacy)
ModifierService.is_modifier_allowed('mod_id', component)

# Instance-style (new)
service = ModifierService()
service.is_modifier_allowed('mod_id', component)
```

Uses parameter introspection to detect calling pattern:
```python
if isinstance(self_or_mod_id, ModifierService):
    # Instance method call
else:
    # Static-style call
```

**Impact:** Confusing API, harder to maintain, violates single calling pattern principle

**Recommendation:** Choose one pattern (instance methods preferred), deprecate the other

**Effort:** Medium

---

### BCD-004: LEGACY COMPONENT PANEL RETENTION
**Severity:** MAJOR
**Location:** `game/ui/screens/builder/legacy_components.py` (189 lines)

**File Header Indicates:**
```
Note: This file contains legacy modifier editing functionality.
Consider migration to ModifierLogic for new code.
```

This is an entire legacy UI panel that's been retained for backward compatibility.

**Recommendation:**
1. Verify all functionality exists in ModifierLogic replacement
2. Audit which code paths still use legacy_components.py
3. Migrate or remove

**Effort:** Medium

---

### BCD-005: SAVE GAME VERSION MIGRATION WITH FALLBACK
**Severity:** MAJOR
**Location:** `game/strategy/systems/save_game_service.py:26-415`

**Issue:** Save system maintains compatibility with 4 previous versions:
```python
SAVE_VERSION = "2.0.0"
MIGRATABLE_VERSIONS = ["1.0.0", "1.1.0", "1.2.0", "1.9.0"]
```

Functions like `_can_migrate_version()`, `_is_compatible_version()` handle old format detection. Also has disabled migration code:

```python
# BUG-29 FIX: Do NOT migrate designs from temp folder
# SaveGameService._migrate_temp_designs(game_session, designs_folder)
```

Commented-out migration helper at line 114-147: `_migrate_temp_designs()`

**Recommendation:**
1. Decide on minimum supported version
2. Remove support for versions below that
3. Clean up disabled migration code
4. Update MIGRATABLE_VERSIONS

**Effort:** Medium

---

### BCD-006: SHIP SERIALIZATION WITH STAT MISMATCH FALLBACK
**Severity:** MEDIUM
**Location:** `game/simulation/entities/ship_serialization.py:208-246`

**Issue:** Serializer includes "expected_stats" that are verified on load with auto-correction:
```python
if mismatches:
    log_warning(f"Ship '{s.name}' stats mismatch after loading!")
    for m in mismatches:
        log_warning(f"  - {m}")
```

This is a backward compatibility fallback for stats mismatch handling. The data includes:
- max_hp, max_fuel, max_energy, max_ammo
- max_speed, acceleration_rate, turn_speed, total_thrust
- armor_hp_pool, warp values, strategic movement

**Recommendation:**
1. Verify these stats are accurately calculated during from_dict()
2. Consider if this fallback is still needed
3. If format changed, implement explicit versioning instead

**Effort:** Medium

---

### BCD-007: BACKWARD COMPATIBILITY ALIASES IN APP.PY
**Severity:** MINOR
**Location:** `game/app.py:49-58`

**Issue:** Scene state aliases for backward compatibility:
```python
# Scene States (Aliased for compatibility)
MENU = GameState.MENU
BUILDER = GameState.BUILDER
BATTLE = GameState.BATTLE
...
```

These module-level aliases duplicate the enum values instead of using them directly.

**Recommendation:** Remove aliases, use GameState enum directly throughout codebase

**Effort:** Simple

---

### BCD-008: LEGACY CREW REQUIREMENT PATTERN
**Severity:** MINOR
**Location:** `game/ui/screens/builder/stats_config.py:67-83`

**Issue:** Helper function for extracting crew requirements from old format:
```python
def _get_legacy_crew_requirement(ship):
    """Get crew requirement from negative CrewCapacity values (legacy pattern)."""
    crew_capacity = ship.get_ability_total('CrewCapacity')
    if crew_capacity < 0:
        return abs(crew_capacity)
    return 0
```

Old components used negative CrewCapacity instead of CrewRequired ability.

**Recommendation:** Migrate all old components to use CrewRequired ability, remove this helper

**Effort:** Medium (requires component migration)

---

### BCD-009: GETATTR WITH DEFAULTS FOR BACKWARDS COMPAT
**Severity:** MINOR
**Location:** `game/simulation/entities/ship_serialization.py:41-66`

Multiple uses of `getattr()` with defaults for potentially-missing attributes:
```python
"vehicle_type": getattr(ship, 'vehicle_type', 'Ship'),
"strategic_movement": getattr(ship, 'total_strategic_movement', 0),
"warp_max_tonnage": getattr(ship, 'warp_max_tonnage', 0),
```

These suggest optional attributes that may not exist on all ship objects (backward compat fallback).

**Recommendation:** Make these attributes mandatory on Ship class

**Effort:** Simple

---

### BCD-010: COMPONENT FORMAT MIGRATION IN SERIALIZATION
**Severity:** MEDIUM
**Location:** `game/simulation/entities/ship_serialization.py:168-172`

**Issue:** Component deserialization supports TWO formats:
```python
if isinstance(c_entry, str):
    # Old format: just component ID
    comp_id = c_entry
elif isinstance(c_entry, dict):
    # New format: dict with id and modifiers
    comp_id = c_entry.get("id", "")
    modifiers_data = c_entry.get("modifiers", [])
```

This is format versioning without explicit version checking.

**Recommendation:** Standardize on dict format, handle migration explicitly

**Effort:** Medium

---

## Lower Priority Issues

### BCD-011: MODIFIER SCHEMA V1 FORMAT SUPPORT
**File:** `game/simulation/components/modifier_schema.py`
**Issue:** Comments indicate V1 format (deprecated) still supported
**Recommendation:** Remove V1 support if migration is complete
**Effort:** Simple

### BCD-012: SHIP COMBAT DEPRECATION NOTICE
**File:** `game/simulation/entities/ship_combat.py`
**Issue:** Deprecation notice about future removal
**Recommendation:** Either remove or set timeline
**Effort:** Simple

### BCD-013: FLEET MOVEMENT MODULE DEPRECATION
**File:** `game/strategy/engine/fleet_movement.py`
**Header:** "DEPRECATED: This module is deprecated as of PROJ-35"
**Recommendation:** Remove or migrate all callers
**Effort:** Medium

### BCD-014: DISABLED BUG-29 MIGRATION CODE
**File:** `game/strategy/systems/save_game_service.py:74-77`
**Issue:** Commented-out temp design migration
**Recommendation:** Remove if no longer needed
**Effort:** Simple

### BCD-015: MODIFIER LOGIC MANDATORY MODIFIER ENFORCEMENT
**File:** `game/ui/screens/builder/modifier_logic.py:142-150`
**Issue:** ensure_mandatory_modifiers() adds missing mandatory modifiers at runtime
**Recommendation:** Ensure this is only for UI, not data model
**Effort:** Simple

---

## Top 5 Priority Issues (by Impact)

1. **DUAL REGISTRY SYSTEM (PROJ-38 Migration)** - BCD-001
   - 15+ files affected with fallback logic
   - Causes deprecation warnings throughout runtime
   - **Action:** Complete IRegistryProvider deprecation, audit 50+ callers

2. **DEPRECATED UTILITY FUNCTIONS** - BCD-002
   - 5 deprecated functions still widely used
   - Runtime warning spam on startup
   - **Action:** Migrate all callers to GameRegistries

3. **MODIFIER SERVICE DUAL CALLING PATTERN** - BCD-003
   - Parameter type introspection for backward compat
   - Confusing API for 2 calling conventions
   - **Action:** Choose instance or static pattern, standardize all callers

4. **SAVE FILE VERSION MIGRATION** - BCD-005
   - Supports 4 old formats unnecessarily
   - Disabled migration code cluttering logic
   - **Action:** Define minimum supported version, remove old code

5. **LEGACY COMPONENT PANEL** - BCD-004
   - Entire 189-line module for backward compat
   - Not actively maintained
   - **Action:** Verify replacement exists, remove if safe

---

## Recommendations Summary

1. **Immediate (Sprint 1):** Remove module-level aliases (app.py), clean up disabled code
2. **Short-term (Sprint 2-3):** Complete PROJ-38 migration, consolidate registry patterns
3. **Medium-term (Sprint 4-5):** Migrate component formats, ship serialization
4. **Long-term:** Establish minimum version policy for future backward compat decisions

All findings suggest the codebase is in active migration with partial completion. Focus should be completing PROJ-38 before adding new backward compatibility features.
