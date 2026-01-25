# Phase 5: Standardize Registry Access

**Project:** Legacy Code Cleanup
**Phase:** 5 of 8
**Risk Level:** Medium
**Dependencies:** Phase 4 complete

---

## High-Level Project Context

This phase is part of a comprehensive 8-phase legacy code cleanup effort:

| Phase | Name | Status |
|-------|------|--------|
| 1 | Delete Dead Code | Complete |
| 2 | Remove Shims & Aliases | Complete |
| 3 | Consolidate Re-exports | Complete |
| 4 | Enforce Layer Boundaries | Complete |
| **5** | **Standardize Registry Access** | **THIS PHASE** |
| 6 | Type Safety via Protocols | Pending |
| 7 | Standardize Data Formats | Pending |
| 8 | Clean Up Tests & Patterns | Pending |

**Overall Goal:** Clean up legacy code, enforce architectural boundaries, and standardize patterns across the Starship Battles codebase.

---

## Phase 5 Objectives

1. Define and document the tiered registry access pattern
2. Fix ModifierService inconsistency (uses direct singleton access)
3. Evaluate DataService - keep if adds value, remove if thin wrapper
4. Ensure consistent patterns across codebase
5. Document when to use each access pattern

---

## Target Access Pattern: Tiered Approach

### Tier 1: Utility Functions (Raw Access)

**Location:** `game/core/registry.py`

**Functions:**
- `get_component_registry()` → Returns component definitions dict
- `get_vehicle_classes()` → Returns vehicle class definitions dict
- `get_modifier_registry()` → Returns modifier definitions dict
- `get_resource_registry()` → Returns resource definitions dict
- `get_validator()` → Returns ship validator instance

**When to use:**
- Simple data retrieval
- No computation or validation needed
- Any layer can use these

**Example:**
```python
from game.core.registry import get_component_registry, get_vehicle_classes

# Get all components
components = get_component_registry()
component_def = components.get("beam_weapon_mk1")

# Get vehicle classes
classes = get_vehicle_classes()
cruiser = classes.get("Cruiser")
```

### Tier 2: Domain Services (Computed Access)

**Keep these services** - they add real value beyond raw access:

**ShipStatsService** (`game/strategy/services/ship_stats_service.py`)
- Calculates derived ship statistics
- Computes resource consumption, warp costs
- Aggregates component abilities
- NOT just a wrapper - does real computation

**ModifierService** (`game/simulation/services/modifier_service.py`)
- Validates modifier applications
- Manages mandatory modifiers
- Computes modifier effects
- NOT just a wrapper - does real computation

**When to use:**
- Need computed/derived values
- Need validation logic
- Need domain-specific operations

**Example:**
```python
from game.strategy.services.ship_stats_service import ShipStatsService

# Compute ship stats (not just retrieval)
stats = ShipStatsService.calculate_ship_stats(design_metadata)
warp_capable = ShipStatsService.has_warp_capability(design_metadata)
```

### Anti-Pattern: Direct Singleton Access

**DO NOT USE:**
```python
from game.core.registry import RegistryManager

# AVOID THIS - harder to mock, inconsistent
mods = RegistryManager.instance().modifiers
```

**INSTEAD USE:**
```python
from game.core.registry import get_modifier_registry

# PREFERRED - easy to mock, consistent
mods = get_modifier_registry()
```

---

## Detailed Tasks

### 5.1 Fix ModifierService Inconsistency

**File:** `game/simulation/services/modifier_service.py`

Currently uses direct singleton access in 3 locations:
- Line 17: `RegistryManager.instance().modifiers`
- Line 20: `RegistryManager.instance().modifiers`
- Line 108: `RegistryManager.instance().modifiers`
- Line 155: `RegistryManager.instance().modifiers`

**Steps:**
1. Add import: `from game.core.registry import get_modifier_registry`
2. Replace all `RegistryManager.instance().modifiers` with `get_modifier_registry()`
3. Remove `from game.core.registry import RegistryManager` if no longer needed
4. Verify tests still pass

**Before:**
```python
from game.core.registry import RegistryManager

def get_modifier(mod_id: str):
    return RegistryManager.instance().modifiers.get(mod_id)
```

