# Phase 7: Standardize Data Formats

**Project:** Legacy Code Cleanup
**Phase:** 7 of 8
**Risk Level:** Medium
**Dependencies:** Phase 6 complete

---

## High-Level Project Context

This phase is part of a comprehensive 8-phase legacy code cleanup effort:

| Phase | Name | Status |
|-------|------|--------|
| 1 | Delete Dead Code | Complete |
| 2 | Remove Shims & Aliases | Complete |
| 3 | Consolidate Re-exports | Complete |
| 4 | Enforce Layer Boundaries | Complete |
| 5 | Standardize Registry Access | Complete |
| 6 | Type Safety via Protocols | Complete |
| **7** | **Standardize Data Formats** | **THIS PHASE** |
| 8 | Clean Up Tests & Patterns | Pending |

**Overall Goal:** Clean up legacy code, enforce architectural boundaries, and standardize patterns across the Starship Battles codebase.

**Important Note:** No save game migration is required. Backward compatibility for save files is NOT a concern.

---

## Phase 7 Objectives

1. Remove dual-format support for fleet ships (string vs ShipInstance)
2. Standardize production queue format (remove list format)
3. Remove legacy ship stats fields
4. Standardize design metadata format
5. Standardize tech tree requirement format
6. Update all test fixtures to use new formats

---

## Detailed Tasks

### 7.1 Fleet Ship Format

**File:** `game/strategy/data/fleet.py`

**Current State:**
- Ships can be strings (legacy) OR ShipInstance objects
- Type: `List[Union[str, 'ShipInstance']]`
- Multiple places handle both formats

**Locations to fix:**
| Lines | Pattern |
|-------|---------|
| 50-54 | Type annotation and documentation |
| 60 | `ships: List[Union[str, 'ShipInstance']]` |
| 93-96 | Speed recalculation guard for string-only fleets |
| 102 | `get_ship_instances()` filters out strings |
| 557-565 | Legacy string preservation in serialization |

**Changes:**
1. Change type to: `ships: List['ShipInstance']`
2. Remove string handling in `_trigger_speed_recalculation()`
3. Remove `get_ship_instances()` - just use `ships` directly
4. Remove legacy string preservation in serialization
5. Update docstrings to remove mentions of string format

**Before:**
```python
ships: List[Union[str, 'ShipInstance']] = field(default_factory=list)

def get_ship_instances(self) -> List['ShipInstance']:
    """Return only ShipInstance objects, filtering out legacy strings."""
    return [s for s in self.ships if isinstance(s, ShipInstance)]
```

**After:**
```python
ships: List['ShipInstance'] = field(default_factory=list)

# get_ship_instances() removed - use self.ships directly
```

### 7.2 Production Queue Format

**File:** `game/strategy/engine/production_engine.py` (Lines 57-79)
**File:** `game/strategy/data/planet.py` (Lines 140-153)

**Current State:**
- Supports old format: `["Ship Name", 5]`
- And new format: `{"design_id": "...", "turns_remaining": 5}`

**Changes to production_engine.py:**
1. Remove list format handling
2. Expect only dict format

**Changes to planet.py (add_production):**
1. Remove list format support
2. Accept only dict format

**Before:**
```python
def add_production(self, item):
    if isinstance(item, list):
        # Legacy format: ["Ship Name", 5]
        self.production_queue.append({
            "design_id": item[0],
            "turns_remaining": item[1]
        })
    else:
        self.production_queue.append(item)
```

**After:**
```python
def add_production(self, item: Dict[str, Any]):
    """Add item to production queue.

    Args:
        item: Dict with 'design_id' and 'turns_remaining' keys
    """
    self.production_queue.append(item)
```

**Also update:** `game/ui/screens/build_queue_screen.py`
- Lines 476-485: Remove dual format handling
- Lines 702, 760-761, 770: Remove format checks

### 7.3 Ship Stats Legacy Fields

**File:** `game/strategy/services/ship_stats_service.py`

**Current State:**
- Supports legacy fields: `max_fuel`, `max_energy`, `max_ammo`
- Supports legacy: `strategic_fuel_per_hex`
- Supports legacy: `warp_energy_cost`, `warp_fuel_cost`

**Locations:**
| Lines | Legacy Fields |
|-------|---------------|
| 90-98 | `max_fuel`, `max_energy`, `max_ammo` extraction |
| 100-103 | `strategic_fuel_per_hex` extraction |
| 105-111 | `warp_energy_cost`, `warp_fuel_cost` extraction |
| 214-234 | WarpJump `energy_cost`/`fuel_cost` support |

**Changes:**
1. Remove legacy field extraction logic
2. Use only ability-based resource system
3. Remove re-export of legacy fields

**The new system uses:**
- `resource_storage: Dict[str, int]` instead of individual max_* fields
- `resource_consumption_per_hex: Dict[str, float]` instead of strategic_fuel_per_hex
- `warp_resource_costs: Dict[str, int]` instead of warp_*_cost

