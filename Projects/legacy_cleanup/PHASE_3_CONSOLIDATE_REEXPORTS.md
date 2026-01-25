# Phase 3: Consolidate Re-exports

**Project:** Legacy Code Cleanup
**Phase:** 3 of 8
**Risk Level:** Medium
**Dependencies:** Phase 2 complete

---

## High-Level Project Context

This phase is part of a comprehensive 8-phase legacy code cleanup effort:

| Phase | Name | Status |
|-------|------|--------|
| 1 | Delete Dead Code | Complete |
| 2 | Remove Shims & Aliases | Complete |
| **3** | **Consolidate Re-exports** | **THIS PHASE** |
| 4 | Enforce Layer Boundaries | Pending |
| 5 | Standardize Registry Access | Pending |
| 6 | Type Safety via Protocols | Pending |
| 7 | Standardize Data Formats | Pending |
| 8 | Clean Up Tests & Patterns | Pending |

**Overall Goal:** Clean up legacy code, enforce architectural boundaries, and standardize patterns across the Starship Battles codebase.

---

## Phase 3 Objectives

1. Update all callers to import from canonical module locations
2. Remove backward compatibility re-exports from modules
3. Consolidate shared constants to `game/core/constants.py`
4. Remove thin adapter/wrapper classes that only delegate

---

## Detailed Tasks

### 3.1 Update Component Module Imports

**File:** `game/simulation/components/component.py` (Lines 8-14)

Currently re-exports:
```python
from .component_constants import (
    ComponentStatus,
    LayerType,
    Modifier,
    ApplicationModifier,
)
```

**Steps:**
1. Search for imports of these from `component.py`:
   - `from game.simulation.components.component import ComponentStatus`
   - `from game.simulation.components.component import LayerType`
   - `from game.simulation.components.component import Modifier`
   - `from game.simulation.components.component import ApplicationModifier`

2. Update to import from `component_constants`:
   - `from game.simulation.components.component_constants import ComponentStatus`
   - etc.

3. Remove the re-export block from `component.py`

### 3.2 Update Ship Module Imports

**File:** `game/simulation/entities/ship.py` (Lines 20-25)

Currently re-exports:
```python
from .ship_loader import (
    get_or_create_validator,
    load_vehicle_classes,
    initialize_ship_data,
)
```

**Steps:**
1. Search for imports of these from `ship.py`:
   - `from game.simulation.entities.ship import get_or_create_validator`
   - `from game.simulation.entities.ship import load_vehicle_classes`
   - `from game.simulation.entities.ship import initialize_ship_data`

2. Update to import from `ship_loader`:
   - `from game.simulation.entities.ship_loader import get_or_create_validator`
   - etc.

3. Remove the re-export block from `ship.py`

### 3.3 Update AI Controller Imports

**File:** `game/ai/controller.py` (Lines 9-18)

Currently re-exports:
```python
from game.ai.strategy_manager import (
    StrategyManager,
    load_combat_strategies,  # Note: deprecated, may be removed in Phase 2
    get_strategy_names,
    reset_strategy_manager,
)

from game.ai.target_evaluator import TargetEvaluator
```

**Steps:**
1. Search for imports from `controller.py`:
   - `from game.ai.controller import StrategyManager`
   - `from game.ai.controller import get_strategy_names`
   - `from game.ai.controller import reset_strategy_manager`
   - `from game.ai.controller import TargetEvaluator`

2. Update to import from source modules:
   - `from game.ai.strategy_manager import StrategyManager`
   - `from game.ai.strategy_manager import get_strategy_names`
   - `from game.ai.target_evaluator import TargetEvaluator`

3. Remove the re-export block from `controller.py`

### 3.4 Consolidate Constants

**File:** `game/strategy/data/planet.py` (Line 7-8)
- Re-exports `PLANET_RESOURCES` for backward compatibility

**File:** `game/core/constants.py` (Lines 29-33)
- Has `WIDTH = DisplayConfig.DEFAULT_WIDTH` and similar

**Steps:**
1. Identify all shared constants that are re-exported
2. Ensure canonical location is `game/core/constants.py`
3. Update all callers to import from `constants.py`
4. Remove re-exports from `planet.py` and elsewhere