**After:**
```python
from game.core.registry import get_modifier_registry

def get_modifier(mod_id: str):
    return get_modifier_registry().get(mod_id)
```

### 5.2 Evaluate DataService

**File:** `game/simulation/services/data_service.py`

Current assessment: DataService is a facade that wraps registry utility functions.

**Analysis needed:**
1. Count usages of DataService across codebase
2. Check what methods DataService provides
3. Determine if methods add value (filtering, validation, computed results) or just wrap

**If DataService just wraps:**
```python
# DataService method
def get_components(self):
    return get_component_registry()  # Just wrapping

# Callers should use directly
from game.core.registry import get_component_registry
components = get_component_registry()
```

**If DataService adds value:**
```python
# DataService method that adds value
def get_components_by_layer(self, layer_type):
    components = get_component_registry()
    return {k: v for k, v in components.items() if v.layer == layer_type}

# Keep this - it's a convenience method
```

**Decision tree:**
1. If all methods just wrap with no logic → Remove DataService
2. If some methods add logic → Keep those, remove simple wrappers
3. If all methods add significant logic → Keep DataService

### 5.3 Audit All Registry Access Patterns

Search for all registry access patterns:

```bash
# Find direct singleton access (anti-pattern)
grep -rn "RegistryManager.instance()" --include="*.py" game/

# Find utility function usage (correct pattern)
grep -rn "get_component_registry\|get_vehicle_classes\|get_modifier_registry" --include="*.py" game/

# Find service usage (also correct)
grep -rn "from game.simulation.services.data_service\|from game.strategy.services.ship_stats_service" --include="*.py"
```

**For each direct singleton access found:**
1. Determine if it's in production code or test code
2. Test code using singleton for mocking is acceptable
3. Production code should use utility functions

### 5.4 Document Access Patterns

Add documentation to `game/core/registry.py`:

```python
"""
Registry Access Patterns
========================

This module provides centralized access to game data registries.

PREFERRED ACCESS PATTERNS:

1. Utility Functions (Tier 1 - Raw Access):
   Use for simple data retrieval.

   from game.core.registry import get_component_registry
   components = get_component_registry()

2. Domain Services (Tier 2 - Computed Access):
   Use for computed/derived values.

   from game.strategy.services.ship_stats_service import ShipStatsService
   stats = ShipStatsService.calculate_ship_stats(design)

AVOID:

   # Direct singleton access - harder to test
   from game.core.registry import RegistryManager
   RegistryManager.instance().components  # DON'T DO THIS
"""
```

### 5.5 Update Any Remaining Anti-Patterns

After audit, update any remaining direct singleton access in production code:

**Files likely to have issues (from prior audit):**
- `game/simulation/services/modifier_service.py` (confirmed - 4 locations)
- Check other service files
- Check UI files that might access registry

---

## Verification Checklist

After completing all tasks:

- [ ] ModifierService uses `get_modifier_registry()` consistently
- [ ] No direct `RegistryManager.instance()` in production code
- [ ] DataService evaluated and decision documented
- [ ] If DataService removed, all callers updated
- [ ] Documentation added to registry.py
- [ ] Access pattern is consistent across codebase
- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] Application launches and runs correctly

---

## Files Modified

- `game/simulation/services/modifier_service.py` (fix singleton access)
- `game/core/registry.py` (add documentation)
- `game/simulation/services/data_service.py` (evaluate/potentially remove)
- Various files if DataService is removed (update imports)

---

## Registry Access Audit Results Template

Document findings:

| File | Line | Pattern | Status |
|------|------|---------|--------|
| modifier_service.py | 17 | RegistryManager.instance() | Fix to utility |
| modifier_service.py | 20 | RegistryManager.instance() | Fix to utility |
| ... | ... | ... | ... |

---

## Notes for Next Phase

Phase 6 (Type Safety via Protocols) will:
- Define core protocols (IStrategyEntity, IFleet, IPlanet)
- Replace duck typing clusters (500+ hasattr patterns)
- Create type guard utilities
- Enable mypy type checking

Ensure registry access is standardized before proceeding to Phase 6.

---

*End of Phase 5 Plan*
