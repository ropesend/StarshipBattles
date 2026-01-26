# Phase 5: Wrapper Evaluation & Removal

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-16 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Evaluate thin wrapper classes and remove backward compat features from ShipControllableAdapter in stages
**Risk:** Medium (staged approach allows fixing breakage)
**Files Affected:** ~15 files for adapter changes

---

## Tasks

### Task 5.1: Evaluate ModifierLogic Wrapper [Simple]

**File:** `ui/builder/modifier_logic.py` (71 lines)
**Usage:** 7 files, 19 usages

#### Analysis Checklist:

- [ ] Review all methods in ModifierLogic:
  - `is_modifier_allowed()` - delegates to ModifierService
  - `get_mandatory_modifiers()` - delegates to ModifierService
  - `is_modifier_mandatory()` - delegates to ModifierService
  - `get_initial_value()` - delegates to ModifierService
  - `ensure_mandatory_modifiers()` - delegates to ModifierService
  - `get_local_min_max()` - delegates to ModifierService
  - `calculate_snap_value()` - **UI-specific logic, NOT in ModifierService**

- [ ] **Decision Point:** Can ModifierLogic be removed?
  - **NO** - `calculate_snap_value()` contains UI-specific snap button logic
  - Moving it to ModifierService would violate layer boundaries
  - **Recommendation: KEEP ModifierLogic in UI layer**

- [ ] Document decision in `decisions.md`

**Notes:**

---

### Task 5.2: Evaluate _ProfilerProxy Wrapper [Simple]

**File:** `game/core/profiling.py` (lines 133-143)
**Usage:** 2 files (app.py, test_profiler_perf.py), 14 usages

#### Analysis Checklist:

- [ ] Review proxy pattern:
  ```python
  class _ProfilerProxy:
      def __getattr__(self, name):
          return getattr(Profiler.instance(), name)
      def __setattr__(self, name, value):
          setattr(Profiler.instance(), name, value)

  PROFILER = _ProfilerProxy()
  ```

- [ ] Check test usage patterns:
  - `PROFILER.active = False` - direct attribute mutation
  - `PROFILER.records = []` - direct attribute mutation
  - `PROFILER.toggle()` - method call
  - `PROFILER.is_active()` - method call

- [ ] **Decision Point:** Can _ProfilerProxy be simplified?
  - **NO** - Tests rely on direct attribute mutation through proxy
  - Lazy initialization is useful (avoids module-level Profiler creation)
  - **Recommendation: KEEP _ProfilerProxy as-is**

- [ ] Document decision in `decisions.md`

**Notes:**

---

### Task 5.3: Audit ShipControllableAdapter Usage [Medium]

**File:** `game/ai/interfaces/controllable.py` (lines 162-319)
**Usage:** 13 files, 72 instantiations

**Goal:** Audit all usages before staged removal to understand impact.

#### Step 1: Audit `.ship` property usage

- [ ] Run: `grep -r "\.ship\b" tests/ game/ --include="*.py" | grep -v "_ship" | grep -v "self.ship"`
- [ ] Document all files using `.ship` on an adapter object
- [ ] Categorize: Production vs Test usage

#### Step 2: Audit `__getattr__` usage

- [ ] Search for access to non-interface attributes through adapter
- [ ] Check test files for attribute access patterns like `adapter.some_legacy_attr`

#### Step 3: Audit `__setattr__` usage

- [ ] Run: `grep -r "adapter\.[a-z_]* =" game/ tests/ --include="*.py"`
- [ ] Run: `grep -r "controllable\.[a-z_]* =" game/ tests/ --include="*.py"`
- [ ] Document any direct attribute assignment through adapter

**Notes:** (Document audit findings here before proceeding to removal)

---

### Task 5.4: Remove `.ship` Property (Stage 1) [Medium]

**File:** `game/ai/interfaces/controllable.py`
**Tests:** `pytest tests/unit/ai/test_controllable_interface.py -v`

**Prerequisite:** Task 5.3 audit complete

- [ ] Remove `.ship` property (lines 185-188):
  ```python
  @property
  def ship(self) -> Any:
      """Access the underlying ship (for backward compatibility)."""
      return self._ship
  ```

- [ ] Update any test files that access `.ship`:
  - Change `adapter.ship.attribute` to use mock's internal setup
  - Or use interface methods instead

- [ ] Run tests: `pytest tests/unit/ai/ -v`
- [ ] If tests fail, fix them before proceeding

**Notes:**

---

### Task 5.5: Remove `__getattr__` Delegation (Stage 2) [Medium]

**File:** `game/ai/interfaces/controllable.py`
**Tests:** `pytest tests/unit/ai/ -v`

**Prerequisite:** Task 5.4 complete and tests passing

- [ ] Remove `__getattr__` method (lines 190-197):
  ```python
  def __getattr__(self, name: str) -> Any:
      """Fallback attribute access to underlying ship."""
      return getattr(self._ship, name)
  ```

- [ ] Run tests: `pytest tests/unit/ai/ -v`
- [ ] If tests fail due to missing attributes:
  - Add the attribute to IControllable interface if it should be exposed
  - Or update test to not rely on fallback access

**Notes:**

---

### Task 5.6: Remove `__setattr__` Delegation (Stage 3) [Medium]

**File:** `game/ai/interfaces/controllable.py`
**Tests:** `pytest tests/ --testmon`

**Prerequisite:** Task 5.5 complete and tests passing

- [ ] Simplify `__setattr__` to standard behavior (lines 199-214):
  ```python
  # Remove this complex delegation:
  def __setattr__(self, name: str, value: Any) -> None:
      if name == '_ship':
          object.__setattr__(self, name, value)
      else:
          setattr(self._ship, name, value)

  # The class will use default __setattr__ behavior after removal
  ```

- [ ] Run tests: `pytest tests/ --testmon`
- [ ] Run full AI tests: `pytest tests/unit/ai/ -v`
- [ ] If tests fail, either:
  - Add proper setter methods to IControllable
  - Or update tests to use interface methods

**Notes:**

---

### Task 5.7: Update Mock Patches [Simple]

**File:** `tests/repro_issues/test_bug_13_clear_removes_hull.py`

Some tests may patch re-export paths that no longer exist after earlier phases.

- [ ] Search for patches that reference removed re-exports:
  ```bash
  grep -r "patch.*game.simulation.entities.ship\." --include="*.py" tests/
  grep -r "patch.*game.simulation.components.component\." --include="*.py" tests/
  grep -r "patch.*game.ai.controller\." --include="*.py" tests/
  ```

- [ ] Update any patch paths that reference re-exports to use canonical locations

**Notes:**

---

### Task 5.8: Document Final Decisions [Simple]

- [ ] Update `decisions.md` with all wrapper evaluation outcomes
- [ ] Update `design.md` if any architectural patterns changed
- [ ] Add comment to ShipControllableAdapter explaining why backward compat was removed

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] All evaluation decisions documented in decisions.md
- [ ] `pytest tests/ --testmon` passes
- [ ] Full test suite passes: `pytest tests/`
- [ ] `pytest simulation_tests/` passes
- [ ] No circular import errors: `python -c "import game"`
- [ ] Application launches: `python -m game`
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to indicate project complete