### 3.5 Remove Thin Wrapper Classes

#### 3.5.1 ModifierLogic Wrapper

**File:** `ui/builder/modifier_logic.py` (Lines 1-70)

This class wraps `ModifierService` with identical methods:
- All methods delegate to ModifierService
- Exposes `MANDATORY_MODIFIERS` for backward compatibility

**Steps:**
1. Find all usages of `ModifierLogic`
2. Update to use `ModifierService` directly
3. Update `MANDATORY_MODIFIERS` references to use source location
4. Delete `ui/builder/modifier_logic.py`

#### 3.5.2 _ProfilerProxy

**File:** `game/core/profiling.py` (Lines 133-144)

```python
class _ProfilerProxy:
    def __getattr__(self, name):
        return getattr(Profiler.instance(), name)
    def __setattr__(self, name, value):
        setattr(Profiler.instance(), name, value)

PROFILER = _ProfilerProxy()
```

**Steps:**
1. Find all usages of `PROFILER` global
2. Update to use `Profiler.instance()` directly
3. Remove `_ProfilerProxy` class
4. Either remove `PROFILER` or make it `PROFILER = Profiler.instance()` (simpler)

#### 3.5.3 Evaluate ShipControllableAdapter

**File:** `game/ai/interfaces/controllable.py` (Lines 160-316)

This adapter wraps Ship to implement IControllable. It has backward compatibility features:
- `ship` property for direct access
- `__getattr__`/`__setattr__` fallback delegation

**Evaluation needed:**
1. Is the adapter still needed after PROJ-12 completion?
2. Are there callers using the backward compatibility features?
3. If adapter is still needed, can backward compat features be removed?

**Possible outcomes:**
- Keep adapter, remove `__getattr__`/`__setattr__` if unused
- Keep adapter as-is if backward compat still needed
- Remove adapter entirely if Ship now implements IControllable directly

---

## Verification Checklist

After completing all tasks:

- [ ] All ComponentStatus/LayerType imports updated to component_constants
- [ ] Re-exports removed from component.py
- [ ] All ship_loader function imports updated
- [ ] Re-exports removed from ship.py
- [ ] All strategy_manager/target_evaluator imports updated
- [ ] Re-exports removed from controller.py
- [ ] Constants consolidated to game/core/constants.py
- [ ] ModifierLogic wrapper removed, callers updated
- [ ] _ProfilerProxy removed, PROFILER usage updated
- [ ] ShipControllableAdapter evaluated and updated as appropriate
- [ ] No circular imports
- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] Application launches and runs correctly

---

## Files Deleted

- `ui/builder/modifier_logic.py` (after migration)

## Files Modified

- `game/simulation/components/component.py` (remove re-exports)
- `game/simulation/entities/ship.py` (remove re-exports)
- `game/ai/controller.py` (remove re-exports)
- `game/strategy/data/planet.py` (remove re-exports)
- `game/core/profiling.py` (remove _ProfilerProxy)
- `game/ai/interfaces/controllable.py` (evaluate/update adapter)
- Various files updating import statements

---

## Import Verification Commands

After changes, verify no remaining re-export usage:

```bash
# Check for old component imports
grep -r "from game.simulation.components.component import ComponentStatus" --include="*.py"
grep -r "from game.simulation.components.component import LayerType" --include="*.py"

# Check for old ship imports
grep -r "from game.simulation.entities.ship import get_or_create_validator" --include="*.py"
grep -r "from game.simulation.entities.ship import load_vehicle_classes" --include="*.py"

# Check for old controller imports
grep -r "from game.ai.controller import StrategyManager" --include="*.py"
grep -r "from game.ai.controller import TargetEvaluator" --include="*.py"

# Check for circular imports
python -c "import game.simulation.entities.ship; import game.ai.controller; print('No circular imports')"
```

---

## Notes for Next Phase

Phase 4 (Enforce Layer Boundaries) will:
- Define strict layer architecture
- Remove pygame from Simulation layer
- Fix AI → Simulation layer violations
- Fix Simulation → AI/Strategy reverse dependencies
- Implement dependency injection where needed

Ensure all tests pass and no circular imports exist before proceeding to Phase 4.

---

*End of Phase 3 Plan*
