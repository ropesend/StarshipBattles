# PROJ-16: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

Phase 3 is part of an 8-phase Legacy Code Cleanup initiative. Phase 1 (Delete Dead Code) is complete, and Phase 2 (Remove Shims & Aliases) is being tracked as PROJ-15.

**Phase 3 Goal:** Consolidate re-exports by updating all callers to import from canonical module locations, then removing backward compatibility re-exports.

### Re-Export Inventory

| Source Module | Re-exported Items | Canonical Source | Incorrect Imports |
|---------------|-------------------|------------------|-------------------|
| `component.py` | LayerType (48), ComponentStatus (6), Modifier/ApplicationModifier (11) | `component_constants.py` | 65 files |
| `controller.py` | StrategyManager (36), TargetEvaluator (0 - dead) | `strategy_manager.py`, `target_evaluator.py` | 36 files |
| `ship.py` | get_or_create_validator (3), initialize_ship_data (1) | `ship_loader.py` | 4 files |
| `planet.py` | PLANET_RESOURCES (7) | `core/constants.py` | 7 files |

### Wrapper Classes Assessment

| Wrapper | Location | Assessment | Action |
|---------|----------|------------|--------|
| ModifierLogic | `ui/builder/modifier_logic.py` | Pure pass-through wrapper (6 methods delegate to ModifierService) | **REMOVE** - move `calculate_snap_value()` to UI utility |
| _ProfilerProxy | `game/core/profiling.py:133-144` | Lazy initialization proxy for PROFILER global | **SIMPLIFY** - replace with `PROFILER = Profiler.instance()` |
| ShipControllableAdapter | `game/ai/interfaces/controllable.py` | Essential adapter pattern for AI system | **KEEP** - not a candidate for removal |

---

## Swarm Findings Summary

### Architecture Analysis

**Current Package Structure Issues:**
- `game/simulation/components/__init__.py` - EMPTY (no package-level API)
- `game/simulation/entities/__init__.py` - DOES NOT EXIST
- `game/ai/__init__.py` - EMPTY (no package-level API)

**Well-Designed Packages (model to follow):**
- `game/simulation/services/__init__.py` - Proper facade with `__all__`
- `game/ai/interfaces/__init__.py` - Proper facade with `__all__`
- `ui/builder/__init__.py` - Exports key UI components

**Recommendation:** Create proper `__init__.py` facades for packages, then update callers to use package-level imports. This maintains convenience while establishing proper architecture.

### Dependency Mapping

**Critical Import Chains (must update in order):**

1. **Root conftest.py** (CRITICAL - affects ALL tests)
   - Line 55, 68: `from game.ai.controller import StrategyManager`
   - This is autouse fixture that runs for EVERY test

2. **Test Fixtures** (affects 100+ tests)
   - `tests/fixtures/components.py` - imports from `component.py`
   - `tests/fixtures/ships.py` - imports from `component.py` and `ship.py`
   - `tests/fixtures/ai.py` - imports from `controller.py`

3. **Production Code** (23 files)
   - Core simulation, AI, UI screens

**Import Update Order (DEPENDENCIES FIRST):**
1. Create `__init__.py` files with re-exports
2. Update root conftest.py
3. Update test fixtures
4. Update production code
5. Remove old re-exports from source modules
6. Update remaining test files (bulk)

### Test Impact

**Import Statistics:**
- `component.py` imports: 188 occurrences in 113 test files
- `ship.py` imports: 151 occurrences in 91 test files
- `controller.py` imports: 17 occurrences in 17 test files

**Fixture Dependencies:**
- `tests/fixtures/components.py` - Used by 60+ tests
- `tests/fixtures/ships.py` - Used by 50+ tests
- `tests/fixtures/ai.py` - Used by 10+ tests

**No explicit tests for re-export behavior** - Tests use imports indirectly

### Key Patterns to Reuse

