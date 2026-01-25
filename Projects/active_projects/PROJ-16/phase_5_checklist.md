# Phase 5: Remove Wrapper Classes

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-16 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Remove ModifierLogic wrapper and simplify ProfilerProxy

---

## Tasks

### Task 5.1: Move calculate_snap_value to ModifierControlRow [Medium]
**Files:** `ui/builder/modifier_logic.py`, `ui/builder/modifier_row.py`
**Tests:** `pytest tests/unit/ui/ tests/unit/entities/test_modifier*.py -x`

- [ ] Read `ui/builder/modifier_logic.py` to get `calculate_snap_value()` implementation
- [ ] Add `calculate_snap_value()` as static method in `ModifierControlRow` class in `modifier_row.py`
- [ ] Update calls in `modifier_row.py:299,301` to use `ModifierControlRow.calculate_snap_value(...)`
- [ ] Verify: `pytest tests/unit/ui/ tests/unit/entities/test_modifier*.py -x`

**Notes:**

---

### Task 5.2: Update ModifierLogic callers to use ModifierService [Medium]
**Files:** `ui/builder/modifier_row.py`, `ui/builder/detail_panel.py`, `game/ui/panels/builder_widgets.py`
**Tests:** `pytest tests/unit/ui/ tests/unit/builder/ -x`

- [ ] In each file, change import from `from ui.builder.modifier_logic import ModifierLogic` to `from game.simulation.services import ModifierService`
- [ ] Replace all `ModifierLogic.method()` calls with `ModifierService.method()`
- [ ] Methods are 1:1 compatible:
  - `is_modifier_allowed`
  - `get_mandatory_modifiers`
  - `is_modifier_mandatory`
  - `get_initial_value`
  - `ensure_mandatory_modifiers`
  - `get_local_min_max`
- [ ] Verify: `pytest tests/unit/ui/ tests/unit/builder/ -x`

**Notes:**

---

### Task 5.3: Update test files using ModifierLogic [Simple]
**Files:** Test files that import ModifierLogic
**Tests:** `pytest tests/unit/entities/test_modifier*.py tests/unit/ui/test_detail*.py -x`

- [ ] `tests/unit/ui/test_detail_panel_rendering.py` - update patch target
- [ ] `tests/unit/entities/test_modifier_defaults_robustness.py` - update import
- [ ] `tests/unit/entities/test_mandatory_updates.py` - update import
- [ ] `Tools/quick_test_modifiers.py` - update import
- [ ] Verify: `pytest tests/unit/entities/test_modifier*.py tests/unit/ui/test_detail*.py -x`

**Notes:**

---

### Task 5.4: Delete ModifierLogic and update __init__.py [Simple]
**Files:** `ui/builder/modifier_logic.py`, `ui/builder/__init__.py`
**Tests:** `pytest tests/unit/ -x`

- [ ] Delete file: `ui/builder/modifier_logic.py`
- [ ] Update `ui/builder/__init__.py` - remove `from .modifier_logic import ModifierLogic` line
- [ ] Verify: `pytest tests/unit/ -x`

**Notes:**

---

### Task 5.5: Simplify ProfilerProxy [Simple]
**File:** `game/core/profiling.py:133-144`
**Tests:** `pytest tests/unit/core/test_profiling.py tests/unit/performance/test_profiler*.py -x`

- [ ] Replace `_ProfilerProxy` class and `PROFILER = _ProfilerProxy()` with:
  ```python
  # Simple module-level instance (Profiler.instance() is thread-safe)
  PROFILER = Profiler.instance()
  ```
- [ ] Delete `_ProfilerProxy` class definition (lines 133-143)
- [ ] Verify: `pytest tests/unit/core/test_profiling.py tests/unit/performance/test_profiler*.py -x`

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `ui/builder/modifier_logic.py` deleted
- [ ] `_ProfilerProxy` class removed from profiling.py
- [ ] `pytest tests/unit/ -x` passes
- [ ] `pytest tests/ -v` passes (full test suite)
- [ ] `pytest simulation_tests/ -v` passes
- [ ] Application launches and runs correctly
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to indicate project complete
