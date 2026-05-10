# PROJ-15: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### Baseline Test Status
- Full test suite: 4561 passed, 1 skipped, 189 warnings
- Pre-existing flaky test: `test_intercept_integration` (passes alone, fails in parallel)
- Pre-existing test isolation issues in strategy tests

### Shim Files Identified (5 total)
1. `game/ui/screens/builder_screen.py` - Complex wrapper (154 lines) with __getattr__ delegation
2. `game/ui/screens/builder_viewmodel.py` - Simple alias (9 lines)
3. `game/ui/screens/builder_data_loader.py` - Simple alias (9 lines)
4. `game/ui/screens/builder_event_router.py` - Simple alias (9 lines)
5. `game/simulation/services/ship_builder_service.py` - Simple alias (12 lines)

### Method Aliases Identified
- Fleet warp: `has_energy_for_warp()` → `has_resources_for_warp()`, `consume_warp_energy()` → `consume_warp_resources()`
- PathSegment: `.hex` property → `.end` property
- Ship stats: `to_hit_profile` → `total_defense_score`
- Singletons: `get_instance()` → `instance()` (3 classes)

### Deprecated Functions Identified
- `load_combat_strategies()` - Replaced by lazy loading in StrategyManager
- `_execute_move_step()` - Emits DeprecationWarning, replaced by `_calculate_next_hex()`

## Swarm Findings Summary

### Architecture Analysis
- **Module boundaries are clean** - No circular dependencies exist
- **Shims don't mask layering violations** - All are within same layer (UI→UI, Service→Service)
- **Public API impact is limited** - ShipBuilderService re-exported in services/__init__.py, Builder shims re-exported in ui/__init__.py
- **BuilderSceneGUI is NOT a simple alias** - It's a sophisticated wrapper that transforms old API signature to new WorkshopContext-based API

### Dependency Map
**Builder Shims Import Chain:**
```
game/app.py → builder_screen.py → workshop_screen.py
tests/unit/builder/* (9 files) → builder_screen.py
tests/unit/builder/test_builder_data_loader.py → builder_data_loader.py (8 dynamic imports)
```

**ShipBuilderService Import Chain:**
```
game/ui/screens/workshop_viewmodel.py → services/__init__.py → ship_builder_service.py → vehicle_design_service.py
```

**Singleton Usage:**
- SpriteManager.get_instance(): 4 locations (app.py, workshop_screen.py, test files)
- ShipThemeManager.get_instance(): 7 locations (workshop_screen.py, game_renderer.py, test files)
- ScreenshotManager.get_instance(): 2 locations (workshop_screen.py, test file)

### Test Impact Analysis
**Files Requiring Updates:**
- 9 test files import from builder_screen shim
- 8 dynamic imports in test_builder_data_loader.py
- 14 test files use get_instance() singleton pattern
- 1 test class (`TestBackwardCompatibility`) tests deprecated aliases - should be deleted
- 1 test file calls `_execute_move_step()` - needs update

### Key Patterns to Reuse
- **Singleton pattern**: `@classmethod instance(cls)` with double-checked locking
- **ViewModel pattern**: Dependency injection of event_bus, properties with setters that emit events
- **Service result pattern**: `DesignResult` dataclass with success/errors/warnings

### Dependencies & Risks
1. **BuilderSceneGUI wrapper complexity** - Transforms `(width, height, callback)` API to `(width, height, context)` API. Tests rely on __getattr__ delegation for mocking.
2. **workshop_viewmodel.py uses ShipBuilderService extensively** - Type annotations and instantiation need coordinated update.
3. **stats_layout.json uses to_hit_profile** - JSON key needs updating (NOT deprecated, still active)
4. **Test isolation issues** - Some tests fail when run in parallel due to shared mocking state.

### Opportunities Discovered
- After removing aliases, the codebase will have consistent naming
- Removing `load_combat_strategies()` simplifies strategy loading to lazy-only pattern
- Removing `get_instance()` aliases standardizes singleton access

## Design Decisions

### Decision 1: Include to_hit_profile removal
**Context:** Original Phase 2 doc suggested removal, but stats_layout.json uses it.
**Investigation:** stats_layout.json is NOT deprecated. It's the active configuration system for UI stats display.
**Decision:** Include removal. Simply update JSON key from `to_hit_profile` to `total_defense_score`.
**Rationale:** The alias exists only because total_defense_score replaced to_hit_profile. No functional difference.

### Decision 2: Defer project_path_as_dicts()
**Context:** Phase 2 doc mentions this wrapper.
**Investigation:** Used by `pathfinding.py` line 227, which expects dict format.
**Decision:** Defer to Phase 3.
**Rationale:** Requires updating pathfinding callers and potentially changing return format expectations.

### Decision 3: Keep TurnEngine._spawn_* methods
**Context:** Phase 2 doc marks these as "kept for backward compatibility".
**Investigation:** These are delegation methods to ProductionEngine, not aliases.
**Decision:** Do NOT remove in Phase 2.
**Rationale:** They serve as useful extension points for subclassing TurnEngine.

### Decision 4: Order phases by risk
**Context:** Many changes to coordinate.
**Decision:** Execute in order: Singletons → Fleet warp → ShipBuilderService → PathSegment → Deprecated functions → Builder shims
**Rationale:** Start with low-risk independent changes. End with highest-risk builder shims which have most test dependencies.

See [decisions.md](decisions.md) for the full log with rationale.