- **Import Style**: `from X import Y` with parentheses for multi-line imports
- **TYPE_CHECKING blocks**: Used in 36+ files for circular dependency prevention
- **Backward compatibility comment**: `# Re-export from X for backward compatibility`
- **Package facade pattern**: See `game/simulation/services/__init__.py` for model

### Risks & Mitigations

1. **ROOT conftest.py breaks all tests**
   - Mitigation: Update FIRST, verify with `pytest --collect-only`

2. **Test fixture chain breaks**
   - Mitigation: Update fixtures BEFORE individual test files

3. **ModifierLogic.calculate_snap_value() is UI-specific**
   - Mitigation: Move to ModifierControlRow or keep as minimal utility

4. **ProfilerProxy provides lazy initialization**
   - Mitigation: Direct assignment is safe IF done after module load

5. **Dynamic imports in TestRegistry**
   - Mitigation: Update scenario imports before running registry

### Opportunities Discovered

1. **Dead code found**: `TargetEvaluator` re-export in `controller.py` is NEVER used (0 imports) - remove immediately

2. **Package facade improvement**: Creating proper `__init__.py` files will:
   - Maintain import convenience
   - Establish proper architecture
   - Enable IDE navigation improvements

3. **Cleaner architecture**: After Phase 3:
   - One canonical source per concept
   - Clear module boundaries
   - Self-documenting imports

---

## Design Decisions

### Decision 1: Use Package-Level Re-exports Instead of Module Re-exports

**Options Considered:**
- A) Just remove re-exports (force callers to use canonical paths)
- B) Move re-exports to `__init__.py` files (maintain convenience, proper architecture)

**Decision:** Option B - Create `__init__.py` package facades

**Rationale:**
- Maintains same import convenience
- Establishes professional Python package structure
- Follows existing pattern in `game/simulation/services/`
- Reduces import statement count per file

### Decision 2: ModifierLogic.calculate_snap_value() Handling

**Options Considered:**
- A) Keep ModifierLogic with only `calculate_snap_value()`
- B) Move to ModifierControlRow as static method
- C) Create new `ui/builder/modifier_utils.py`

**Decision:** Option B - Move to ModifierControlRow

**Rationale:**
- Only used in modifier_row.py (2 call sites)
- Natural home for UI-specific snap logic
- Eliminates entire wrapper file

### Decision 3: ProfilerProxy Simplification

**Options Considered:**
- A) Keep proxy for lazy initialization
- B) Direct assignment: `PROFILER = Profiler.instance()`
- C) Remove PROFILER, update all callers to use `Profiler.instance()`

**Decision:** Option B - Simplify to direct assignment

**Rationale:**
- instance() uses thread-safe double-checked locking
- Module-level assignment happens once at import
- Simpler code, same behavior
- Callers continue using PROFILER unchanged

### Decision 4: ShipControllableAdapter Status

**Decision:** KEEP - Not a Phase 3 candidate

**Rationale:**
- Essential adapter pattern for AI system
- Backward compat features (`ship` property, `__getattr__`) are actively tested
- Would require Ship to implement IControllable directly (separate project)

---

## Verification Strategy

### After Each Task
```bash
pytest --collect-only -q  # Verify imports don't break test collection
```

### After Each Phase
```bash
pytest tests/unit/ -x --tb=short  # Stop on first failure
python -c "import game.simulation.entities.ship; import game.ai.controller; print('OK')"  # Check circular imports
```

### Final Verification
```bash
pytest tests/ -v  # Full test suite
pytest simulation_tests/ -v  # Simulation tests
# Load existing save game from saves/1pQS/ to verify compatibility
```

### Import Verification Commands
```bash
# Verify no remaining old import patterns
grep -r "from game.simulation.components.component import ComponentStatus" --include="*.py"
grep -r "from game.simulation.components.component import LayerType" --include="*.py"
grep -r "from game.ai.controller import StrategyManager" --include="*.py"
grep -r "from game.simulation.entities.ship import get_or_create_validator" --include="*.py"
```
