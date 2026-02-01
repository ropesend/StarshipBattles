# PROJ-50: Design Document - Strict Dependency Injection Refactor

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Objective

Eliminate the "Service Locator" anti-pattern by removing `get_default_registry_provider()` and `_get_registries_fallback()`. Enforce mandatory `GameRegistries` injection in all core entities.

**Success Metric:** `grep -r "get_default_registry_provider" game/` returns 0 results (excluding definition in registry.py).

---

## Initial Analysis

### Current State Summary

| Metric | Count |
|--------|-------|
| Files using `get_default_registry_provider()` | 18 |
| Files using `get_default_registries()` | 13 |
| Files with `_get_registries_fallback()` implementations | 4 |
| Module-level registry constants | 3 |
| Test files requiring updates | ~120+ |

### Global State Locations

**Definition (game/core/registry.py):**
- `_default_registries` (line 80) - Module-level global
- `_default_provider` (line 514) - Singleton provider
- `get_default_registry_provider()` (lines 517-531) - Factory function
- `get_default_registries()` (lines 97-116) - Accessor with exception
- `set_default_registries()` (lines 83-94) - Setter called by app.py

**Module-Level Constants (executed at import time):**
- `game/simulation/components/component.py:81-82` - COMPONENT_REGISTRY, MODIFIER_REGISTRY
- `game/simulation/entities/ship.py:27` - VEHICLE_CLASSES

### Fallback Pattern Implementations

Located in 4 files with identical two-tier fallback pattern:
1. `game/simulation/components/component.py:85-110` - `_get_registries_fallback()`
2. `game/simulation/entities/ship.py:49-67` - `Ship._get_registries_fallback()`
3. `game/strategy/services/ship_stats_calculator.py:72-90` - `_get_registries_fallback()`
4. `game/simulation/services/vehicle_design_service.py:52-71` - `_get_registries_fallback()`

---

## Swarm Findings Summary

### Architecture Analysis

**Three-Tier Access Pattern (Current):**
```
TIER 1 - Module-level dicts (Hot-reload support):
  COMPONENT_REGISTRY = get_default_registry_provider().get_components()

TIER 2 - Provider fallback pattern (PROJ-38 transitional):
  registries = registries if registries else _get_registries_fallback()

TIER 3 - Pure DI (Target state):
  def __init__(self, *, registries: GameRegistries):  # Required, no default
```

**Layer Coupling:**
- **Core Layer** - Decoupled (defines global state intentionally)
- **Simulation Layer** - HIGH coupling (Component, Ship use module-level dicts + fallback)
- **Strategy Layer** - MEDIUM coupling (services accept registries but have fallback)
- **UI Layer** - MIXED (WorkshopViewModel strict, other widgets have fallback)

### Key Patterns to Reuse

**Gold Standard - WorkshopViewModel (game/ui/screens/workshop_viewmodel.py:66-70):**
```python
if context is None or context.registries is None:
    raise ValueError(
        "WorkshopViewModel requires a WorkshopContext with registries. "
        "Pass context=WorkshopContext(mode=..., registries=...) to constructor."
    )
self._registries: GameRegistries = context.registries
```

This is the TARGET PATTERN: Required parameter, clear error message, no fallback.

**Test Fixtures (tests/conftest.py):**
- `session_registries` (lines 118-146) - Session-scoped, loaded once
- `fresh_registries` (lines 149-173) - Function-scoped, deep-copied
- `minimal_registries` (lines 176-194) - Empty for isolated tests

### Dependencies & Risks

**HIGH Severity:**
1. **Module-level import-time execution** - COMPONENT_REGISTRY, VEHICLE_CLASSES execute at import before app.py sets registries
   - Mitigation: Remove module-level constants, use lazy access via DI

2. **Parallel test worker isolation** - Import race conditions in pytest-xdist
   - Mitigation: Pre-import modules in session scope, ensure fixture runs first

3. **Widget race during hot reload** - UI may see partial data during reload
   - Mitigation: Transactional reload or START/COMPLETE event pattern

**MEDIUM Severity:**
4. **Strategy layer missing DI** - `ShipInstance.to_ship()`, `Fleet.to_battle_ships()` have no registries parameter
   - Mitigation: Add optional registries parameter with fallback for backward compat

5. **Clone uses old registries** - `Component.clone()` uses original registries
   - Mitigation: Clone should use current registries or inherit from ship

6. **Scripts bypass app.py** - CLI tools don't initialize registries
   - Mitigation: Document requirement, add bootstrap function

### Data Flow Gaps

**Critical Missing DI Paths:**
1. `ShipInstance.to_ship()` - NO registries parameter
2. `Fleet.to_battle_ships()` - NO registries parameter
3. `SimulationBattleResolver.resolve_battle()` - NO registries to pass

All three are in the same call chain for strategy-to-simulation battle initialization.

### Opportunities Discovered

1. **WorkshopViewModel pattern already strict** - Can use as reference implementation
2. **Test fixtures already support DI** - `fresh_registries` fixture exists
3. **Serialization already has DI support** - `ShipSerializer.from_dict()` accepts registries
4. **BattleState.to_ship() has DI** - Good pattern to follow

---

## Design Decisions

