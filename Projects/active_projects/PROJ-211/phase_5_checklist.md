# Phase 5: UI Screens & Cleanup

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-211 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Fix remaining UI screen violations and clean up docstrings
**Priority:** Low - Display-only code
**Risk:** Very low
**Depends on:** Phase 4 (WorkshopContext carries registries)

---

## Tasks

### Task 5.1: Fix compute_planet_production() [DI-UI-001]
**Files:** `game/ui/panels/planet_report_panel.py`
**Tests:** `pytest tests/unit/ui/panels/`

- [ ] Add `registries: Optional[GameRegistries] = None` parameter
- [ ] Update callers (strategy detail panel, build queue, planets list) to pass registries
- [ ] Remove fallback once all callers provide registries
- [ ] Verify: all tests pass

### Task 5.2: Fix EmpirePanelWindow [DI-UI-006]
**Files:** `game/ui/screens/empire_panel_window.py`
**Tests:** `pytest tests/unit/ui/screens/`

- [ ] Add `registries` parameter to `__init__()`
- [ ] Use stored registries in `_build_treasury_tab()` instead of inline resolution
- [ ] Update StrategyScreen to pass registries when opening the panel
- [ ] Remove `get_default_registry_provider` import
- [ ] Verify: all tests pass

### Task 5.3: Fix builder sub-panels [DI-UI-007, DI-UI-008, AR-013]
**Files:** `game/ui/screens/builder/schematic_view.py`, `game/ui/screens/builder/right_panel.py`
**Tests:** `pytest tests/unit/ui/screens/builder/`

- [ ] Ensure DesignWorkshopScreen passes VehicleClassService to both sub-panels
- [ ] Remove fallback to `get_default_registry_provider()` in both constructors
- [ ] Verify: all tests pass

### Task 5.4: Update empire_economy_calculator docstring [DI-S-006]
**Files:** `game/strategy/engine/empire_economy_calculator.py`

- [ ] Update docstring "Usage" example to show proper DI from session context
- [ ] Remove example calling `get_default_registry_provider()` directly

### Task 5.5: Final verification - zero fallback calls outside composition roots
**Tests:** `pytest tests/ -n 12`

- [ ] Grep for `get_default_registry_provider()` across all production code
- [ ] Verify only `game/app.py`, `conftest.py`, and `game/core/registry.py` (definition site) contain it
- [ ] Verify `game/core/__init__.py` re-export is acceptable (public API for tests)
- [ ] Full test suite passes
- [ ] Document any remaining legitimate usages in decisions.md

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/ -n 12` - full suite passes
- [ ] Zero `get_default_registry_provider()` calls outside composition roots
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to "Project Complete"
