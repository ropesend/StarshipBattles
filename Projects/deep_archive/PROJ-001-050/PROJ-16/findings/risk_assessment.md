# Risk Assessment - PROJ-16

**Agent Role:** Risk Assessor
**Date:** 2026-01-25

## Critical Path Analysis

### Game Initialization (game/app.py)
- **Line 27:** Direct import of PROFILER from game.core.profiling
- **Lines 498-499, 724, 744:** Uses PROFILER.toggle(), is_active(), save_history()
- **Risk:** HIGH - Core application initialization
- **Mitigation:** Keep PROFILER proxy, test app launch after ship_loader changes

### Battle Engine Initialization
- Uses direct imports from modules (not re-exports)
- **Risk:** MEDIUM
- **Mitigation:** No changes needed for re-export removal

### Ship Loading
- **game/simulation/entities/ship.py** re-exports from ship_loader
- Critical for initialize_ship_data() used everywhere
- **Risk:** MEDIUM - Many test fixtures depend on this
- **Mitigation:** Update test fixtures first, test incrementally

## Dynamic Import Risks

### Test Framework (test_framework/runner.py)
- Lines 215-217, 220: Uses `importlib.import_module()` for scenarios
- **Risk:** MEDIUM - Dynamically loaded scenarios may import re-exports
- **Mitigation:** Test scenario loading after consolidation

### Formula System (game/simulation/formula_system.py)
- Uses ast.parse() for validation, blocks `__import__`, `eval()`, `exec()`
- **Risk:** LOW - No dynamic imports used
- **Mitigation:** None needed

## ModifierLogic Removal Risk

**Risk Level:** HIGH - CANNOT REMOVE

`calculate_snap_value()` (lines 48-70) contains UI-specific logic:
- `smart_floor` parameter controls Size Mount special behavior
- This is presentation logic, not business logic
- Moving to ModifierService would violate layer boundaries

**Recommendation:** KEEP ModifierLogic in UI layer

## PROFILER Proxy Removal Risk

**Risk Level:** HIGH - SHOULD NOT REMOVE

Tests directly mutate PROFILER fields:
```python
PROFILER.active = False
PROFILER.records = []
```

The proxy provides:
1. Lazy initialization (delays Profiler.instance() until first use)
2. Stable API for direct attribute mutation

**Recommendation:** KEEP _ProfilerProxy as-is

## ShipControllableAdapter Backward Compat Risk

**Risk Level:** MEDIUM - CAN REMOVE IN STAGES

| Feature | Production Usage | Test Usage | Removal Risk |
|---------|-----------------|------------|--------------|
| `.ship` property | None | Yes (mock setup) | LOW |
| `__getattr__` | Unknown | Yes (legacy tests) | MEDIUM |
| `__setattr__` | Possible | Yes | HIGH - audit first |

**Recommendation:** Remove in 3 stages with testing between each

## Summary Risk Table

| Risk Area | Severity | Mitigation |
|-----------|----------|------------|
| ModifierLogic removal | HIGH | Keep in UI layer |
| PROFILER proxy removal | HIGH | Keep proxy |
| App initialization | MEDIUM | Test launch after changes |
| Test fixtures | MEDIUM | Update fixtures first |
| Mock patches | MEDIUM | Update before removing re-exports |
| Dynamic imports | LOW | Test scenario loading |
| ShipControllableAdapter | MEDIUM | Staged removal |
