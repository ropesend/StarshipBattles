# PROJ-16: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

Phase 3 of the Legacy Cleanup project focuses on consolidating re-exports - updating callers to import from canonical module locations and removing backward-compatibility re-exports.

### Scope Summary

**Re-exports to Remove:**
1. `game/simulation/components/component.py` → re-exports ComponentStatus, LayerType, Modifier, ApplicationModifier from component_constants (65 files affected)
2. `game/simulation/entities/ship.py` → re-exports get_or_create_validator, load_vehicle_classes, initialize_ship_data from ship_loader (67 files affected)
3. `game/ai/controller.py` → re-exports StrategyManager, get_strategy_names, reset_strategy_manager, TargetEvaluator (40+ files affected)
4. `game/strategy/data/planet.py` → re-exports PLANET_RESOURCES from game.core.constants (8 files affected)

**Thin Wrappers to Evaluate:**
1. `ui/builder/modifier_logic.py` - ModifierLogic wrapper (7 files, 19 usages)
2. `game/core/profiling.py` - _ProfilerProxy (2 files, 14 usages)
3. `game/ai/interfaces/controllable.py` - ShipControllableAdapter backward compat features

### Key Finding: Import Path Statistics

| Re-export Source | Files Using Re-export | Files Using Canonical | Migration Scope |
|------------------|----------------------|----------------------|-----------------|
| component.py → component_constants | 65 | 5 | High |
| ship.py → ship_loader | 67 | 0 | High |
| controller.py → strategy_manager | 38 | 1 | High |
| controller.py → target_evaluator | 2 | 3 | Low |
| planet.py → constants | 8 | 0 | Low |

## Swarm Findings Summary

### Architecture Analysis

**Circular Import Risk: NONE DETECTED**
- All re-export removals are architecturally safe
- Canonical modules have no dependencies on re-export locations
- One-way dependency chains maintained

**Layer Violations Identified:**
- `planet.py` re-exporting from `core.constants` is an inverse dependency (strategy → core re-export)
- UI layer correctly imports from simulation layer (not a violation)

**Module Design Issues:**
- `component.py` violates SRP by being both Component class definition AND constant re-exporter
- `ship.py` re-exports obscure that ship_loader handles initialization, not Ship class
- `controller.py` re-exports hide singleton nature of StrategyManager

### Dependency Map

**Cross-Layer Import Patterns:**
- UI → Simulation: 13 files import ComponentStatus/LayerType
- UI → AI: 7 files import StrategyManager from controller
- Tests → All layers: Direct canonical imports mostly

**Package __init__.py Status:**
- `game/simulation/components/__init__.py` - EMPTY
- `game/simulation/entities/__init__.py` - DOES NOT EXIST
- `game/ai/__init__.py` - EMPTY
- `game/core/__init__.py` - Exports Vector2, clamp, lerp, angle_diff (well-designed)

### Test Impact Analysis

**Critical Test Fixtures Affected:**
- `tests/conftest.py` - Session-level ship data initialization
- `tests/fixtures/components.py` - Component factory functions (used by 141 tests)
- `tests/fixtures/ships.py` - Ship fixtures (used by 100 tests)
- `simulation_tests/conftest.py` - Simulation test setup

**Mock Patches That Will Break:**
- `tests/repro_issues/test_bug_13_clear_removes_hull.py:34-35` patches re-export paths

### Key Patterns to Reuse

- **PROJ-11 Pattern**: `game/ui/screens/fleet_report_filters.py:11-29` - Re-export with backward compat comment, docstring with migration instructions
- **Deprecation Pattern**: `game/strategy/engine/turn_engine.py:264-272` - warnings.warn() with DeprecationWarning
- **Interface Export Pattern**: `game/ai/interfaces/__init__.py` - Clean `__all__` with PROJ docstring

### Dependencies & Risks

1. **HIGH - ModifierLogic.calculate_snap_value**: UI-specific method that CANNOT move to ModifierService without violating layer boundaries. Keep in UI layer.

2. **HIGH - PROFILER Proxy Pattern**: Tests directly mutate `PROFILER.active` and `PROFILER.records`. Proxy provides lazy initialization. Keep proxy, simplify if needed.

3. **MEDIUM - Dynamic Imports**: `test_framework/runner.py` uses `importlib.import_module()` for scenarios

4. **LOW - ShipControllableAdapter**: Backward compat features (.ship, __getattr__, __setattr__) used minimally. Can remove .ship and __getattr__; audit __setattr__ first.

### Opportunities Discovered

1. **Create formal export points**: `game/simulation/__init__.py` and `game/simulation/entities/__init__.py` could provide stable API surface
2. **Consolidate constants**: PLANET_RESOURCES already moved to core.constants per PROJ-11 - just need to remove re-export
3. **Simplify PROFILER**: Could replace proxy with `PROFILER = Profiler.instance()` if lazy init not needed

## Design Decisions

See [decisions.md](decisions.md) for the full log with rationale.

### Decision 1: Keep ModifierLogic in UI Layer
**Rationale:** `calculate_snap_value()` contains UI-specific snap-button logic. Moving to ModifierService would violate layer separation.

### Decision 2: Keep PROFILER Proxy
**Rationale:** Tests rely on direct attribute mutation (`PROFILER.active = False`). Proxy enables lazy initialization and provides stable API.

### Decision 3: Remove PLANET_RESOURCES re-export from planet.py
**Rationale:** Already marked as backward compat bridge from PROJ-11. Only 8 files to update.

### Decision 4: Phase Removals by Risk
**Order:**
1. PLANET_RESOURCES (trivial)
2. Component constants (isolated)
3. AI re-exports (test infrastructure)
4. Ship loader functions (critical path)
