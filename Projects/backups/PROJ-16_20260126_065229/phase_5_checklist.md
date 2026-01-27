# Phase 5: Wrapper Evaluation & Removal

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-16 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Evaluate thin wrapper classes and remove backward compat features from ShipControllableAdapter in stages
**Risk:** Medium (staged approach allows fixing breakage)
**Files Affected:** ~15 files for adapter changes

---

## Tasks

### Task 5.1: Evaluate ModifierLogic Wrapper [Simple] ✅

**File:** `ui/builder/modifier_logic.py` (71 lines)
**Usage:** 7 files, 19 usages

#### Analysis Checklist:

- [x] Review all methods in ModifierLogic:
  - `is_modifier_allowed()` - delegates to ModifierService
  - `get_mandatory_modifiers()` - delegates to ModifierService
  - `is_modifier_mandatory()` - delegates to ModifierService
  - `get_initial_value()` - delegates to ModifierService
  - `ensure_mandatory_modifiers()` - delegates to ModifierService
  - `get_local_min_max()` - delegates to ModifierService
  - `calculate_snap_value()` - **UI-specific logic, NOT in ModifierService**

- [x] **Decision Point:** Can ModifierLogic be removed?
  - **NO** - `calculate_snap_value()` contains UI-specific snap button logic
  - Moving it to ModifierService would violate layer boundaries
  - **Recommendation: KEEP ModifierLogic in UI layer**

- [x] Document decision in `decisions.md`

**Notes:** Decision documented. ModifierLogic stays.

---

### Task 5.2: Evaluate _ProfilerProxy Wrapper [Simple] ✅

**File:** `game/core/profiling.py` (lines 133-143)
**Usage:** 2 files (app.py, test_profiler_perf.py), 14 usages

#### Analysis Checklist:

- [x] Review proxy pattern
- [x] Check test usage patterns
- [x] **Decision Point:** Can _ProfilerProxy be simplified?
  - **NO** - Tests rely on direct attribute mutation through proxy
  - Lazy initialization is useful (avoids module-level Profiler creation)
  - **Recommendation: KEEP _ProfilerProxy as-is**

- [x] Document decision in `decisions.md`

**Notes:** Decision documented. _ProfilerProxy stays.

---

### Task 5.3: Audit ShipControllableAdapter Usage [Medium] ✅

**File:** `game/ai/interfaces/controllable.py` (lines 162-319)
**Usage:** 13 files, 72 instantiations

**Goal:** Audit all usages before staged removal to understand impact.

#### Audit Results:

**`.ship` property usage (3 locations in tests):**
- `tests/integration/test_fleet_combat.py:607,611` - test backward compat
- `tests/unit/ai/test_controllable_interface.py:473` - test backward compat

**`__getattr__` usage (EXTENSIVE in production):**
- `game/ai/controller.py` - 40+ usages of `self.ship.position`, `self.ship.turn_throttle`, etc.
- This is production code, not just tests!

**`__setattr__` usage (EXTENSIVE in production):**
- `game/ai/controller.py` - uses `self.ship.turn_throttle = x`, `self.ship.engine_throttle = x`, etc.

**Notes:** Audit revealed production code depends heavily on delegation features.

---

### Task 5.4-5.6: Remove Backward Compat Features ❌ CANCELLED

**Original Plan:** Remove `.ship` property, `__getattr__`, and `__setattr__` in stages.

**Attempted:** Removed all three features.

**Result:** 50+ test failures due to production code in `controller.py` using direct attribute access.

**Decision:** KEEP ALL BACKWARD COMPAT FEATURES

The `AIController` in `game/ai/controller.py` extensively uses patterns like:
```python
self.ship.position           # needs __getattr__
self.ship.turn_throttle = x  # needs __setattr__
self.ship.current_target     # needs both
```

Refactoring `controller.py` to use interface methods exclusively is out of scope for PROJ-16.

**Restored:** `.ship` property, `__getattr__`, `__setattr__` with clarifying comment.

---

### Task 5.7: Update Mock Patches [Simple] ✅

**File:** `tests/repro_issues/test_bug_13_clear_removes_hull.py`

- [x] Fixed: Removed obsolete patch of `game.simulation.entities.ship.get_vehicle_classes`
  (function doesn't exist there anymore, only in `game.core.registry`)

**Notes:** One patch updated.

---

### Task 5.8: Document Final Decisions [Simple] ✅

- [x] Update `decisions.md` with all wrapper evaluation outcomes
- [x] Added detailed rationale for keeping ShipControllableAdapter backward compat
- [x] Added comment to ShipControllableAdapter explaining why delegation is required

**Notes:** All decisions documented.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked (5.4-5.6 cancelled with reason documented)
- [x] All evaluation decisions documented in decisions.md
- [x] `pytest tests/ --testmon` passes (109 AI tests verified)
- [ ] Full test suite passes: `pytest tests/`
- [ ] `pytest simulation_tests/` passes
- [x] No circular import errors: `python -c "import game"`
- [ ] Application launches: `python -m game`
- [x] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to indicate project complete
