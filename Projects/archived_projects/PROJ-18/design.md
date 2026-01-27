# PROJ-18: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### Current Registry Architecture

The `RegistryManager` is a thread-safe singleton at `game/core/registry.py` that provides:
- **components**: Dict of component definitions
- **modifiers**: Dict of modifier definitions
- **vehicle_classes**: Dict of vehicle class definitions
- **resources**: Dict of resource definitions
- **_validator**: Ship design validator (lazy-loaded)
- **_frozen**: State lock to prevent modifications during gameplay

### Existing Utility Functions (Tier 1)
Located at `game/core/registry.py:173-196`:
- `get_component_registry() -> Dict[str, Any]`
- `get_modifier_registry() -> Dict[str, Any]`
- `get_vehicle_classes() -> Dict[str, Any]`
- `get_validator() -> Any`
- `get_resource_registry() -> Dict[str, Any]`

### Anti-Pattern Identified
Direct `RegistryManager.instance()` access in production code:
- `game/simulation/services/modifier_service.py` - 4 locations (lines 17, 20, 108, 155)
- `game/simulation/ship_validator.py` - 1 location (line 242)
- Test files - 275 occurrences (most are acceptable `.clear()` calls)

### DataService Status
- Location: `game/simulation/services/data_service.py`
- **NOT used in any production code** - only exported and tested
- Contains 9 pure wrapper methods (no value) and 4 filtering methods
- Test file at `tests/unit/services/test_data_service.py`
- **Decision: Delete entirely** (user confirmed no production usage)

## Swarm Findings Summary

### Architecture Analysis

**Tiered Access Pattern:**
```
TIER 1: Utility Functions (game/core/registry.py)
├── get_component_registry() ✓
├── get_modifier_registry() ✓
├── get_vehicle_classes() ✓
├── get_resource_registry() ✓
├── get_validator() ✓
├── freeze_registry() ✗ MISSING (to add)
├── set_validator() ✗ MISSING (to add)
└── clear_registry() ✗ MISSING (to add)

TIER 2: Domain Services
├── ShipStatsService ✓ (uses utility functions correctly)
├── VehicleDesignService ✓ (uses utility functions correctly)
└── ModifierService ✗ (uses RegistryManager.instance() directly - FIX)
```

### Key Patterns to Reuse

- **VehicleDesignService**: `game/simulation/services/vehicle_design_service.py:66` - Correctly imports and uses `get_vehicle_classes()`:
  ```python
  vehicle_classes = get_vehicle_classes()
  if ship_class not in vehicle_classes:
      warnings.append(f"Unknown ship class '{ship_class}', using defaults")
  ```

- **ShipStatsService**: `game/strategy/services/ship_stats_service.py:345` - Correctly uses `get_component_registry()`:
  ```python
  registry = get_component_registry()
  for comp_id, comp_entry in layer_components:
      comp_def = registry.get(comp_id)
  ```

### Dependencies & Risks

1. **ModifierService refactor** (LOW risk)
   - Simple search-replace: `RegistryManager.instance().modifiers` → `get_modifier_registry()`
   - No API changes, internal refactoring only
   - All 30+ tests will work as-is

2. **DataService deletion** (LOW risk)
   - Zero production usage confirmed
   - Only need to delete file and remove from exports
   - Delete test file `test_data_service.py`

3. **New utility functions** (LOW risk)
   - Pure delegation to existing methods
   - No new logic, just convenience wrappers
   - Already used pattern established

### Test Impact

- **ModifierService tests**: 30+ tests in `tests/unit/services/test_modifier_service.py` - no changes needed
- **DataService tests**: Delete `tests/unit/services/test_data_service.py`
- **Registry tests**: Existing coverage in `tests/unit/core/test_registry.py`

### Pre-existing Test Failures (NOT related to this project)

5 tests failing before project start:
- `test_builder_warning_logic.py` (4 tests) - Reference `builder._workshop` which doesn't exist
- `test_advanced_fleet_orders.py::test_intercept_integration` (1 test)

These are unrelated to registry access and should not block Phase 5 work.

## Design Decisions

| Decision | Rationale |
|----------|-----------|
| Delete DataService entirely | Not used in production, pure wrapper with no value |
| Add 3 new utility functions | User requested; provides complete Tier 1 API |
| Do NOT move `get_or_create_validator()` | Keep in `ship_loader.py` - not widely used |
| Production code only | Focus fixes on production code, not test code |

See [decisions.md](decisions.md) for the full log with rationale.