### Decision 1: Strict at ViewModel Boundary (User-approved)
- WorkshopViewModel is the strict DI boundary for UI
- Widgets get registries from ViewModel, no fallbacks in widgets
- Rationale: Simplifies UI layer, single injection point

### Decision 2: Adapt Stages Based on Findings (User-approved)
- User's 5 stages are a guide, not rigid structure
- Additional files found will be incorporated
- Goal: Complete migration to strict DI with no fallbacks

### Decision 3: Keep Module-Level Constants for Hot-Reload
- COMPONENT_REGISTRY, MODIFIER_REGISTRY must remain for UI hot-reload
- BUT: Convert from import-time assignment to lazy property pattern
- Rationale: Hot-reload requires mutable dict refs; lazy pattern avoids import-time issues

### Decision 4: Test Baseline Deferred
- Current 46 test failures are pre-existing (another project in progress)
- PROJ-50 will establish new baseline when implementation starts
- Do not attempt to fix unrelated test failures

---

## Implementation Strategy

### Safe Migration Order (Leaf → Root)

```
Phase 1: Test Infrastructure (LEAF - no code dependents)
├─ Update test fixtures in conftest.py
├─ Create mock_registries fixture pattern
└─ Update tests/fixtures/ships.py factory

Phase 2: UI Layer (Few dependents)
├─ builder_widgets.py - Remove fallback
├─ workshop_screen.py - Pass from context
├─ workshop_event_router.py - Pass from context
└─ workshop_data_loader.py - Pass from context

Phase 3: Strategy Layer Services
├─ ship_stats_calculator.py - Remove fallback
└─ resource_management_engine.py - Remove fallback

Phase 4: Strategy Layer Data (NEW - fills gaps)
├─ ship_instance.py - Add registries parameter
├─ fleet.py - Add registries parameter
└─ simulation_adapter.py - Pass registries through

Phase 5: Simulation Services
├─ modifier_service.py - Remove fallback
├─ vehicle_design_service.py - Remove fallback
└─ ship_loader.py - Remove direct provider calls

Phase 6: Core Entities (ROOT - many dependents)
├─ component.py - Make registries required
├─ ship.py - Make registries required
├─ ship_serialization.py - Remove fallback
├─ battle_state.py - Remove fallback
├─ ship_validator.py - Remove fallback
└─ ship_component_manager.py - Remove fallback

Phase 7: Big Bang Removal
├─ Remove get_default_registry_provider() from registry.py
├─ Remove _default_provider global
├─ Remove set_default_registries() (keep app.py initialization)
└─ Update app.py entry point
```

### Constructor Signature Changes

**Before (current):**
```python
def __init__(self, data, *, registries: Optional[GameRegistries] = None):
    self._registries = registries if registries else _get_registries_fallback()
```

**After (strict DI):**
```python
def __init__(self, data, *, registries: GameRegistries):
    if registries is None:
        raise TypeError("registries parameter is required")
    self._registries = registries
```

### Module-Level Constants Strategy

**Before:**
```python
COMPONENT_REGISTRY = get_default_registry_provider().get_components()
```

**After (lazy property):**
```python
def get_component_registry() -> Dict[str, Any]:
    """Get component registry. Requires registries to be initialized."""
    return RegistryManager.instance().components
```

Or keep for hot-reload but document clearly:
```python
# PROJ-50: Kept for UI hot-reload compatibility. Dict ref is shared with RegistryManager.
# Do NOT use for new code - use dependency injection instead.
COMPONENT_REGISTRY = get_default_registry_provider().get_components()
```

---

## Verification Strategy

### After Each Phase
- Run `pytest tests/ --testmon` - affected tests pass
- Run `grep -r "get_default_registry_provider" game/` - count decreases

### Final Verification
- `grep -r "get_default_registry_provider" game/` returns only registry.py definition
- `grep -r "_get_registries_fallback" game/` returns 0 results
- Full test suite passes: `pytest tests/ -n 4`
- Game launches and runs: `python -m game.app`
- Workshop opens and creates ship
- Battle simulation completes

---

## Files Reference

### Core Files to Modify

| Component | File Path | Changes |
|-----------|-----------|---------|
| Global State | `game/core/registry.py` | Remove provider functions (Phase 7) |
| Component | `game/simulation/components/component.py` | Remove fallback, require registries |
| Ship | `game/simulation/entities/ship.py` | Remove fallback, require registries |
| ShipSerializer | `game/simulation/entities/ship_serialization.py` | Remove fallback |
| BattleState | `game/simulation/battle_state.py` | Remove fallback |
| ShipValidator | `game/simulation/ship_validator.py` | Remove fallback |
| ShipStatsCalculator | `game/strategy/services/ship_stats_calculator.py` | Remove fallback |
| VehicleDesignService | `game/simulation/services/vehicle_design_service.py` | Remove fallback |
| ShipInstance | `game/strategy/data/ship_instance.py` | Add registries parameter |
| Fleet | `game/strategy/data/fleet.py` | Add registries parameter |

### Test Files to Update

- `tests/conftest.py` - Ensure fixtures work with strict DI
- `tests/fixtures/ships.py` - Add registries to factory functions
- `tests/repro_issues/` - 24 files need registries parameter
- All service test files - Inject registries via fixtures