### 7.4 Design Metadata Format

**File:** `game/strategy/data/design_metadata.py`

**Current State:**
- Supports old layer format: `{"components": [...]}`
- Supports new format: Direct list `[...]`
- Mass in `expected_stats.mass` (new) or top-level `mass` (legacy)

**Locations:**
| Lines | Pattern |
|-------|---------|
| 88-90 | Mass location check |
| 163-169 | Old `{"components": [...]}` vs new list |
| 210-215 | Same dual format handling |

**Changes:**
1. Remove `{"components": [...]}` wrapper support
2. Expect direct list format only
3. Mass always from `expected_stats.mass`

**Before:**
```python
def get_layer_components(self, layer_name: str) -> List[str]:
    layer_data = self.layers.get(layer_name, {})
    if isinstance(layer_data, dict):
        return layer_data.get('components', [])  # Old format
    return layer_data  # New format (direct list)
```

**After:**
```python
def get_layer_components(self, layer_name: str) -> List[str]:
    return self.layers.get(layer_name, [])
```

### 7.5 Tech Tree Requirement Format

**File:** `game/research/data/tech_tree.py` (Lines 64-70)

**Current State:**
- Supports old format: `level: 5` (single integer)
- Supports new format: `level_range: [5, 10]` (array)

**Changes:**
1. Remove single `level` integer support
2. Use only `level_range` array format

### 7.6 Update Test Fixtures

After removing legacy format support, update all test fixtures:

**Files with legacy fixtures:**
- `tests/unit/strategy/conftest.py` (Lines 117-124, 257-270)
  - `ship_stats_with_custom_resources` fixture has legacy fields
  - `legacy_string_fleet` fixture
- Various test files using legacy formats

**Steps:**
1. Update `ship_stats_with_custom_resources` to use new format
2. Delete `legacy_string_fleet` fixture
3. Update any tests using legacy formats
4. Search for and update any inline legacy format usage

### 7.7 Remove Backward Compatibility Tests

These tests validate legacy behavior that no longer exists:

**Files to update/remove tests from:**
- `tests/unit/strategy/test_fleet.py` - Legacy string ship tests
- `tests/unit/strategy/test_turn_engine.py` - `test_legacy_list_format_supported()`
- `tests/integration/test_resource_system.py` - Mixed legacy/new ship tests
- `tests/unit/entities/test_ship_stats.py` - `test_ability_values_match_legacy_attributes()`

---

## Verification Checklist

After completing all tasks:

- [ ] Fleet only accepts ShipInstance objects
- [ ] `get_ship_instances()` method removed
- [ ] Production queue only accepts dict format
- [ ] Build queue screen uses single format
- [ ] Legacy ship stats fields removed
- [ ] Design metadata uses direct list format
- [ ] Tech tree uses level_range only
- [ ] All test fixtures updated
- [ ] Legacy format tests removed
- [ ] No `Union[str, ShipInstance]` types remain
- [ ] No list format checks in production code
- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] Application launches and runs correctly
- [ ] New game creation works correctly

---

## Files Modified

**Core Data Files:**
- `game/strategy/data/fleet.py`
- `game/strategy/data/planet.py`
- `game/strategy/data/design_metadata.py`
- `game/strategy/engine/production_engine.py`
- `game/strategy/services/ship_stats_service.py`
- `game/research/data/tech_tree.py`
- `game/ui/screens/build_queue_screen.py`

**Test Files:**
- `tests/unit/strategy/conftest.py`
- `tests/unit/strategy/test_fleet.py`
- `tests/unit/strategy/test_turn_engine.py`
- `tests/integration/test_resource_system.py`
- `tests/unit/entities/test_ship_stats.py`
- Other test files using legacy formats

---

## Search Commands

Find remaining legacy patterns:

```bash
# String ship format
grep -rn "Union\[str, " --include="*.py" game/
grep -rn "isinstance.*str" --include="*.py" game/strategy/

# List production format
grep -rn "isinstance.*list" --include="*.py" game/strategy/

# Legacy ship stats fields
grep -rn "max_fuel\|max_energy\|max_ammo" --include="*.py" game/
grep -rn "strategic_fuel_per_hex" --include="*.py" game/
grep -rn "warp_energy_cost\|warp_fuel_cost" --include="*.py" game/

# Legacy design format
grep -rn "\.get\('components'" --include="*.py" game/

# Legacy tech format
grep -rn "'level':" --include="*.py" game/research/
```

---

## Notes for Next Phase

Phase 8 (Clean Up Tests & Patterns) will:
- Remove test fixture aliases
- Consolidate bug reproduction tests
- Standardize code patterns (f-strings, exception types)
- Consolidate duplicate utility functions
- Final cleanup and polish

This is the last major cleanup phase. Phase 8 is lower risk.

---

*End of Phase 7 Plan*
